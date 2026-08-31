# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/jonas.schroeder/Documents/dev/dev/StarWars/StarWarsGame.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/jonas.schroeder/Documents/dev/dev/StarWars/Pixelarts', 'Pixelarts')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StarWarsGame',
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
    icon=['C:/Users/jonas.schroeder/Documents/dev/dev/StarWars/Pixelarts/icon.ico'],
)
