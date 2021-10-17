import os
from kivy_deps import sdl2, glew

spec_root = os.path.abspath(SPECPATH)
block_cipher = None
app_name = 'Profile Software'

a = Analysis(['main.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[('main.kv', '.'), ('C:/Users/NexGen/AppData/Roaming/Python/Python39/site-packages/face_recognition_models', 'face_recognition_models'), ('Resources', 'Resources')],
             hiddenimports=['win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=app_name,
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
		*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=False,
               upx_exclude=[],
               name=app_name)
