import glob
from os.path import splitext
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
    'aipatterns.xml': 'aipatterns',
    'entities.xmlb': 'xml',
    'fightstyles.xmlb': 'fightstyle',
    'powerstyles.xmlb': 'fightstyle',
    'talents.xmlb': 'xml_talents',
    'weapons.xmlb': 'xml',
    'shared_nodes.xmlb': 'fightstyle_xml',
    'effects.xmlb': 'effect',
    'maps.xmlb': 'zonexml',
    'motionpaths.igb': 'motionpath',
    'common_ents.xmlb': 'common_ents',
    'item_ents.xmlb': 'item_ents',
    'shared_nodes.xmlb': 'shared_nodes',
    'shared_nodes_combat.xmlb': 'shared_nodes_combat',
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

Dir_In_Type = {
    'actorskin': 'actors',
    'actoranimdb': 'actors',
    'effect': 'effects'
}

def decompile(fb_path: Path, output_path: Path):
    fb_data = fb_path.read_bytes()

    with BytesIO(fb_data) as fb_file:
        entries = ET.Element('packagedef')

        while (file_header := fb_file.read(FBFileHeader.size)):
            file_path, file_type, file_size = FBFileHeader.unpack(file_header)
            file_path = file_path.decode().split('\x00', 1)[0]
            file_type = file_type.decode().split('\x00', 1)[0]
            file_data = fb_file.read(file_size)

            file_info, ext = splitext(file_path)
            for d in list(Dir_In_Type.values()):
                Dir = d + '/'
                if file_info.lower().startswith(Dir):
                    file_info = file_info[len(Dir):]
                    break
            if not any(e.attrib['filename'].lower() == file_info.lower() for e in entries.findall("./*")):
                child = ET.SubElement(entries, file_type)
                #inner text: child.text = str(file_info)
                child.set('filename', file_info) #attribute

            file_path = output_path.parent / output_path.stem / file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(file_data)

        ET.indent(entries, ' ' * 4)
        ET.ElementTree(entries).write(output_path, encoding='utf-8')

def compile(xml_path: Path, output_path: Path):
    data = ET.parse(xml_path)

    with BytesIO() as fb_data:
        for e in data.findall("./*"):
            file_path = e.attrib['filename']
            file_type = e.tag.lower()
            if file_type in list(Dir_In_Type.keys()):
                Dir = Dir_In_Type[file_type] + '/'
                if not file_path.lower().startswith(Dir):
                    file_path = Dir + file_path
            file_info, ext = splitext(file_path)
            ext = [ext]
            if ext[0] == '':
                try:
                    ext = list(Known_Formats.keys())[list(Known_Formats.values()).index(file_type)]
                    ext = [ext[ext.index('.'):]]
                    if ext[0] in XML_Formats:
                        ext = XML_Formats
                except:
                    print(f"WARNING: Unknown file type '{file_type}'. '{file_path}' not packed.")
                    continue

            Any = False
            for e in ext:
                file_path = file_info + e
                real_file_path = xml_path.parent / xml_path.stem / file_path
                if real_file_path.exists():
                    Any = True
                    file_data = real_file_path.read_bytes()
                    fb_file_header = FBFileHeader.pack(file_path.encode(), file_type.encode(), len(file_data))
                    
                    fb_data.write(fb_file_header)
                    fb_data.write(file_data)

            if not Any:
                print(f"WARNING: File '{file_path}' not found and not packed.")

        output_path.write_bytes(fb_data.getbuffer())

def rebuild(xml_path: Path, output_path: Path):
    data = ET.parse(xml_path)
    input_folder = xml_path.parent / xml_path.stem

    with BytesIO() as fb_data:
        for file_type in ('combat_is', 'bigconvmap'):
            e = data.find('./' + file_type)
            if e is not None:
                file_path = e.attrib['filename']
                fb_file_header = FBFileHeader.pack(file_path.encode(), file_type.encode(), 0)
                fb_data.write(fb_file_header)

        for p in input_folder.rglob("*.*"):
            file_type = ''
            file_path = str(p.relative_to(input_folder)).replace('\\', '/')
            file_lowr = file_path.lower()
            file_info = file_lowr.removesuffix(p.suffix)
            for e in data.findall("./*"):
                if e.attrib['filename'].lower() in (file_lowr, file_info):
                    file_type = e.tag
            if file_type == '':
                folders = file_lowr.split('/')
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
    parser.add_argument('-d', '--decompile', action='store_true', help='decompile input FB file to XML package and extract all files')
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