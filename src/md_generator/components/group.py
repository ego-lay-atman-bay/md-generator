from typing import Iterable, overload

from ..md_format import parse_format_spec, parse_format_spec_part, md_format
from .base import BaseNode
# from .text import Text


class Group(BaseNode, list):
    separator: str = ''
    
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, *group: Iterable, separator: str = '') -> None: ...
    def __init__(self, *group: Iterable, separator: str = '') -> None:
        if group == None:
            list.__init__(self)
        elif len(group) == 0:
            list.__init__(self)
        elif len(group) == 1 and isinstance(group[0], (list, tuple, set)):
            list.__init__(self, group[0])
        else:
            list.__init__(self, group)
        
        self.separator = str(separator)
        
    def write(self) -> str:
        return self.separator.join([str(part) for part in self])
    
    @classmethod
    def from_str(cls, string: str, separator: str = ';'):
        return Group(str(string).split(separator), separator = separator)
    
    def __add__(self, value):
        return Group(list.__add__(self, value))
    
    def __format__(self, format_spec: str) -> str:
        formatted_group = self.copy()
        
        split_spec, rest = parse_format_spec_part(format_spec)
        if split_spec[0] and isinstance(split_spec[0], str):
            formatted_group.separator = split_spec[0]
            split_spec, rest = parse_format_spec_part(format_spec)
        else:
            rest = format_spec
        
        for part in split_spec:
            if isinstance(part, tuple):
                if part[0] in ['sep', 'separator']:
                    formatted_group.separator = part[1]
                    split_spec, rest = parse_format_spec_part(format_spec)

        new_group = Group(separator = formatted_group.separator)
        for item in formatted_group:
            if isinstance(item, (list, tuple, set)):
                item = Group(item, separator = formatted_group.separator)
            
            new_group.append(md_format(f'{{item:{rest}}}', item = item))
            
        return str(new_group)
