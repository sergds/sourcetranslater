import tarfile
import os
import shutil
import zlib
import argparse

ap = argparse.ArgumentParser(description="Build an UNInstaller for your mod (requires pyinstaller in PATH). The main installer settings are defined in uninstaller.json. Make sure to change it for your target game!", add_help=True)
ap.add_argument("--musfile", type=str, help="Optionally add music to your installer like in old good days! (ogg format only!)", required=False)
args = ap.parse_args()

wantmus = False

if args.musfile:
    print("Adding music file: " + args.musfile)
    wantmus = True
    if args.musfile.split(".")[1] != "ogg":
        print("Music must be in ogg(vorbis) format! Discarding it!")
        wantmus = False

if wantmus:
    shutil.copy(args.musfile, "unimusic.ogg")

t = tarfile.open("data.uni" , "w")

t.add("../output", "output")
t.close()

fb = zlib.compress(open("data.uni", "rb").read(), 9)
f = open("data.uni" , "wb")
f.write(fb)

if wantmus:
    os.system('pyinstaller -F -w -i srctr.png --add-data "data.uni;uni" --add-data "uninstaller.json;uni" --add-data "captioncompiler.exe;uni" --add-data "unimusic.ogg;uni" UNInstaller.py')
    os.remove("unimusic.ogg")
else:
    os.system('pyinstaller -F -w -i srctr.png --add-data "data.uni;uni" --add-data "uninstaller.json;uni" --add-data "captioncompiler.exe;uni" UNInstaller.py')
#shutil.copy("dist/UNInstaller.exe", "installer_build")