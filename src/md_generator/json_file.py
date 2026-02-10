import os
from copy import deepcopy

import charset_normalizer
import json5

from .md_format import MDFormatter, parse_format_spec
from .utils import strnum


def read_json_file(file) -> dict:
    try:
        if file == None:
            return {}
        elif (isinstance(file, dict)):
            return deepcopy(file)
        elif (isinstance(file, str)):
            if os.path.isfile(file):
                json_file = charset_normalizer.from_path(file).best()
                return json5.loads(json_file.output().decode())
            else:
                return json5.loads(file)
        elif (hasattr(file, 'read')):
            return json5.load(file)
        else:
            return json5.loads(str(file))

    except Exception as e:
        e.add_note(str(file))
        raise e

class JsonContent():
    def __init__(self, json_data) -> None:
        self.data = read_json_file(json_data)
    
    def __format__(self, format_spec: str) -> str:
        split_spec = parse_format_spec(format_spec)

        current_data = self.data

        for part in split_spec:
            if isinstance(part, str):
                try:
                    current_data = current_data[part]
                except:
                    current_data = current_data[strnum(part)]
        
        return str(current_data)
        

MDFormatter.register_component('json', JsonContent)
MDFormatter.register_component('json5', JsonContent)
