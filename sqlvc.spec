# -*- mode: python -*-

block_cipher = None


a = Analysis(['sqlvc.py'],
             pathex=['/media/hellgorithm/BACKUP/sqlvc_builda_a_1_6'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='sqlvc',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='iconssqlvc-icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='sqlvc')
