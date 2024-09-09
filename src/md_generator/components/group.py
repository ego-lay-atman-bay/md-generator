from typing import Iterable, overload

from .base import BaseNode

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
    
    def __add__(self, value):
        return Group(list.__add__(self, value))
