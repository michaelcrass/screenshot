import PyInstaller.__main__

PyInstaller.__main__.run([
    'screenshot-tool.py',
    '--onefile', # als one file 
    '-w'#als demon = ohne shell
])
