import PyInstaller.__main__

# PyInstaller.__main__.run([
#     'excel_backup_gdrive.py',
#     '--onefile',
#     '-w'#als demon = ohne shell
# ])

PyInstaller.__main__.run([
    'screenshot.py',
    '--onefile'
])