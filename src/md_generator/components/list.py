from typing import Iterable, overload

from .base import BaseNode
from .lines import Lines
from ..utils import indent


class List(Lines):
    block = True
    
    ordered: bool
    start: int
    marker: str = '-'
    
    @overload
    def __init__(self) -> None: ...
    def __init__(self, *group: Iterable, ordered: bool = False) -> None:
        super().__init__(group)
        
        self.ordered = bool(ordered)
        self.start = 1
    
    def write(self) -> str:
        lines = []
        
        index = int(self.start)
        marker = self.marker
        
        for line in self:
            if isinstance(line, BaseNode) and line.block:
                lines.append(indent(str(line)))
            else:
                if self.ordered:
                    marker = f'{index}.'
                    index += 1
                
                lines.append(f"{marker} {str(line)}")
        
        return '\n'.join(lines)


