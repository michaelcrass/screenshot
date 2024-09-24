import PyInstaller.__main__

# requirements:
# pip install -r requirements.txt
# py -m pip install pigar
# # py -m pigar generate


PyInstaller.__main__.run([
    'screenshot-tool.py',
    '--onefile', # als one file 
    # '--onedir', # in one subfolder
    '--icon=screenshot.ico',
    '-w'#als demon = ohne shell
])
