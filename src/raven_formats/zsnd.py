import glob, json
from argparse import ArgumentParser
from pathlib import Path
from .lib_zsnd import read_zsnd, write_zsnd

def decompile(zsnd_path: Path, output_path: Path):
    with output_path.open(mode='w', encoding='utf-8') as json_file:
        json.dump(read_zsnd(zsnd_path, output_path), json_file, indent=4)

def compile(json_path: Path, output_path: Path):
    with json_path.open(mode='r', encoding='utf-8') as json_file:
        write_zsnd(json.load(json_file), output_path)

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--decompile', action='store_true', help='decompile input ZSND file to JSON file')
    parser.add_argument('input', help='input file (supports glob)')
    parser.add_argument('output', help='output file (wildcards will be replaced by input file name)')
    args = parser.parse_args()
    input_files = glob.glob(args.input.replace('[', '[[]'), recursive=True)

    if not input_files:
        raise ValueError('No files found')

    for input_file in input_files:
        input_file = Path(input_file)
        output_file = Path(args.output.replace('*', input_file.stem))
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if args.decompile:
            decompile(input_file, output_file)
        else:
            compile(input_file, output_file)

if __name__ == '__main__':
    main()