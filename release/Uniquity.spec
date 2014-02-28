# -*- mode: python -*-
a = Analysis(['../src/Uniquity.py'],
             pathex=['/Users/goodcat/projects/uniquity/release'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
assets_tree = Tree('../src/assets', prefix='assets')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Uniquity',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
		assets_tree,
               a.datas,
               strip=None,
               upx=True,
               name='Uniquity')
app = BUNDLE(coll,
             name='Uniquity.app',
             debug=True,
	     icon=None)
