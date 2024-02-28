# Raven Formats
[![MarvelMods](https://i.imgur.com/qoCxdy8t.png)](http://marvelmods.com)

Tools to work with formats used by **Raven Software** in **MUA/XML2** games.
This XMLB version was designed to be used as an .exe to associate files with. Tested on Windows 11 with [PyInstaller, self contained, single file](https://pyinstaller.org/en/stable/usage.html#cmdoption-F).
## Open With Usage for XMLB
- Build the .exe and place it anywhere, e.g. 'C:\Modding\Raven-Formats\xmlb.exe'.
- Use the usual way to associate files with this .exe. This can be done either through right-click > 'Open with' (> 'Choose another app' if available), or in [settings](https://support.microsoft.com/windows/change-default-programs-in-windows-e5d82cad-17d1-c53b-3505-f10a32e1894d).
- This will now open the files with Notepad by default. To change the settings, create a new .json file with the name config.json next to xmlb.exe (e.g. 'C:\Modding\Raven-Formats\config.json') with content as in the examples below:
```json
{
  "app": "C:\\Modding\\XiMpLe\\XiMpLe.exe",
  "decompileFormat": "xml"
}
```
```json
{
  "app": "Notepad++",
  "decompileFormat": "json"
}
```
## Command Line Usage
#### XMLB Decompile
Note: Opens each decompiled file
```
usage: xmlb.py [-h] [--no_indent] [input ...]

positional arguments:
  input            input file (supports glob)

optional arguments:
  -h, --help       show this help message and exit
  --no_indent      disable indent in decompiled XML/JSON file
```
#### ZSND Compile/Decompile
```
usage: zsnd.py [-h] [-d] [-g] input output

positional arguments:
  input               input file (supports glob)
  output              output file (wildcards will be replaced by input file name)

options:
  -h, --help          show this help message and exit
  -d, --decompile     decompile input ZSND file to JSON file and extract sound files
  -g, --generatehash  generate a PJW hash number from strings on separate lines in a text file
```