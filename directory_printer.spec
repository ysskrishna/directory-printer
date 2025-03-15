# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['directory_printer/gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('directory_printer/assets/*.png', 'directory_printer/assets'),
        ('directory_printer/translations/*.json', 'directory_printer/translations'),
        ('pyproject.toml', '.'),
    ],
    hiddenimports=[
        # Core Python imports
        'tkinter',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'webbrowser',
        
        # PIL/Pillow imports
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        
        # TOML parsing
        'tomli',
        'tomli._parser',
        'tomli._re',
        'tomli._types'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='directory-printer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='directory_printer/assets/logo.png'
) 