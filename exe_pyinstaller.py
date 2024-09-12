import PyInstaller.__main__

PyInstaller.__main__.run([
    'screenshot.py',
    '--onefile', # als one file 
    '-w'#als demon = ohne shell
])
