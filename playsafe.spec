# playsafe.spec
# Build with:  pyinstaller playsafe.spec
# This bundles start.py (Streamlit app) + model.py (YOLO analysis) into a single PlaySafe.exe

block_cipher = None

a = Analysis(
    ['start.py'],  # your main app file
    pathex=[],
    binaries=[],
    datas=[
        ('boy-playing-at-playground_1741623809.png', '.'),  # image asset
        ('model.py', '.'),  # include your model script
    ],
    hiddenimports=[
        'pkg_resources.py2_warn',
        'cv2',
        'numpy',
        'streamlit',
        'ultralytics',
        'folium',
        'PIL',
        'requests',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PlaySafe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # hides the black terminal window
    icon='playsafe.ico',    # optional custom icon
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False,
    upx=True,
    name='PlaySafe',
)
