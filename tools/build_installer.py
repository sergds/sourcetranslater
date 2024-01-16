import tarfile
import os
import shutil
import zlib

if os.path.exists("installer_build"):
    shutil.rmtree("installer_build")

os.mkdir("installer_build")

t = tarfile.open("data.uni" , "w")

t.add("../output", "output")
t.close()

fb = zlib.compress(open("data.uni", "rb").read(), 9)
f = open("data.uni" , "wb")
f.write(fb)

os.system('pyinstaller -F -i srctr.png --add-data "data.uni;uni" --add-data "uninstaller.json;uni" --add-data "captioncompiler.exe;uni" UNInstaller.py')
#shutil.copy("dist/UNInstaller.exe", "installer_build")