# -*- mode: python -*-

block_cipher = None


a = Analysis(['Server.py'],
             pathex=['D:\\C-S-and-P2P-demo\\C-S'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Server',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
