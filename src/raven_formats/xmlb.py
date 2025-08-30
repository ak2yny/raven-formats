import json, glob
from pathlib import Path
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
from .lib_xmlb import read_xmlb, write_xmlb, from_json_element, to_json_element, FakeDict

def decompile(xmlb_path: Path, output_path: Path, has_indent: bool):
    root_element = read_xmlb(xmlb_path)

    if output_path.suffix == '.xml':
        if has_indent:
            ET.indent(root_element, ' ' * 4)
        ET.ElementTree(root_element).write(output_path, encoding='utf-8')
    elif output_path.suffix == '.json':
        with output_path.open(mode='w', encoding='utf-8') as json_file:
            json.dump(FakeDict([to_json_element(root_element)]), json_file, indent=4 if (has_indent) else None, ensure_ascii=False)
    else:
        raise ValueError(f'Output file extension {output_path.suffix} is not supported. Supported: .xml, .json')

def parse_json_object_pairs(pairs):
    return pairs

def compile(input_path: Path, output_path: Path):
    if input_path.suffix == '.xml':
        output_path.write_bytes(write_xmlb(ET.parse(input_path).getroot()))
    elif input_path.suffix == '.json':
        with input_path.open(mode='r', encoding='utf-8') as json_file:
            data = json.load(json_file, object_pairs_hook=parse_json_object_pairs)
            root_amount = len(data)

            if root_amount != 1:
                raise ValueError(f'Found {root_amount} root elements. Required 1')

            output_path.write_bytes(write_xmlb(from_json_element(data[0])))
    else:
        raise ValueError(f'Input file extension {input_path.suffix} is not supported. Supported: .xml, .json')

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--decompile', action='store_true', help='decompile input XMLB file to XML/JSON file')
    parser.add_argument('--no_indent', action='store_true', help='disable indent in decompiled XML/JSON file')
    parser.add_argument('input', help='input file (supports glob)')
    parser.add_argument('output', help='output file (wildcards will be replaced by input file name)')
    args = parser.parse_args()
    input_files = glob.glob(args.input.replace('[', '[[]'), recursive=True)
    output = Path(args.output)

    if not input_files:
        raise ValueError('No files found')

    for input_file in input_files:
        input_file = Path(input_file)
        output_file = input_file.parent / output.with_stem(output.stem.replace('*', input_file.stem))
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if args.decompile:
            decompile(input_file, output_file, not args.no_indent)
        else:
            compile(input_file, output_file)

if __name__ == '__main__':
    main()
