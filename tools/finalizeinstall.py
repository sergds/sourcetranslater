# Insert this into your Google Translate mod root, and make your to installer to exec it after install.
# It will recompile closecaption, subtitles, etc.
import time
import PySimpleGUI as sg
import os
import sys

modlang = 'russian'

sg.theme('DarkGrey11')

print("im here: " + os.path.dirname(sys.executable))
os.chdir(os.path.dirname(sys.executable))

layout = [[sg.Titlebar("finalizeinstall by sergds for [KRINGE TEAM]")],
        [sg.Text('Finalizing install...', font='Courier 25')],
        [sg.Text(key='-status-', font='Courier 12')],]

window = sg.Window("finalizeinstall by sergds for [KRINGE TEAM] [PORTAL2]", layout, size=(450,150), keep_on_top=True, titlebar_icon=b'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', enable_close_attempted_event=True, icon=b'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')

failed = False

while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if failed:
        time.sleep(3)
        break
    if not 'bin' in os.listdir('.'):
        window["-status-"].update("ERROR: Not a source install!")
        failed = True
        continue
    if not 'captioncompiler.exe' in os.listdir('bin'):
        window["-status-"].update("ERROR: No captioncompiler.exe; install SDK!")
        failed = True
        continue
    if window['-status-'].get() != "Compiling Captions...":
        window["-status-"].update("Compiling Captions...")
        continue
    else:
        os.system(r"finalizescript.bat")
        window["-status-"].update("Done.")
        failed = True
window.close()