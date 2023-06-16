from ..model import Binary, BinaryLocations

ffmpeg = Binary(
        binary_name="ffmpeg", 
        urls=BinaryLocations(
            windows="https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", 
            macosx64="https://evermeet.cx/pub/ffmpeg/ffmpeg-6.0.zip",
            macossilicon="https://www.osxexperts.net/ffmpeg6arm.zip", 
            linux="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        ),
        files = BinaryLocations(
            windows="ffmpeg.exe",
            macosx64="ffmpeg",
            macossilicon="ffmpeg",
            linux="ffmpeg"
        )
        )

binary_list: list[Binary] = [
    ffmpeg
]
