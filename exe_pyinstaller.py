import PyInstaller.__main__

PyInstaller.__main__.run([
    'screenshot-tool.py',
    '--onefile', # als one file 
    # '--onedir', # in one subfolder
    '-w'#als demon = ohne shell
])
