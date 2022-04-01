import shutil
import json
import sys
from shaderverse import bl_info

sys.dont_write_bytecode = True

if __name__ == "__main__":
    # plugin_version="".join(str(bl_info["version"]))
    plugin_version = ".".join([str(version_int) for version_int in bl_info["version"]])
    output_filename = F"shaderverse-{plugin_version}"

    # build
    shutil.copytree("shaderverse", "dist/shaderverse", symlinks=True,
                        ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))

    shutil.make_archive(output_filename, 'zip', "dist")

    # cleanup
    try:
        shutil.rmtree("dist")
    except:
        print("No dist directory to delete")
    

    print(f"Built {output_filename}.zip")


