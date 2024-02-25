for %%p in (xmlb, zsnd) do pyinstaller --specpath dist --onefile --icon=..\SHIELD.ico src\raven_formats\%%p.py

