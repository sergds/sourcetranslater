# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['UNInstaller.py'],
    pathex=[],
    binaries=[],
    datas=[('data.uni', 'uni'), ('uninstaller.json', 'uni'), ('captioncompiler.exe', 'uni'), ('unimusic.ogg', 'uni')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UNInstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['srctr.png'],
)
