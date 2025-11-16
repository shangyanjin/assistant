# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'internal.chat',
        'internal.chat.handler',
        'internal.chat.service',
        'internal.chat.ui',
        'internal.chat.window',
        'internal.chat.model_manager',
        'internal.file',
        'internal.file.handler',
        'internal.file.service',
        'internal.file.ui',
        'internal.model',
        'internal.model.chat',
        'internal.model.config',
        'internal.ui',
        'internal.ui.components',
        'internal.ui.toolbar',
        'internal.ui.window',
        'pkg.api',
        'pkg.api.ollama',
        'pkg.utils',
        'pkg.utils.path',
        'pkg.utils.system',
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
    name='assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Icon file path (optional)
)

