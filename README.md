# Raven Formats
[![MarvelMods](https://i.imgur.com/qoCxdy8t.png)](http://marvelmods.com)

Tools to work with formats used by **Raven Software** in **MUA/XML2** games.
## Usage
#### XMLB Compile/Decompile
```
usage: xmlb.py [-h] [-c] [-d] [--no_indent] [-b XMLB_FORMAT] [-e XML_FORMAT] input [output ...]

positional arguments:
  input                 input file (supports glob)
  output                output file (wildcards will be replaced by input file name)

options:
  -h, --help            show this help message and exit
  -c, --convert         convert decompiled input file to XML/JSON file
  -d, --decompile       decompile input XMLB file to XML/JSON file
  --no_indent           disable indent in decompiled XML/JSON file
  -b XMLB_FORMAT, --xmlb_format XMLB_FORMAT
                        Binary/compiled extension - output file takes priority
  -e XML_FORMAT, --xml_format XML_FORMAT
                        Text/decompiled extension - output file takes priority
```
Notes:
- This version was designed to be used as single binary file (.exe).
- Supports drag & drop. Add arguments (e.g. -e "xml") to a shortcut to make drag & drop use this format.
- Output is optional. Name is taken from input file and optional -e/-b arguments, if not defined.
- Compile output extensions are limited to four character extensions ending in 'b'.
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