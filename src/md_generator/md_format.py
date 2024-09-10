import re
from typing import TYPE_CHECKING, Callable, Any, Mapping
from copy import deepcopy
import string
import os
from collections.abc import Sequence

import charset_normalizer

from .utils import escape

if TYPE_CHECKING:
    from .components import BaseNode

class FormattedList(list):
    def __format__(self, format_spec: str) -> str:
        separator = ', '
        if format_spec:
            separator = format_spec
        return separator.join(self)

class EscapeFormat():
    def __init__(self, key):
        if isinstance(key, (list, tuple, set)):
            key = FormattedList(key)
        self.key = key

    def __format__(self, spec: str):
        result = self.key
        if spec.lower() == "fftext":
            result = str(result)
            escape_chars = r'\:"()[]'
            result = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', result)
            result = result.replace("'", r"'\\\''")
        else:
            result = self.key.__format__(spec)
        return result
    
    def __str__(self) -> str:
        return str(self.key)
    
    def __repr__(self) -> str:
        return repr(self.key)

class MissingKey():
    conversion = ''
    
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return repr(self.value)
    
    def __format__(self, format_spec: str) -> str:
        return f'{str(self)}{':' if format_spec else ''}{format_spec}'

class FileContents():
    conversion = ''
    
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return repr(self.value)
    
    def __format__(self, format_spec: str) -> str:
        return f'{str(self)}{':' if format_spec else ''}{format_spec}'
    

# class MDFormatter():
#     COMPONENTS = {}
#     
#     def __init__(self, data):
#         self.data = data
#     @classmethod
#     def register_component(cls, name: str, component: "BaseNode | Callable[[str], BaseNode]"):
#         if not isinstance(name, str):
#             raise TypeError('name must be str')
#         
#         cls.COMPONENTS[name.lower()] = component
#         
#     def __format__(self, format_spec: str) -> str:
#         result = str(self.data)
#         split_spec = format_spec.split(':')
#         
#         if len(split_spec) > 0:
#             component_name = split_spec[0].lower()
#             if not component_name in self.COMPONENTS:
#                 return result.__format__(format_spec)
#             
#             component = self.COMPONENTS[component_name](self.data)
#             return component.__format__(':'.join(split_spec[1::]))
#         else:
#             return result.__format__(format_spec)
#     
#     def __str__(self) -> str:
#         return str(self.data)
#     
#     def __repr__(self) -> str:
#         return repr(self.data)

class SafeFormatDict(dict):
    def __missing__(self, key):
        return MDFormatter(key)
    
    def __getitem__(self, key):
        return EscapeFormat(super().__getitem__(key))

class KeyValue():
    value: Any = None
    conversion: str = ''
    
    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value
    
    @property
    def key(self):
        if self.__key == None:
            return str(self.value)
        return self.__key
    @key.setter
    def key(self, key):
        if key == None:
            self.__key = None
        self.__key = str(key)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return repr(self.value)
    
    def __getattr__(self, name: str) -> Any:
        if name in dir(self.value):
            return getattr(self.value, name)

class MDFormatter(string.Formatter):
    COMPONENTS = {}
    
    def vformat(self, format_string, args, kwargs):
        used_args = set()
        result, _ = self._vformat(format_string, args, kwargs, used_args, 99) # I want a large recursive limit
        self.check_unused_args(used_args, args, kwargs)
        return result
    
    @classmethod
    def register_component(cls, name: str, component: "BaseNode | Callable[[str], BaseNode]"):
        if not isinstance(name, str):
            raise TypeError('name must be str')
        
        cls.COMPONENTS[name.lower()] = component
    
    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> Any:
        try:
            value, key = super().get_field(field_name, args, kwargs)
            return KeyValue(field_name, value), key
        except:
            if field_name.startswith('[') and field_name.endswith(']') and os.path.isfile(field_name[1:-1]):
                contents = field_name[1:-1]
                file = charset_normalizer.from_path(field_name[1:-1]).best()
                contents = file.output().decode()
                return KeyValue(field_name, FileContents(contents)), field_name
            else:
                return KeyValue(field_name, MissingKey(field_name)), field_name
    
    
    def convert_field(self, value, conversion: str | None):
        key = ''
        
        if isinstance(value, KeyValue):
            key = value.key
            value = value.value
        
        if isinstance(value, (MissingKey, FileContents)):
            value.conversion = conversion
            result = KeyValue(key, value)
        else:
            result = KeyValue(key, super().convert_field(value, conversion))

        result.conversion = conversion

        return result
    
    def format_field(self, value: Any, format_spec: str) -> Any:
        # if isinstance(value, MissingKey):
        #     return f'{{{super().format_field(value, format_spec)}}}'
        
        result = str(value)
        
        old = format_spec
        split_spec, rest = parse_format_spec_part(format_spec)
        
        bracket_level = 0
        
        if len(split_spec[0]) > 2 and isinstance(split_spec[0], str) and split_spec[0][0] + split_spec[0][-1] == '{}':
            bracket_str_num = ''
            if isinstance(split_spec[0], str):
                bracket_str_num = split_spec[0][1:-1]
            else:
                bracket_str_num = split_spec[0][1]
            
            if bracket_str_num.isnumeric():
                bracket_level = int(bracket_str_num)
            
            old = rest
            split_spec, rest = parse_format_spec_part(rest)
            
        if bracket_level > 0:
            key = str(value)
            conversion = None
            if isinstance(value, KeyValue):
                key = value.key
                conversion = value.conversion
            
            return ('{' * (2 ** (bracket_level - 1))) + key + (f'!{conversion}' if conversion else '') + (f':{old}' if old else '') + '}' * (2 ** (bracket_level - 1))
        
        if isinstance(value, KeyValue):
            value = value.value
        
        if len(split_spec) > 0:
            for part in split_spec:
                if isinstance(part, str):
                    component_name = part.lower()
                    if component_name in self.COMPONENTS:
                        component = self.COMPONENTS[component_name](value)
                        result = super().format_field(component, rest)
                        break
                    else:
                        result = super().format_field(value, old)
                        break
                elif isinstance(part, tuple):
                    component_name = part[0].lower()
                    if component_name in self.COMPONENTS:
                        args = []
                        kwargs = {}
                        
                        if isinstance(part[1], str):
                            args.append(part[1])
                        else:
                            for arg in part[1]:
                                if isinstance(arg, str):
                                    args.append(arg)
                                elif isinstance(arg, list):
                                    kwargs[arg[0]] = arg[1]
                        
                        component = self.COMPONENTS[component_name](value, *args, **kwargs)
                        result = super().format_field(component, rest)
                        break
                    else:
                        result = super().format_field(value, old)
                        break
        else:
            result = super().format_field(value, old)
        
        if hasattr(value, 'conversion') and value.conversion:
            result = super().convert_field(result, value.conversion)
        
        return result

def md_format(string: str, **values: dict[str,str]):
    for key in values:
        try:
            values[key] = int(values[key])
        except:
            try:
                values[key] = float(values[key])
            except:
                pass
    return MDFormatter().format(string, **values)

def parse_format_spec(format_spec: str):
    """
    
    csv -> [csv]
    csv:test -> [csv,test]
    csv:test=hello -> [csv, (test, hello)]
    csv:test=hello,world -> [csv, (test, [hello, world])]
    csv:test=hello=world,wow=hello -> [csv, (test, [(hello, world), (wow,hello)])]
    csv:test=hello=(world,wow)
    
    
    """
    
    result = []
    rest = format_spec
    
    while rest != '':
        new, rest = parse_format_spec_part(rest)
        result.extend(new)
    
    return result


def parse_format_spec_part(format_spec: str) -> tuple[list, str]:
    """Parse format spec part

    Args:
        format_spec (str): format spec

    Returns:
        tuple[list, str]: (parsed, rest)
    """
    index = -1
    result = []
    character = lambda peek = 0: format_spec[index + peek] if (index + peek) < len(format_spec) else ''
    
    key = ''
    value: list[str] = []
    
    def get_section_item():
        item = key
        
        section_value = deepcopy(value)
        
        if len(section_value) > 0:
            item = (key, section_value[0] if len(section_value) == 1 and isinstance(section_value[0], str) else section_value)
        
        return item
    
    def is_empty_value():
        if key == '':
            return True
        elif len(value) == 0:
            return True
        elif isinstance(value[-1], str) and value[-1] == '':
            return True
        elif isinstance(value[-1], list) and len(value[-1]) > 0 and value[-1][-1] == '':
            return True
        
        return False
    
    mode = 'key'
    
    quote_char = ''
    raw_escape = False
    
    brackets = []
    
    while index < len(format_spec):
        index += 1
        char = character()
        
        if character() == '\\':
            index += 1
            if raw_escape:
                char = f'\\{character()}'
        elif quote_char:
            if character() == quote_char:
                raw_escape = False
                quote_char = ''
                continue
        elif is_empty_value() and character() == 'r' and character(1) in ["'", '"']:
            raw_escape = True
            quote_char = character(1)
            index += 1
            continue
        elif is_empty_value() and character() and character() in ["'", '"']:
            raw_escape = False
            quote_char = character()
            continue
        elif character() and character() in ['(','{','[','<']:
            # if character() == '[' and ']' not in brackets:
            #     brackets.append(']')
            #     char = '{'
            # else:
            #     print('char', character())
            brackets.append({'(': ')', '{': '}', '[': ']', '<': '>'}[character()])
        elif len(brackets):
            if character() == brackets[-1]:
                brackets.pop()
                # if ']' not in brackets:
                #     char = '}'
        elif character() == ':':
            mode = 'key'
            break
        elif mode == 'key':
            if character() == '=':
                mode = 'value'
                value.append('')
                continue
        elif mode == 'value':
            if character() == '=':
                value[-1] = [value[-1], '']
                continue
            elif character() == ',':
                value.append('')
                continue
            
        if mode == 'key':
            key += char
        elif mode == 'value':
            if len(value) == 0:
                value.append('')
            if isinstance(value[-1], str):
                value[-1] += char
            elif isinstance(value[-1], list):
                value[-1][-1] += char
    
    result.append(get_section_item())
    
    return result, format_spec[index + 1::]
