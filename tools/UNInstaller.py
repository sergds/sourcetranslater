# UNInstaller --- An UNIversal Installer
# for kringe team's source mods. Written because NSIS sucks and isn't flexible without nsi wizardry
# Should be compiled with build_installer.py
import pkgutil
import tarfile
import zlib
import tempfile
import PySimpleGUI as sg
import json
import os
import shutil
import sys
import atexit
import subprocess
import platform
import uni

# https://stackoverflow.com/questions/42004445/python-exe-not-deleting-itself
def execute(command, asyncexec=False):
    """
    if async=False Executes a shell command and waits until termination and

    returns process exit code
    if async=True Executes a shell command without waiting for its 
    termination and returns subprocess.Popen object
    On Windows, does not create a console window.
    """
    if asyncexec:
        call = subprocess.Popen
    else:
        call = subprocess.call
    if platform.system() == 'Windows':
        # the following CREATE_NO_WINDOW flag runs the process without 
        # a console window
        # it is ignored if the application is not a console application
        return call(command, creationflags=0x08000000)
    else:
        return call(command)


def cleanup(td):
    os.chdir(sys.argv[0].replace(os.path.basename(sys.argv[0]), "")) # What a beautiful piece of hack
    shutil.rmtree(td)

print(__name__)
print(sys.modules[__name__])

# Unpack everything
if not (os.path.exists(".uninstaller_srctr_installed") and os.path.exists("SRCTR_BACKUP")):
    td = tempfile.mkdtemp(prefix="uni")
    os.chdir(td)
    atexit.register(cleanup, td)
    dat = pkgutil.get_data('uni', "data.uni")
    uc = pkgutil.get_data("uni", "uninstaller.json")
    cc = pkgutil.get_data("uni", "captioncompiler.exe")
    f1 = open("data.uni", "wb")
    f2 = open("uninstaller.json", "wb")
    f3 = open("captioncompiler.exe", "wb")
    f1.write(dat)
    f2.write(uc)
    f3.write(cc)
    f1.close()
    f2.close()
    f3.close()
sg.theme('DarkGreen2')

mainlayout = [[sg.Titlebar("[UNInstaller] SourceTranslater Mod installer", bytes("iVBORw0KGgoAAAANSUhEUgAAAEAAAAA3CAYAAAC8TkynAAAACXBIWXMAAAVPAAAFTwE3eRCbAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAADK1JREFUaIHNm390VNW1xz/nziSZ/AKCSUgymYRfKQmw+FXUCi+Clh+11bpasfCk1AqtsUirda3Xii1VVPoWtUo1sqSttBRToVCrYosF8fGoUCWC9BkaE5AfITP5QRICSSaTmczc0z9uJrnzM3cms7red61Z99x9zj53n33O2Weffc4IKSWJRHFxcZbX6y0XQsxQVbVECDEZSBVCjA4uK6VMB5IT9OlMwDyQdgPdQANwRkr5v0KItx0OR2Mwk0iEAqxWq01K+XUhxDJgFqCMuNLEwwfsATY6HI56P3FECigoKLhZUZRHpZRL+f/Z6HBwCiFW2+32PRCnAqxW62zgeaA8wcIlDPPmzWP69OnU19fj8/k4evSoPltKKb/T1NT0y5gUkJeXl24ymX4KPAiYopUdn+aldJSXielexiarZJpVANyqoNurcNFp4tMeM7VdSbhVEXsLdViyZAklJSUBtClTpjBp0iTOnz/P4sWL2bp1K3v37qWlpcVfpB+40RxcWSTk5+dPM5lMe4Cp4fJNAhbkuLmzwEV5jptxKT5D9bpVwYnOZA62WHjdkUqHJzEzqaenh8zMTOrq6qirqwtXJEkI8X1DI6CgoOArQogqIC04L8Ms+Uaxk29PdJJrsNGR4JWCvzRbeOFsBnXdSTHxPvLII5SXl+N2u8nJyeGee+5h165dLF26lDfeeIM1a9boe9+PmmHVbbVaVwsh9hLUeEXAqmInH9zayo/KukbceACzkNxZ4OLQgjZenN0ZU51ZWVkcPnyYqqoqLBYLra2tWCwW1q1bR1dXV7jGA9hMTzzxRMRKrVbrfcB2gix8cbqPV264wqriXlJNifUjAARQNsrLymIXLX0KtV3Dj4bS0lKSkpJQVZXq6mpqamrIzc3lgQceYPXq1aSlpeF2u/H5ApUacQoUFhbeLqV8nSHnAoAl4/p4YfbVQaP278DuxjTW14zGE8FY3nbbbcyZM4dx48ZRUFCAoii0tbVRVlZGSkoKhw4dIicnh6NHj7Jz5049a2vYKWC1WkullLsJavzdhb38+rNXhm/8hBvh4Xfgrp+BGJmFB1hh6+X3N14hMyl8Z5nNZurr63nllVd4+eWXWbt2LfX19WzevJmFCxfS3t5OZmYmx48fD2a9EKKACRMmWIBdQLqevqrYyZZZVzEbMdIZ2VC2SHsmyNWed52bqhs6wk656upqVqxYQUNDAxs2bGDKlCksW7aM9957D5fLxeTJk9m2bRv19fXBrCdDmuPxeJ5Cc2cH8cX8PjZNv8bI+3JkmJvl4aU5nZiCBKmoqODSpUv09/ejKApHjhxhzZo1dHd3U1VVxYEDB6isrGTWrIBmIaU8HDDE8/PzpymK8pCeNj7Ny3Mzgj76tS0wOYoTmDqw75n5ZXjsRPgynY3w0leitzgMFo/r4+GSbp49kxlAr6yspLu7G1VV+eSTT5BSkpSUxIULF9i/fz8ejwen06lncaWmph4KMIJWq/UdYJH/3Swk+8vbmTaqP1CKB/fBjDtiFj4Alz+FDSXDlwsDn4TlH2TzfseINpKvOhyOlYMKsNlsN6iqGmAl1k7q4UdlXaGsKRlgirI0TV0C394N1a/CrnXhy0gVXNfilv6808znj+REXBkMYInD4Xhn0AaoqvqYPjfXovJwSXd4VncP9HZqv+wJcM9Wzdr7ae4erZzXPUQL/o2g8QAT0718c7xz+ILh0djU1PQuDDg4RUVFBcDt+hL3T+gh3WzAgt/yXbj+P+E/vhWvMHFj7aQeLHE4YlLK30kpVRhQgM/nW4lud5eZJFlVbFC7b28C1QcLHwRlwKamZWlPjytm4WJBTorK3YW9sbKpZrN5h//FPwVW6Et8Kc9FhpHeB82YffQajC2Cm+7VaBnZ2rMvjP1IMJbbYlOylPKvly5dOud/V2w221iC1v2vFsbYc/5RsOwZGJ0PtoHq2i/EVk8cmD3Gw/g0bywslfoXxefzLUS32Uk1Sa7P8sQmhf1jOPScNvRXvgTTb9PoDRF8gARjQY7baNFPm5ubD+oJiqIoc/WEuVkekpU43Nd9j8PlszDzTsjMhY4GaPxH7PXEgfnZxjpMSvmi3/j5oQBT9IQQp8co+l3wum4l7WmDzJzQcooZsidqvzHW+L4VhGmjDcncm5SUtDOYqEgpA9yxSRkxzach5E6GuzYPvRfPhcdPw+cfgmRdLGXml2HTOe331JmhFWMEsKV6hx21UsqdDQ0NncF0BcjWE/ItMUZ2FDPcsg5+fErr1eZa2HoHtJ7RVoOv/QJ+ehHufBoUBebdN8SbnAY3fj2274WBScA4S/QtuqqqW8OKj3aiMgjDy59lFNxcAU/Vw4pKzT2uPww/XwAf/xk2zYEDP9OmRmYOZBVCRi5M/4LGf3q/9lzwnYTEDNJNURXwPy0tLafDZShAakC7jHhWC9fCM82wcpvW633d8Np/wZZF0NOulXE74U8/hB+XwLu/gL/9SvMTFDN0t8FbG7Vy+WXRd5YGES00J6UM2/ugRXz60AU/+nwGeuPiCW34Oq/Ase1w8BmtUeFw1QF7vq+l792uPU/vh4vVmhOVO1kbSWf/Nvx3o8AVWe5Lzc3N+yJlKmiHiIPo8RpRQDU8vxR+UACv/SBy4/WYNB/ySrX0qde158m92nPOXeFXjBjQ440YqnpJShnRsivAFT2hqS/qgc8Qag9quz2jmL9aezqvwD//qqWrX9We5pRA4xgjvCq09oVVgEtV1e3ReBXgrJ5wrsfwYZFxpKTDZ+/W0h/uGlJc02loOKmlb64AEd+pUKPLTL8MO3J3NDc3Rx2eCnBGT/ingRh8zJi7HCwDi837vwvM879nT4Spi+OqPoLMqqIoW4bjVYCTesKJzuSRRFnCwz+8m2vh4oeBedW/HxoR5RVxVX+sPWxo7M3Gxsaz4TL0UHw+32FgcA3p8wmOX0nUpQ0gt0QzgBDa+6DZhI//rKVn3qH5CzFAAkfaLSF0IcQzRvjNLS0tl61Way0wzU/8kz2V8uwYDFw0zLtvyNHpatXOC4LROjALFbMWWXrrCcPVf9SZTIMzxHAfs9vt7xvh91u8PcBGP3F/SypP9l+LeBJjGIoJPqdzdb+5Y3ie8vth/ybwGduU7bGHHFgjhHjcoIRaHEBV1Z3opkGPV7CzIT0ik2FMXQpZNi3d1x05QNrbqXmOoAVUZtweuU4dLvcp/NGeGkw+YLfb3zUqohmgubn5otVqPQQMmuFfX8jg3vFO43uDcPCv/f19sL4Ieq9GLptXChs/0dLlFUPOUhRsPZcZ7LmqwPpYRBxceIUQ/63PaHMrPBd0+hIT0q8b6sn/2xe98QAtdXBh4Fhi6hLNeEbBmW4zOy6GDP/dDofjVCxiDirAbrcfBo7pM7dfzKDmWpx+wU3f0Dw8gONVxnj+/lvtKUTUMLtPwg9rxuANdH48JpPpJ7GKGex6fQ/tPh2guZgVJ7PojuxnR4Y/QuzsgNoDxniqd4FnIMw9fzUkhS5vAM+eyaQ6dKl+Th/tNYqAljkcjo+AbXpaQ6+Z750agy8WUzD+eiicqaWrd4HXYJC1r0sLsYMWTJn91ZAib7dYqPw0ZGqeURTlyRgkHERI1/b39z8KBFyrOthq4dGaMRjWgX5jY3T4+3HsN0PpmwM9w+NXkll3Kgs1UBCflPJbjY2NcZ3ChL0ik5eXN91kMlUTFCxZVuji2ZlXMYvE3wsaDkfbU1hzYmzIdl0IscFutz8db73R7gjdPXBNJmCU3JrbR+Xsq4xJ+vfdEXrDkcpD/wgxegxcgL49ONQdC6LeE7RarQ8CL4bQU328OLuTG8bGeIASI671K6yvGc2bTSHODsBRYKnD4Yj5cFCPYS9KDijhBYJGggCW23pZX9pFdkpiR4Mq4Y+ONJ6uHRX25qgQ4kOXy7Woo6NjxIePhm6KWq3W5cAOIGRdSjNJVhY5uX+ik4LUkV2W7JeCfQ7Nyp+NHJh50+PxrGpra4tweSE2GL4sXVhYOEtK+QfgM+HyFQHzrxu6K1xoUBm9PsHxjmQOtlrY15TK1f6IPocEnmxqatooE/gvj5hui+fk5GQmJydvBioY5v8BtjQfn8noZ3KGl+uSVUYlSQSSXp9Cj1dw3mnmvNNM7bWI4Sw9aoAHHA7H3w0LaxBx/V8gPz//ekVRngduSrRAQbgshNicl5dXeeLEiTgPLaNjRP8YsVqti4DHgFsSJhEghDgvpdyiKMr2eB0cw99KxHSy2WwlqqquApYBZXFWcwF4Swix2+FwfJDIeR4NCVGAHkVFRQVer/dWIcQMoBQoAcagnUGmAB0Dv3NAnZSyRghxxOFwXEqoIAbxL5ngx2WBxyVbAAAAAElFTkSuQmCC", "utf-8"))],
              [sg.Column([[sg.Text("Install a source translater mod for:", key='-SINSTALLDESC-', justification='center')]], element_justification="center", justification="center")],
              [sg.Column([[sg.Text("", key='-SMOD-', font="sans-serif 20")]], element_justification="center", justification="center")],
              [sg.Column([[sg.InputText("", key="-SINSTALLDIR-"), sg.FolderBrowse()]], element_justification="center", justification="center")],
              [sg.Column([[sg.Button("Install", key='-SINSTALLCONFIRM-', size=(10, 3))]], element_justification="center", justification="center")]]

progresslayout = [[sg.Titlebar("[UNInstaller] SourceTranslater Mod installer", bytes("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", "utf-8"))],
                  [sg.Column([[sg.Text("Installing...", key='-SINSTALLTEXT-', font="sans-serif 20", justification='center')]], element_justification="center", justification="center")],
                [sg.Column([[sg.ProgressBar(100, 'horizontal', key="-SINSTALLBAR-", size_px=(280,10))]], element_justification="center", justification="center")]]

window = sg.Window("SourceTranslater Mod installer", mainlayout, finalize=True)
progresswindow = sg.Window("SourceTranslater Mod installing", progresslayout, finalize=True)

progresswindow.hide()
uniconfig = json.load(open("uninstaller.json"))
window["-SMOD-"].update(uniconfig["guimodname"])
window["-SINSTALLDIR-"].update(uniconfig["default_installdir"])

global installing
installing = False
wantuninstalling = False
uninstalling = False
files_to_preserve = []
files_to_compile = set()
i = 0
stage = 0 # 0 - nop (pre-install); 1 - create backup list; 2 - perform backup; 3 - spill our files out into the game; 4 - captioncompile all our closecaption and subtitles files. 5 - nop (post-install).
uninstage = 0 # 0 - nop (pre-uninstall); 1 - apply backups; 2 - remove uninstaller and backups and quit; 3 - nop (post-uninstall)
errstr = "" # For errors

if os.path.exists(".uninstaller_srctr_installed") and os.path.exists("SRCTR_BACKUP"):
    wantuninstalling = True
    window["-SINSTALLDIR-"].Disabled = True
    window["-SINSTALLDESC-"].update("Do you want to DELETE a source translater mod for:")
    window["-SINSTALLCONFIRM-"].update("Uninstall")

def selfnuke():
    os.remove(sys.argv[0])

while True:
    event, values = window.read(timeout=10)
    event2, values2 = progresswindow.read(timeout=10)

    if uninstalling:
        if uninstage == 1:
            progresswindow['-SINSTALLTEXT-'].update("Restoring original files...")
            progresswindow['-SINSTALLBAR-'].update(50)
            shutil.copytree("SRCTR_BACKUP/", os.getcwd() ,dirs_exist_ok=True)
            uninstage = 2
        if uninstage == 2:
            progresswindow['-SINSTALLTEXT-'].update("Removing backups...")
            progresswindow['-SINSTALLBAR-'].update(50)
            shutil.rmtree("SRCTR_BACKUP")
            os.remove(".uninstaller_srctr_installed")
            os.remove("uninstaller.json")
            try:
                os.remove("uninstaller.exe")
            except Exception:
                print("1st try nuking self failed")
            atexit.register(selfnuke)
            uninstage = 3
        if uninstage == 3:
            progresswindow['-SINSTALLTEXT-'].update("Uninstalled! you still need to manually remove uninstall.exe in gamedir!")
            progresswindow['-SINSTALLBAR-'].update(100)

    if installing:
        if stage == 1: # Gather some info about mod we are about to install
            if not os.path.exists(window["-SINSTALLDIR-"].get()):
                stage = 6
                errstr = "installdir does not exist!"
                continue
            if not os.path.exists(os.path.join(window["-SINSTALLDIR-"].get(), uniconfig["basemodname"])) or not os.path.isdir(os.path.join(window["-SINSTALLDIR-"].get(), uniconfig["basemodname"])):
                stage = 6
                errstr = "not a Source game the mod was made for!"
                continue
            if not "bin" in os.listdir(window["-SINSTALLDIR-"].get()) and not "platform" in os.listdir(window["-SINSTALLDIR-"].get()):
                stage = 6
                errstr = "installdir is not a Source game!"
                continue
            open("data.tmp", "wb").write(bytearray(zlib.decompress(open("data.uni", "rb").read())))
            un = tarfile.open("data.tmp")
            un.extractall()
            un.close()
            os.remove("data.tmp")
            for dirpath, dirnames, filenames in os.walk("output"):
                for ff in filenames:
                    if "subtitles" in ff or "closecaption" in ff:
                        files_to_compile.add(os.path.join(dirpath.replace("output" + os.sep, ""), ff))
                        print(os.path.join(dirpath.replace("output" + os.sep, ""), ff))
                if uniconfig["basemodname"] in dirpath or "platform" in dirpath and dirnames != []:
                    for  d in dirnames:
                        files_to_preserve.append(os.path.join(dirpath.replace("output" + os.sep, ""), d))
                        print(os.path.join(dirpath.replace("output" + os.sep, ""), d))
                        progresswindow['-SINSTALLTEXT-'].update("Backing up files...")
                        progresswindow['-SINSTALLBAR-'].update(20 + i)
                        i += 1
            stage = 2
        if stage == 2: # backup
            progresswindow['-SINSTALLTEXT-'].update("Backing up files...")
            progresswindow['-SINSTALLBAR-'].update(40)
            if not os.path.exists(os.path.join(window["-SINSTALLDIR-"].get(), "SRCTR_BACKUP")):
                os.mkdir(os.path.join(window["-SINSTALLDIR-"].get(), "SRCTR_BACKUP"))
            else:
                shutil.rmtree(os.path.join(window["-SINSTALLDIR-"].get(), "SRCTR_BACKUP"))
                os.mkdir(os.path.join(window["-SINSTALLDIR-"].get(), "SRCTR_BACKUP"))
            for file in files_to_preserve:
                for comp in file.split(os.path.sep):
                    if file.split(os.path.sep).index(comp) == len(file.split(os.path.sep)) - 1:
                        continue
                    prev_comps = []
                    currdir = ""
                    if comp == "":
                        continue
                    if file.split(os.path.sep).index(comp) > 0:
                        for prevp in file.split(os.path.sep)[file.split(os.path.sep).index(comp)-1::-1][::-1]:
                            if prevp != "":
                                prev_comps.append(prevp)
                    currdir = os.path.join(os.path.normpath("/".join(prev_comps)))
                    if not os.path.exists(os.path.join(window["-SINSTALLDIR-"].get(), currdir, comp)):
                        os.mkdir(os.path.join(window["-SINSTALLDIR-"].get(), currdir, comp))
            for d in files_to_preserve:
                shutil.copytree(os.path.join(window["-SINSTALLDIR-"].get(), d), os.path.join(window["-SINSTALLDIR-"].get(), os.path.join("SRCTR_BACKUP", d)))
            stage = 3
        if stage == 3: # Install mod
            progresswindow['-SINSTALLTEXT-'].update("Copying files...")
            progresswindow['-SINSTALLBAR-'].update(50)
            shutil.copy(sys.argv[0], os.path.join(window["-SINSTALLDIR-"].get(), "uninstall.exe"))
            f = open(os.path.join(window["-SINSTALLDIR-"].get(), ".uninstaller_srctr_installed"), "wt")
            shutil.copy("uninstaller.json", os.path.join(window["-SINSTALLDIR-"].get(), "uninstaller.json"))
            f.write(uniconfig["basemodname"])
            f.close()
            shutil.copytree("output/", window["-SINSTALLDIR-"].get(), dirs_exist_ok=True)
            stage = 4
        if stage == 4: # captioncompiler stage
            cwd = os.getcwd()
            progresswindow['-SINSTALLTEXT-'].update("Compiling close captions...")
            progresswindow['-SINSTALLBAR-'].update(85)
            if not os.path.exists(os.path.join(window["-SINSTALLDIR-"].get(), "bin", "captioncompiler.exe")):
                shutil.copy("captioncompiler.exe", os.path.join(window["-SINSTALLDIR-"].get(), "bin", "captioncompiler.exe")) # use our copy if user don't have sdk installed (99% don't)
            for bdir in os.listdir("output"): # output already contains basedirs we need to recompile!
                print("cd " + bdir)
                os.chdir(os.path.join(window["-SINSTALLDIR-"].get(), bdir))
                for f in files_to_compile:
                    execute(f"..\\bin\\captioncompiler {os.path.basename(f)}")
            os.chdir(cwd)
            stage = 5
        if stage == 5:
            progresswindow['-SINSTALLTEXT-'].update("Done! To uninstall, use uninstall.exe in gamedir or verify game files with Steam. Now close this window.")
            progresswindow['-SINSTALLBAR-'].update(100)
        if stage == 6:
            progresswindow['-SINSTALLTEXT-'].update("Ouch, an ERROR!: " + errstr)
            progresswindow['-SINSTALLBAR-'].update(0)

    if event == sg.WIN_CLOSED:
        break
    if event2 == sg.WIN_CLOSED:
        break
    if event == "-SINSTALLCONFIRM-":
        if wantuninstalling:
            uninstalling = True
            uninstage = 1
        else:
            installing = True
        print(window["-SINSTALLDIR-"].get())
        progresswindow.un_hide()
        window.hide()
        stage = 1
window.close()
progresswindow.close()