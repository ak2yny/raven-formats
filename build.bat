set options=--specpath dist --onefile --version-file=..\pi_version_info\script.txt --icon=..\SHIELD.ico src\raven_formats\script.py
pyinstaller %options:script=xmlb%
pyinstaller --add-data ..\src\raven_formats\data\zsnd_hashes.json:. %options:script=zsnd%

REM for zsnd:  --add-data src/raven_formats/data/zsnd_hashes.json:raven_formats/data

