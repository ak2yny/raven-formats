import json, glob
from pathlib import Path
from argparse import ArgumentParser
from struct import Struct
from io import BytesIO
import xml.etree.ElementTree as ET

FBFileHeader = Struct(
    '128s' # file path
    '64s' # file type
    'I' # file size
)

XML_F = ['xml', 'eng', 'fre', 'ger', 'ita', 'spa', 'rus', 'pol']
XML_Formats = []
for f in XML_F:
    XML_Formats.append('.' + f)
    XML_Formats.append('.' + f + 'b')

Known_Formats = {
    'actors.igb': 'actorskin',
    'anim.igb': 'actoranimdb',
    'textures.igb': 'texture',
    'conversations.xmlb': 'xml',
    'data.xmlb': 'xml',
    'weapons.xmlb': 'xml',
    'entities.xmlb': 'xml',
    'talents.xmlb': 'xml_talents',
    'powerstyles.xmlb': 'fightstyle',
    'fightstyles.xmlb': 'fightstyle',
    'shared_nodes.xmlb': 'fightstyle_xml',
    'effects.xmlb': 'effect',
    'maps.xmlb': 'zonexml',
    'motionpaths.igb': 'motionpath',
    'shared_powerups.xmlb': 'shared_powerups',
    '.xmlb': 'xml_resident',
    '.igb': 'model',
    '.py': 'script',
    '.chrb': 'characters',
    '.chr': 'characters',
    '.navb': 'nav',
    '.nav': 'nav',
    '.boyb': 'boy',
    '.boy': 'boy',
    '.pkgb': 'pkg',
    '.pkg': 'pkg',
    '.zam': 'zam',
    '.shd': 'shadow',
    '.sdfb': 'sdf',
    '.sdf': 'sdf'
}

#This is a duplicate of xmlb - it should probably be a separate file to import
#http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Note: The dictionary key/val is reverse, because a dictionary doesn't allow duplicate keys
def dict_to_xml(tag: str, d: dict) -> ET.ElementTree:
    root = ET.Element(tag)
    for val, key in d.items():
        child = ET.SubElement(root, key)
        #inner text: child.text = str(val)
        child.set('filename', val.rstrip('/')) #attribute

    indent(root)
    return ET.ElementTree(root)

def xml_to_dict(r: ET.ElementTree) -> dict:
    d = {}
    for e in r.findall("./*"):
        d[e.attrib['filename']] = e.tag
    return d

def check_exist(entries: dict, file_path: str) -> str:
    if file_path in entries:
        return check_exist(entries, (file_path + '/'))
    else:
        return file_path

def decompile(fb_path: Path, output_path: Path):
    fb_data = fb_path.read_bytes()

    with BytesIO(fb_data) as fb_file:
        entries = {}

        while (file_header := fb_file.read(FBFileHeader.size)):
            file_path, file_type, file_size = FBFileHeader.unpack(file_header)
            file_path = file_path.decode().split('\x00', 1)[0]
            file_type = file_type.decode().split('\x00', 1)[0]
            file_data = fb_file.read(file_size)

            entries[check_exist(entries, file_path)] = file_type
            file_path = output_path.parent / output_path.stem / file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(file_data)

        if output_path.suffix.lower() == '.json':
            output_path.write_text(json.dumps(entries, indent=4))
        else:
            #Every other extension uses XML format (no extension errors)
            dict_to_xml('packagedef', entries).write(output_path, encoding='utf-8')

def compile(input_path: Path, output_path: Path):
    data = input_path.read_text()
    if data.lstrip()[0] == '{':
        d = json.loads(data)
    else:
        d = xml_to_dict(ET.fromstring(data))
    #Try XML for every other file (intentionally not using filter)
    #elif data.lstrip()[0] == '<':

    with BytesIO() as fb_data:
        for file_path, file_type in d.items():
            file_path = file_path.rstrip('/')
            real_file_path = input_path.parent / input_path.stem / file_path
            file_data = real_file_path.read_bytes()
            fb_file_header = FBFileHeader.pack(file_path.encode(), file_type.encode(), len(file_data))

            fb_data.write(fb_file_header)
            fb_data.write(file_data)

        #Not forcing FB extension for now
        #output_path = output_path.parent / (output_path.stem + '.fb')
        output_path.write_bytes(fb_data.getbuffer())

def rebuild(input_path: Path, output_path: Path):
    data = input_path.read_text()
    if data.lstrip()[0] == '{':
        d = json.loads(data)
    else:
        d = xml_to_dict(ET.fromstring(data))

    input_folder = input_path.parent / input_path.stem

    with BytesIO() as fb_data:
        for file_path, file_type in d.items():
            if file_type in ('combat_is', 'bigconvmap'):
                file_path = file_path.rstrip('/')
                fb_file_header = FBFileHeader.pack(file_path.encode(), file_type.encode(), 0)
                fb_data.write(fb_file_header)

        for p in input_folder.rglob("*.*"):
            file_path = str(p.relative_to(input_folder)).replace('\\', '/')
            if file_path in d:
                file_type = d[file_path]
            else:
                folders = file_path.split('/')
                sf = folders[1] if len(folders) > 1 else ''
                dp = sf.rsplit('.', maxsplit=1)[0]
                folder = sf if folders[0] == 'data' and '.' not in sf else 'anim' if folders[0] == 'actors' and not all(d in '0123456789' for d in p.stem) else dp if dp == 'shared_powerups' else dp[0:12] if dp[0:12] == 'shared_nodes' else folders[0]
                e = p.suffix.lower()
                if e in XML_Formats: e = '.xmlb'
                type_string = folder + e
                file_type = Known_Formats[type_string] if type_string in Known_Formats else Known_Formats[e] if e in Known_Formats else 'unknown'
            file_data = p.read_bytes()
            fb_file_header = FBFileHeader.pack(file_path.encode(), file_type.encode(), len(file_data))

            fb_data.write(fb_file_header)
            fb_data.write(file_data)

        output_path.write_bytes(fb_data.getbuffer())

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--decompile', action='store_true', help='decompile input FB file to JSON file')
    parser.add_argument('-r', '--rebuild', action='store_true', help='compile to FB file, including all files that exist in the corresponding directory')
    parser.add_argument('input', help='input file (supports glob)')
    parser.add_argument('output', help='output file (wildcards will be replaced by input file name)')
    args = parser.parse_args()
    input_files = glob.glob(args.input, recursive=True)

    if not input_files:
        raise ValueError('No files found')

    for input_file in input_files:
        input_file = Path(input_file)
        output_file = Path(args.output.replace('*', input_file.stem))
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if args.decompile:
            decompile(input_file, output_file)
        elif args.rebuild:
            rebuild(input_file, output_file)
        else:
            compile(input_file, output_file)

if __name__ == '__main__':
    main()