# Raven Formats
[![MarvelMods](https://i.imgur.com/qoCxdy8t.png)](http://marvelmods.com)

Tools to work with formats used by **Raven Software** in **MUA/XML2** games.
## Usage
#### XMLB Compile/Decompile
```
usage: xmlb.py [-h] [-c] [-d] [--no_indent] input output

positional arguments:
  input            input file (supports glob)
  output           output file (wildcards will be replaced by input file name)

optional arguments:
  -h, --help       show this help message and exit
  -c, --convert    convert decompiled input file to XML/JSON file
  -d, --decompile  decompile input XMLB file to XML/JSON file
  --no_indent      disable indent in decompiled XML/JSON file
```
#### ZSND Compile/Decompile
```
usage: zsnd.py [-h] [-d] [-g] input output

positional arguments:
  input               input file (supports glob)
  output              output file (wildcards will be replaced by input file name)

optional arguments:
  -h, --help          show this help message and exit
  -d, --decompile     decompile input ZSND file to JSON file and extract sound files
  -g, --generatehash  generate a PJW hash number from strings on separate lines in a text file
```

#### FB Compile/Decompile
```
usage: fb.py [-h] [-d] input output

positional arguments:
  input            input file (supports glob)
  output           output file (wildcards will be replaced by input file name)

optional arguments:
  -h, --help       show this help message and exit
  -d, --decompile  decompile input FB file to JSON file
```