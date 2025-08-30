from pathlib import Path
from collections import defaultdict
from collections.abc import Iterator
from itertools import chain # accumulate, 
from struct import Struct, unpack_from
import xml.etree.ElementTree as ET

# Note: Using size from Struct is slightly slower than using numbers directly
header_fmt = Struct('< 2I') #magic_number, version
element_fmt = Struct('<'
    'I' #name_offset
    'i' #next_element_offset
    'i' #sub_element_offset
    'I' #attr_count
)
attr_fmt = header_fmt #name_offset, value_offset

def indices_of_null(data: bytes, offset: int) -> Iterator:
    yield offset
    for _ in range(data[offset:].count(b'\x00') - 1):
        offset = data.index(b'\x00', offset) + 1
        yield offset

def read_element(data: bytes, offset: int) -> tuple[ET.Element, int]:
    name_offset,\
    next_element_offset,\
    sub_element_offset,\
    attr_count = element_fmt.unpack_from(data, offset)
    element = ET.Element(string_offsets[name_offset])
    
    for o in range(offset + 16, offset + 16 + attr_count * 8, 8):
        name_offset, value_offset = attr_fmt.unpack_from(data, o)
        element.set(string_offsets[name_offset], string_offsets[value_offset])

    while sub_element_offset != -1:
        sub_element, sub_element_offset = read_element(data, sub_element_offset)
        element.append(sub_element)

    return element, next_element_offset

def read_xmlb(xmlb_path: Path) -> ET.Element:
    data = xmlb_path.read_bytes()
    magic_number, version = header_fmt.unpack_from(data)

    if magic_number != 0x11B1 or version != 1:
        raise ValueError('Invalid magic number')

    global string_offsets
    string_table_offset, = unpack_from('< I', data, header_fmt.size)
    for offset, string in zip(
        indices_of_null(data, string_table_offset),
        data[string_table_offset:].decode('cp1252').split('\x00')):
        string_offsets[offset] = string

    root_element, next_element_offset = read_element(data, header_fmt.size)
    return root_element

#https://stackoverflow.com/a/29520802/15020406
class FakeDict(dict):
    def __init__(self, items):
        self['something'] = 'something'
        self._items = items
    def items(self):
        return self._items

def str2value(string: str):
    value = string

    try:
        value = int(value)

        if len(str(value)) < len(string):
            value = string
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
    return value

def to_json_element(element: ET.Element) -> tuple[str, FakeDict]:
    elements = []

    for name, value in element.items():
        elements.append((name, str2value(value)))

    for sub_element in element:
        elements.append(to_json_element(sub_element))

    return (element.tag, FakeDict(elements))

def get_offset() -> int:
    prev_key = tuple(string_offsets)[-1]
    return string_offsets[prev_key] + len(prev_key) + 1

string_offsets = defaultdict(lambda: get_offset())

def pack_elements(offset: int, element: ET.Element, last_index: int) -> Iterator:
    for sub_element_index, sub_element in enumerate(element):
        data = pack_element(offset, sub_element, sub_element_index < last_index)
        offset += len(data)
        yield data

def pack_element(offset: int, element: ET.Element, has_next: bool) -> bytes:
    attr_count = len(element.attrib)
    sub_element_count = len(element)
    sub_element_offset = offset + 16 + attr_count * 8 if sub_element_count > 0 else -1
    next_element_offset = offset + sum(16 + len(e.attrib) * 8 for e in element.iter()) if has_next else -1

    return element_fmt.pack(string_offsets[element.tag], next_element_offset,
                            sub_element_offset, attr_count) + \
           b''.join(chain(
                (attr_fmt.pack(string_offsets[name], string_offsets[value])
                    for name, value in element.items()),
                (pack_elements(sub_element_offset, element, sub_element_count - 1))))

def write_xmlb(root_element: ET.Element) -> bytes:
    string_offsets.clear()
    string_offsets[root_element.tag] = header_fmt.size + sum(16 + len(e.attrib) * 8 for e in root_element.iter())
    return header_fmt.pack(0x11B1, 1) + \
           pack_element(header_fmt.size, root_element, False) + \
           '\x00'.join(string_offsets).encode('cp1252') + b'\x00'

def value2str(value) -> str:
    if isinstance(value, str):
        return value

    string = str(value)
    return string.lower() if (isinstance(value, bool)) else string

def from_json_element(element: tuple) -> ET.Element:
    tag, sub_elements = element
    xml_element = ET.Element(tag)

    for element in sub_elements:
        tag, value = element

        if isinstance(value, list):
            xml_element.append(from_json_element(element))
        else:
            xml_element.set(tag, value2str(value))

    return xml_element
