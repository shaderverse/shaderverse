#!/usr/bin/env python3.7
import os.path
from os import chdir
import sys
import importlib
import tempfile
from shutil import rmtree
import zipfile

usdLibLoaded = True
kConvertErrorReturnValue = 2


if sys.version_info.major != 3:
    print('  \033[93mWarning: It is recommended to use Python 3. Current version is ' + str(sys.version_info.major) + '.\033[0m')

# try:
from pxr import *
from . import usdUtils
# except ImportError as e:
#     print(f'  \033[91mError: failed to import pxr module. Please add path to USD Python bindings to your {e}PYTHONPATH\033[0m')
#     usdLibLoaded = False

__all__ = ['convert']


class USDParameters:
    version = 0.66
    materialsPath = '/Materials'

    def __init__(self, usdStage, verbose, url, creator, copyright, assetPath):
        self.usdStage = usdStage
        self.verbose = verbose
        self.url = url
        self.creator = creator
        self.copyright = copyright
        self.usdMaterials = {} # store materials by path
        self.usdMaterialsByName = {} # store materials by name
        self.defaultMaterial = None
        self.assetName = ''
        self.asset = usdUtils.Asset(assetPath, usdStage)


# parameters from command line
class ParserOut:
    def __init__(self):
        self.inFilePath = ''
        self.outFilePath = ''
        self.argumentFile = ''
        self.materials = []
        self.verbose = False
        self.copyTextures = False
        self.iOS12 = False
        self.paths = None
        self.url = ''
        self.creator = ''
        self.copyright = ''
        self.metersPerUnit = 0 # set by user
        self.preferredIblVersion = -1
        self.loop = False
        self.noloop = False
        self.useObjMtl = False
        material = usdUtils.Material('')
        self.materials.append(material)


# in/out parameters for converters
class OpenParameters:
    def __init__(self):
        self.copyTextures = False
        self.searchPaths = None
        self.verbose = False
        self.metersPerUnit = 0 # set by converters


class Parser:
    def __init__(self):
        self.out = ParserOut()
        self.arguments = []
        self.argumentIndex = 0
        self.texCoordSet = 'st'
        self.wrapS = usdUtils.WrapMode.useMetadata
        self.wrapT = usdUtils.WrapMode.useMetadata


    def printConvertNameAndVersion(self):
        print('usdzconvert ' +  str(USDParameters.version))



    def printUsage(self):
        self.printConvertNameAndVersion()
        print('usage: usdzconvert inputFile [outputFile]\n\
                   [-h] [-version] [-f file] [-v]\n\
                   [-path path[+path2[...]]]\n\
                   [-url url]\n\
                   [-copyright copyright]\n\
                   [-copytextures]\n\
                   [-metersPerUnit value]\n\
                   [-useObjMtl]\n\
                   [-preferredIblVersion value]\n\
                   [-loop]\n\
                   [-no-loop]\n\
                   [-iOS12]\n\
                   [-m materialName]\n\
                   [-texCoordSet name]\n\
                   [-wrapS mode]\n\
                   [-wrapT mode]\n\
                   [-diffuseColor           r,g,b]\n\
                   [-diffuseColor           <file> fr,fg,fb]\n\
                   [-normal                 x,y,z]\n\
                   [-normal                 <file> fx,fy,fz]\n\
                   [-emissiveColor          r,g,b]\n\
                   [-emissiveColor          <file> fr,fb,fg]\n\
                   [-metallic               c]\n\
                   [-metallic               ch <file> fc]\n\
                   [-roughness              c]\n\
                   [-roughness              ch <file> fc]\n\
                   [-occlusion              c]\n\
                   [-occlusion              ch <file> fc]\n\
                   [-opacity                c]\n\
                   [-opacity                ch <file> fc]\n\
                   [-clearcoat              c]\n\
                   [-clearcoat              ch <file> fc]\n\
                   [-clearcoatRoughness     c]\n\
                   [-clearcoatRoughness     ch <file> fc]\n')


    def printHelpAndExit(self):
        self.printUsage()
        with open(os.path.join(sys.path[0], 'help.txt'), 'r') as file:
            print (file.read())
            file.close()
        raise usdUtils.ConvertExit()


    def printVersionAndExit(self):
        print(USDParameters.version)
        raise usdUtils.ConvertExit()


    def printErrorUsageAndExit(self, message):
        self.printConvertNameAndVersion()
        usdUtils.printError(message)
        print('For more information, run "usdzconvert -h"')
        raise usdUtils.ConvertError()


    def loadArgumentsFromFile(self, filename):
        self.out.argumentFile = ''
        if os.path.isfile(filename):
            self.out.argumentFile = filename
        elif self.out.inFilePath:
            filename = os.path.dirname(self.out.inFilePath) + '/' + filename
            if os.path.isfile(filename):
                self.out.argumentFile = filename
        if self.out.argumentFile == '':
            self.printErrorUsageAndExit("failed to load argument file:" + filename)

        with open(self.out.argumentFile) as file:
            for line in file:
                line = line.strip()
                if '' == line:
                    continue

                line = line.replace('\t', ' ')
                line = line.replace(',', ' ')
                # arguments, like file names, can be with spaces in quotes
                quotes = line.split('"')
                if len(quotes) > 1:
                    for i in range(1, len(quotes), 2):
                        quotes[i] = quotes[i].replace(' ', '\t')
                    line = ''.join(quotes)

                arguments = line.split(' ')
                for argument in arguments:
                    argument = argument.replace('\t', ' ').strip()
                    if argument:
                        self.arguments.append(argument)


    def getParameters(self, count, argument):
        if self.argumentIndex + count >= len(self.arguments):
            self.printErrorUsageAndExit('argument ' + argument + ' needs more parameters')

        self.argumentIndex += count
        if count == 1:
            parameter = self.arguments[self.argumentIndex]
            if parameter[0] == '-' and not isFloat(parameter):
                self.printErrorUsageAndExit('unexpected parameter ' + parameter + ' for argument ' + argument)
            return self.arguments[self.argumentIndex]
        else:
            parameters = self.arguments[(self.argumentIndex - count + 1):(self.argumentIndex + 1)]
            for parameter in parameters:
                if parameter[0] == '-' and not isFloat(parameter):
                    self.printErrorUsageAndExit('unexpected parameter ' + parameter + ' for argument ' + argument)
            return parameters


    def isNextArgumentsAreFloats(self, count):
        if self.argumentIndex + count >= len(self.arguments):
            return False
        for i in range(count):
            argument = self.arguments[self.argumentIndex + 1 + i]
            if not isFloat(argument):
                return False
        return True


    def processInputArgument(self, argument):
        Ok = 0
        Error = 1
        inputIdx = -1
        for i in range(len(usdUtils.Input.names)):
            inputName = usdUtils.Input.names[i]
            if '-' + inputName == argument:
                inputIdx = i
                break
        if inputIdx == -1:
            return Error

        defaultChannels = usdUtils.Input.channels[inputIdx]
        channelsCount = len(defaultChannels)
        inputName = usdUtils.Input.names[inputIdx]
        if self.isNextArgumentsAreFloats(channelsCount):
            # constant or RGB value for input
            self.out.materials[-1].inputs[inputName] = self.getParameters(channelsCount, argument)
            return Ok

        # texture file
        channels = ''
        filename = ''
        parameter = self.getParameters(1, argument)
        if 'r' == parameter or 'g' == parameter or 'b' == parameter or 'a' == parameter or 'rgb' == parameter:
            channels = parameter
            filename = self.getParameters(1, argument)
        else:
            filename = parameter

        if channelsCount != 1 and channels != '' or channels == 'rgb':
            usdUtils.printWarning('invalid channel ' + channels + ' for argument ' + argument)
            channels = ''


        fallback = None
        if self.isNextArgumentsAreFloats(channelsCount):
            fallback = self.getParameters(channelsCount, argument)

        if channels == '':
            index = usdUtils.Input.names.index(inputName)
            channels = usdUtils.Input.channels[index]

        self.out.materials[-1].inputs[inputName] = usdUtils.Map(channels, filename, fallback, self.texCoordSet, self.wrapS, self.wrapT)
        return Ok


    def processPath(self, pathLine):
        paths = pathLine.split('+')
        outPath = []
        for path in paths:
            if path:
                if os.path.isdir(path):
                    outPath.append(path)
                else:
                    usdUtils.printWarning("Folder '" + path + "' does not exist. Ignored.")
        return outPath


    def parse(self, arguments):
        self.arguments = []
        for arg in arguments:
            if arg.find(',') != -1:
                newargs = filter(None, arg.replace(',',' ').split(' '))
                for newarg in newargs:
                    self.arguments.append(newarg)
            else:
                self.arguments.append(arg)
        
        if len(arguments) == 0:
            self.printUsage()
            print('For more information, run "usdzconvert -h"')
            raise usdUtils.ConvertExit()

        while self.argumentIndex < len(self.arguments):
            argument = self.arguments[self.argumentIndex]
            if not argument:
                continue
            if '-' == argument[0]:
                # parse optional arguments
                if '-v' == argument:
                    self.out.verbose = True
                elif '-copytextures' == argument:
                    self.out.copyTextures = True
                elif '-iOS12' == argument or '-ios12' == argument:
                    self.out.iOS12 = True
                elif '-path' == argument:
                    self.out.paths = self.processPath(self.getParameters(1, argument))
                elif '-copyright' == argument:
                    self.out.copyright = self.getParameters(1, argument)
                elif '-url' == argument:
                    self.out.url = self.getParameters(1, argument)
                elif '-creator' == argument:
                    self.out.creator = self.getParameters(1, argument)
                elif '-metersPerUnit' == argument:
                    metersPerUnit = self.getParameters(1, argument)
                    if not isFloat(metersPerUnit) or float(metersPerUnit) <= 0:
                        self.printErrorUsageAndExit('expected positive float value for argument ' + argument)
                    self.out.metersPerUnit = float(metersPerUnit)
                elif '-preferredIblVersion' == argument or '--preferredIblVersion' == argument or '--preferrediblversion' == argument:
                    preferredIblVersion = self.getParameters(1, argument)
                    if not isFloat(preferredIblVersion) or float(preferredIblVersion) < 0 or 2 < float(preferredIblVersion):
                        self.printErrorUsageAndExit('expected positive integer value [0, 1, 2] for argument ' + argument)
                    self.out.preferredIblVersion = int(float(preferredIblVersion))
                elif '-m' == argument:
                    name = self.getParameters(1, argument)
                    material = usdUtils.Material(name)
                    self.out.materials.append(material)
                    self.texCoordSet = 'st' # drop to default
                elif '-texCoordSet' == argument:
                    self.texCoordSet = self.getParameters(1, argument)
                elif '-wraps' == argument.lower():
                    self.wrapS = self.getParameters(1, argument)
                    if not usdUtils.isWrapModeCorrect(self.wrapS):
                        self.printErrorUsageAndExit('wrap mode \'' + self.wrapS + '\' is incorrect for ' + argument)
                elif '-wrapt' == argument.lower():
                    self.wrapT = self.getParameters(1, argument)
                    if not usdUtils.isWrapModeCorrect(self.wrapT):
                        self.printErrorUsageAndExit('wrap mode \'' + self.wrapT + '\' is incorrect for ' + argument)
                elif '-loop' == argument or '--loop' == argument:
                    self.out.loop = True
                elif '-no-loop' == argument or '--no-loop' == argument:
                    self.out.noloop = True
                elif '-useObjMtl' == argument:
                    self.out.useObjMtl = True
                elif '-h' == argument or '--help' == argument:
                    self.printHelpAndExit()
                elif '-version' == argument or '--version' == argument:
                    self.printVersionAndExit()
                elif '-f' == argument:
                    self.loadArgumentsFromFile(self.getParameters(1, argument))
                else:
                    errorValue = self.processInputArgument(argument)
                    if errorValue:
                        self.printErrorUsageAndExit('unknown argument ' + argument)
            else:
                # parse input/output filenames
                if self.out.inFilePath == '':
                    self.out.inFilePath = argument
                elif self.out.outFilePath == '':
                    self.out.outFilePath = argument
                else:
                    print('Input file: ' + self.out.inFilePath)
                    print('Output file:' + self.out.outFilePath)
                    self.printErrorUsageAndExit('unknown argument ' + argument)

            self.argumentIndex += 1

        if self.out.inFilePath == '':
            self.printErrorUsageAndExit('too few arguments')

        if self.out.loop and self.out.noloop:
            self.printErrorUsageAndExit("can't use -loop and -no-loop flags together")

        return self.out


def isFloat(value):
    try:
        val = float(value)
        return True
    except ValueError:
        return False


def createMaterial(params, materialName):
    matPath = params.materialsPath + '/' + materialName

    if params.verbose:
        print('  creating material at path: ' + matPath)
    if not Sdf.Path.IsValidIdentifier(materialName):
        usdUtils.printError("failed to create material by specified path.")
        raise usdUtils.ConvertError()

    surfaceShader = UsdShade.Shader.Define(params.usdStage, matPath + '/Shader')
    surfaceShader.CreateIdAttr('UsdPreviewSurface')
    surfaceOutput = surfaceShader.CreateOutput('surface', Sdf.ValueTypeNames.Token)
    usdMaterial = UsdShade.Material.Define(params.usdStage, matPath)
    usdMaterial.CreateOutput('surface', Sdf.ValueTypeNames.Token).ConnectToSource(surfaceOutput)

    params.usdMaterials[matPath] = usdMaterial
    params.usdMaterialsByName[materialName] = usdMaterial
    return usdMaterial


def getAllUsdMaterials(params, usdParentPrim):
    for usdPrim in usdParentPrim.GetChildren():
        if usdPrim.IsA(UsdGeom.Mesh) or usdPrim.IsA(UsdGeom.Subset):
            bindAPI = UsdShade.MaterialBindingAPI(usdPrim)
            if bindAPI != None:
                usdShadeMaterial = None
                directBinding = bindAPI.GetDirectBinding()
                matPath = str(directBinding.GetMaterialPath())

                if matPath != '':
                    if params.usdStage.GetObjectAtPath(matPath).IsValid():
                        usdShadeMaterial = directBinding.GetMaterial()
                    elif params.verbose:
                        usdUtils.printWarning("Mesh has material '" + matPath + "' which is not exist.")

                if usdShadeMaterial != None and matPath not in params.usdMaterials:
                    params.usdMaterials[matPath] = usdShadeMaterial
                    materialNameSplitted = matPath.split('/')
                    materialName = materialNameSplitted[len(materialNameSplitted) - 1]
                    params.usdMaterialsByName[materialName] = usdShadeMaterial

        getAllUsdMaterials(params, usdPrim)


def addDefaultMaterialToGeometries(params, usdParentPrim):
    for usdPrim in usdParentPrim.GetChildren():
        if usdPrim.IsA(UsdGeom.Mesh) or usdPrim.IsA(UsdGeom.Subset):
            bindAPI = UsdShade.MaterialBindingAPI(usdPrim)
            if bindAPI != None:
                usdShadeMaterial = None
                directBinding = bindAPI.GetDirectBinding()
                matPath = str(directBinding.GetMaterialPath())

                if matPath != '':
                    usdShadeMaterial = directBinding.GetMaterial()

                if usdShadeMaterial == None:
                    if params.defaultMaterial == None:
                        params.defaultMaterial = createMaterial(params, 'defaultMaterial')
                    matPath = params.materialsPath + '/defaultMaterial'
                    usdShadeMaterial = params.defaultMaterial
                    bindAPI.Bind(usdShadeMaterial)

                if matPath not in params.usdMaterials:
                    params.usdMaterials[matPath] = usdShadeMaterial
                    materialNameSplitted = matPath.split('/')
                    materialName = materialNameSplitted[len(materialNameSplitted) - 1]
                    params.usdMaterialsByName[materialName] = usdShadeMaterial

        addDefaultMaterialToGeometries(params, usdPrim)


def findUsdMaterialRecursively(params, usdParentPrim, name, byPath):
    for usdPrim in usdParentPrim.GetChildren():
        if usdPrim.IsA(UsdShade.Material):
            path = usdPrim.GetPath()
            if byPath:
                if path == name:
                    return UsdShade.Material(usdPrim)
            else:
                matName = os.path.basename(str(path))
                if matName == name:
                    return UsdShade.Material(usdPrim)
        usdMaterial = findUsdMaterialRecursively(params, usdPrim, name, byPath)
        if usdMaterial is not None:
            return usdMaterial
    return None


def findUsdMaterial(params, name):
    if not name or len(name) < 1:
        return None

    # first try to find by material path
    if name in params.usdMaterials:
        return params.usdMaterials[name]

    # try to find by material name 
    materialName = usdUtils.makeValidIdentifier(name)
    if materialName in params.usdMaterialsByName:
        return params.usdMaterialsByName[materialName]

    # try other options
    testMaterialName = '/Materials/' + materialName
    if testMaterialName in params.usdMaterials:
        return params.usdMaterials[testMaterialName]

    testMaterialName = '/' + materialName
    if testMaterialName in params.usdMaterials:
        return params.usdMaterials[testMaterialName]

    byPath = '/' == name[0]
    return findUsdMaterialRecursively(params, params.usdStage.GetPseudoRoot(), name, byPath)


def copyTexturesFromStageToFolder(params, srcPath, folder):
    copiedFiles = {}
    srcFolder = os.path.dirname(srcPath)
    for path, usdMaterial in params.usdMaterials.items():
        for childShader in usdMaterial.GetPrim().GetChildren():
            idAttribute = childShader.GetAttribute('info:id')
            if idAttribute is None:
                continue
            id = idAttribute.Get()
            if id != 'UsdUVTexture':
                continue
            fileAttribute = childShader.GetAttribute('inputs:file')
            if fileAttribute is None or fileAttribute.Get() is None:
                continue
            filename = fileAttribute.Get().path
            if not filename:
                continue
            if filename in copiedFiles:
                continue
            if srcFolder and filename[0] != '/':
                filePath = srcFolder + '/' + filename
            else:
                filePath = filename
            usdUtils.copy(filePath, folder + '/' + filename, params.verbose)
            copiedFiles[filename] = filename


def copyMaterialTextures(params, material, srcPath, dstPath, folder):
    srcFolder = os.path.dirname(srcPath)
    dstFolder = os.path.dirname(dstPath)
    for inputName, input in material.inputs.items():
        if not isinstance(input, usdUtils.Map):
            continue
        if not input.file:
            continue

        if srcFolder:
            if os.path.isfile(srcFolder + '/' + input.file):
                usdUtils.copy(srcFolder + '/' + input.file, folder + '/' + input.file, params.verbose)
                continue

        if dstFolder and dstFolder != srcFolder:
            if os.path.isfile(dstFolder + '/' + input.file):
                usdUtils.copy(dstFolder + '/' + input.file, folder + '/' + input.file, params.verbose)
                continue

        if os.path.isfile(input.file):
            if srcFolder and len(srcFolder) < len(input.file) and srcFolder + '/' == input.file[0:(len(srcFolder)+1)]:
                input.file = input.file[(len(srcFolder)+1):]
                usdUtils.copy(srcFolder + '/' + input.file, folder + '/' + input.file, params.verbose)
                continue

            if dstFolder and dstFolder != srcFolder and len(dstFolder) < len(input.file) and dstFolder + '/' == input.file[0:(len(dstFolder)+1)]:
                input.file = input.file[(len(dstFolder)+1):]
                usdUtils.copy(dstFolder + '/' + input.file, folder + '/' + input.file, params.verbose)
                continue

            basename = 'textures/' + os.path.basename(input.file)
            usdUtils.copy(input.file, folder + '/' + basename, params.verbose)
            input.file = basename


def createStageMetadata(params):
    if params.creator != '':
        params.usdStage.SetMetadataByDictKey("customLayerData", "creator", str(params.creator))
    else:
        params.usdStage.SetMetadataByDictKey("customLayerData", "creator", "usdzconvert preview " + str(params.version))
    if params.url != '':
        params.usdStage.SetMetadataByDictKey("customLayerData", "url", str(params.url))
    if params.copyright != '':
        params.usdStage.SetMetadataByDictKey("customLayerData", "copyright", str(params.copyright))


def unzip(filePath, outputDir):
    firstFile = ''
    with zipfile.ZipFile(filePath) as zf:
        zf.extractall(outputDir)
        namelist = zf.namelist()
        if len(namelist) > 0:
            firstFile = namelist[0]
    return firstFile


def process(argumentList):
    parser = Parser()
    parserOut = parser.parse(argumentList)

    srcPath = ''
    if os.path.isfile(parserOut.inFilePath):
        srcPath = parserOut.inFilePath
    elif os.path.dirname(parserOut.inFilePath) == '' and parserOut.argumentFile:
        # try to find input file in argument file folder which is specified by -f in command line
        argumentFileDir = os.path.dirname(parserOut.argumentFile)
        if argumentFileDir:
            os.chdir(argumentFileDir)
            if os.path.isfile(parserOut.inFilePath):
                srcPath = parserOut.inFilePath

    if srcPath == '':
        parser.printErrorUsageAndExit('input file ' + parserOut.inFilePath + ' does not exist.')

    fileAndExt = os.path.splitext(srcPath)
    if len(fileAndExt) != 2:
        parser.printErrorUsageAndExit('input file ' + parserOut.inFilePath + ' has unsupported file extension.')

    print('Input file: ' +  srcPath)
    srcExt = fileAndExt[1].lower()

    dstIsUsdz = False
    dstPath = parserOut.outFilePath
    dstExt = ''
    if dstPath == '':
        # default destination file is .usdz file in the same folder as source file
        dstExt = '.usdz'
        dstPath = fileAndExt[0] + dstExt
        dstIsUsdz = True

    dstFileAndExt = os.path.splitext(dstPath)
    if len(dstFileAndExt) != 2:
        parser.printErrorUsageAndExit('output file ' + dstPath + ' has unsupported file extension.')

    if not dstIsUsdz:
        dstExt = dstFileAndExt[1].lower()
        if dstExt == '.usdz':
            dstIsUsdz = True
        elif dstExt != '.usd' and dstExt != '.usdc' and dstExt != '.usda':
            parser.printErrorUsageAndExit('output file ' + dstPath + ' should have .usdz, .usdc, .usda or .usd extension.')

    tmpFolder = tempfile.mkdtemp('usdzconvert')

    legacyModifier = None
    if parserOut.iOS12:
        iOS12Compatible_module = importlib.import_module("iOS12LegacyModifier")
        legacyModifier = iOS12Compatible_module.createLegacyModifier()
        print('Converting in iOS12 compatiblity mode.')

    tmpPath = dstFileAndExt[0] + '.usdc' if dstIsUsdz else dstPath
    tmpBasename = os.path.basename(tmpPath)
    tmpPath = tmpFolder + '/' + tmpBasename

    if parserOut.verbose and parserOut.copyTextures and dstIsUsdz:
        usdUtils.printWarning('argument -copytextures works for .usda and .usdc output files only.')

    openParameters = OpenParameters()
    openParameters.copyTextures = parserOut.copyTextures and not dstIsUsdz
    openParameters.searchPaths = parserOut.paths
    openParameters.verbose = parserOut.verbose

    srcIsUsd = False
    srcIsUsdz = False
    usdStage = None
    if '.obj' == srcExt:
        global usdStageWithObj_module
        usdStageWithObj_module = importlib.import_module("usdStageWithObj")
        # this line can be updated with Pixar's backend loader
        usdStage = usdStageWithObj_module.usdStageWithObj(srcPath, tmpPath, parserOut.useObjMtl, openParameters)
    elif '.gltf' == srcExt or '.glb' == srcExt:
        from . import usdStageWithGlTF

        usdStage = usdStageWithGlTF.usdStageWithGlTF(srcPath, tmpPath, legacyModifier, openParameters)
    elif '.fbx' == srcExt:
        global usdStageWithFbx_module
        usdStageWithFbx_module = importlib.import_module("usdStageWithFbx")
        usdStage = usdStageWithFbx_module.usdStageWithFbx(srcPath, tmpPath, legacyModifier, openParameters)
    elif '.usd' == srcExt or '.usda' == srcExt or '.usdc' == srcExt:
        usdStage = Usd.Stage.Open(srcPath)
        srcIsUsd = True
        openParameters.metersPerUnit = usdStage.GetMetadata("metersPerUnit")
    elif '.usdz' == srcExt:
        tmpUSDC = unzip(srcPath, tmpFolder)
        if tmpUSDC == '':
            parser.printErrorUsageAndExit("can't open input usdz file " + parserOut.inFilePath)
        usdStage = Usd.Stage.Open(tmpFolder + '/' + tmpUSDC)
        srcIsUsdz = True
    elif '.abc' == srcExt:
        usdStage = Usd.Stage.Open(srcPath)
        # To update Alembic USD Stage, first save it to temporary .usdc and reload it
        tmpUSDC = tmpPath + '.usdc'
        usdStage.GetRootLayer().Export(tmpUSDC)
        if parserOut.verbose:
            print('Temporary USDC file: ' + tmpUSDC)
        usdStage = Usd.Stage.Open(tmpUSDC)
    else:
        parser.printErrorUsageAndExit('input file ' + parserOut.inFilePath + ' has unsupported file extension.')

    if usdStage == None:
        usdUtils.printError("failed to create USD stage.")
        raise usdUtils.ConvertError()

    params = USDParameters(usdStage, parserOut.verbose, parserOut.url, parserOut.creator, parserOut.copyright, tmpPath)
    createStageMetadata(params)

    if parserOut.loop and (srcIsUsd or srcIsUsdz):
        usdStage.SetMetadataByDictKey("customLayerData", "loopStartToEndTimeCode", True)

    if parserOut.noloop:
        usdStage.SetMetadataByDictKey("customLayerData", "loopStartToEndTimeCode", False)

    if parserOut.preferredIblVersion != -1:
        appleDict = usdStage.GetMetadataByDictKey("customLayerData", "Apple")
        if appleDict is None or type(appleDict) is not dict:
            appleDict = {}
        appleDict["preferredIblVersion"] = parserOut.preferredIblVersion
        usdStage.SetMetadataByDictKey("customLayerData", "Apple", appleDict)

    rootPrim = None
    if usdStage.HasDefaultPrim():
        rootPrim = usdStage.GetDefaultPrim()

    if rootPrim != None:
        params.assetName = rootPrim.GetName()
        params.materialsPath = '/' + params.assetName + '/Materials'

    metersPerUnit = openParameters.metersPerUnit # set by converter
    if parserOut.metersPerUnit != 0:
        metersPerUnit = parserOut.metersPerUnit  # set by user
    if metersPerUnit == 0:
        metersPerUnit = 0.01
    if legacyModifier is None:
        usdStage.SetMetadata("metersPerUnit", metersPerUnit)
    else:
        if rootPrim != None:
            usdMetersPerUnit = 0.01
            scale = metersPerUnit / usdMetersPerUnit
            if scale != 1:
                rootXform = UsdGeom.Xform(rootPrim)
                rootXform.AddScaleOp(UsdGeom.XformOp.PrecisionFloat, "metersPerUnit").Set(Gf.Vec3f(scale, scale, scale))

    getAllUsdMaterials(params, params.usdStage.GetPseudoRoot())

    if srcIsUsd and dstIsUsdz:
        # copy textures to temporary folder while creating usdz
        copyTexturesFromStageToFolder(params, srcPath, tmpFolder)

    if srcIsUsd:
        if not (len(parserOut.materials) == 1 and parserOut.materials[0].isEmpty()):
            usdUtils.printWarning('Material arguments are ignored for .usda/usdc input files.')
    else:
        # update usd materials with command line material arguments
        for material in parserOut.materials:

            if legacyModifier is not None:
                legacyModifier.opacityAndDiffuseOneTexture(material)

            if material.name == '':
                # if materials are not specified, then apply default material to all materials
                if not material.isEmpty():
                    addDefaultMaterialToGeometries(params, params.usdStage.GetPseudoRoot())

                    copyMaterialTextures(params, material, srcPath, dstPath, tmpFolder)
                    if legacyModifier is not None:
                        legacyModifier.makeORMTextures(material, tmpFolder, parserOut.verbose)

                    for path, usdMaterial in params.usdMaterials.items():
                        surfaceShader = material.getUsdSurfaceShader(usdMaterial, params.usdStage)
                        material.updateUsdMaterial(usdMaterial, surfaceShader, params.usdStage)
                continue

            usdMaterial = findUsdMaterial(params, material.path if material.path else material.name)

            if usdMaterial is not None:
                # if material does exist remove it
                matPath = str(usdMaterial.GetPrim().GetPath())
                if matPath in params.usdMaterials:
                    del params.usdMaterials[matPath]
                usdStage.RemovePrim(matPath)
                usdMaterial = None

            copyMaterialTextures(params, material, srcPath, dstPath, tmpFolder)
            if legacyModifier is not None:
                legacyModifier.makeORMTextures(material, tmpFolder, parserOut.verbose)

            usdMaterial = material.makeUsdMaterial(params.asset)
            if usdMaterial is None:
                continue

            surfaceShader = material.getUsdSurfaceShader(usdMaterial, params.usdStage)
            material.updateUsdMaterial(usdMaterial, surfaceShader, params.usdStage)
            params.usdMaterials[str(usdMaterial.GetPrim().GetPath())] = usdMaterial

    usdStage.GetRootLayer().Export(tmpPath)

    # prepare destination folder
    dstFolder = os.path.dirname(dstPath)
    if dstFolder != '' and not os.path.isdir(dstFolder):
        if parserOut.verbose:
            print('Creating folder: ' + dstFolder)
        os.makedirs(dstFolder)

    if dstIsUsdz:
        # construct .usdz archive from the .usdc file
        UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(tmpPath), dstPath)
    else:
        usdUtils.copy(tmpPath, dstPath)

    # copy textures with usda and usdc
    if openParameters.copyTextures:
        copyTexturesFromStageToFolder(params, tmpPath, dstFolder)

    rmtree(tmpFolder, ignore_errors=True)
    print('Output file: ' + dstPath)

    arkitCheckerReturn = 0


    return arkitCheckerReturn

def tryProcess(argumentList):
    try:
        ret = process(argumentList)
    except usdUtils.ConvertError:
        return kConvertErrorReturnValue
    except usdUtils.ConvertExit:
        return 0
    except:
        raise
    return ret


def convert(fileList, optionDictionary):
    supportedFormats = ['.obj', '.gltf', '.glb', '.fbx', '.usd', '.usda', '.usdc', '.usdz', '.abc']
    argumentList = []

    for file in fileList:
        fileAndExt = os.path.splitext(file)
        if len(fileAndExt) == 2:
            ext = fileAndExt[1].lower()
            if ext in supportedFormats:
                # source file to convert
                argumentList.append(file)

            name = fileAndExt[0]

            for inputName in usdUtils.Input.names:
                if inputName in optionDictionary:
                    option = optionDictionary[inputName]

                    channel = ''

                    optionAndChannel = option.split(':')
                    if len(optionAndChannel) == 2:
                        option = optionAndChannel[0]
                        channel = optionAndChannel[1]

                    if len(name) > len(option) and option==name[-len(option):]:
                        argumentList.append('-' + inputName)
                        if channel != '':
                            argumentList.append(channel)
                        argumentList.append(file)

    return tryProcess(argumentList)


def main():
    return tryProcess(sys.argv[1:])


if __name__ == '__main__':
    if usdLibLoaded:
        errorValue = main()
    else:
        errorValue = kConvertErrorReturnValue

    sys.exit(errorValue)

