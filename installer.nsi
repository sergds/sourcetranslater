; SourceTranslater Mod Installer Template
; Use it to distribute final mods
; Just make sure to adjust it (as well as finalizescript.bat) for your specific game
;--------------------------------

!include 'FileFunc.nsh'

; The name of the installer
Name "SourceTranslater"

; The file to write
OutFile "portal2-gte_installer.exe"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

; Build Unicode installer
Unicode True

; The default installation directory
InstallDir "D:\SteamLibrary\steamapps\common\Portal 2"

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "Portal 2: Google Translate Edition (RU) [TEXTONLY]"

  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Back Things up
  CreateDirectory $INSTDIR\SRCTR_BACKUP
  CreateDirectory $INSTDIR\SRCTR_BACKUP\platform
  CreateDirectory $INSTDIR\SRCTR_BACKUP\platform\resource
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2\resource
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2_dlc1
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2_dlc1\resource
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2_dlc2
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2_dlc2\resource
  CreateDirectory $INSTDIR\SRCTR_BACKUP\portal2_dlc2\media
  CopyFiles "$INSTDIR\platform\resource\*_*.txt" "$INSTDIR\SRCTR_BACKUP\platform\resource"
  CopyFiles "$INSTDIR\portal2\resource\*_*.txt" "$INSTDIR\SRCTR_BACKUP\portal2\resource"
  CopyFiles "$INSTDIR\portal2_dlc1\resource\*_*.txt" "$INSTDIR\SRCTR_BACKUP\portal2_dlc1\resource"
  CopyFiles "$INSTDIR\portal2_dlc2\media\*.bik" "$INSTDIR\SRCTR_BACKUP\portal2_dlc2\media"
  CopyFiles "$INSTDIR\portal2_dlc2\resource\*_*.txt" "$INSTDIR\SRCTR_BACKUP\portal2_dlc2\resource"

  ; Put file there
  File /r "output\*.*"
  ExecWait "$INSTDIR\finalizeinstall.exe"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SourceTranslater" "DisplayName" "SourceTranslater Mod"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SourceTranslater" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SourceTranslater" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SourceTranslater" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall_srctr.exe"
  
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SourceTranslater"

  CopyFiles "$INSTDIR\SRCTR_BACKUP\*" "$INSTDIR\"

  RMDir /r "$INSTDIR\SRCTR_BACKUP\"
  ; Restore normal subtitles
  ExecWait "$INSTDIR\finalizeinstall.exe"
  ; Remove files and uninstaller
  Delete "$INSTDIR\uninstall_srctr.exe"
  Delete "$INSTDIR\finalizeinstall.exe"
  Delete "$INSTDIR\finalizescript.bat"

SectionEnd