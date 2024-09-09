from .base import BaseNode, BaseBlockNode
from .group import Group
from .text import Text


class Heading(BaseBlockNode):
    level: int
    content: str | BaseNode
    def __init__(self, text: str = None, level: int = 1) -> None:
        super().__init__()
        
        self.level = level
        self.content = text
    
    @property
    def level(self) -> int:
        try:
            self.level = self._level
        except:
            return 1
        return self._level
    
    @level.setter
    def level(self, level: int):
        self._level = int(float(level))
        
        self._level = max(1, min(self._level, 6))
    
    def write(self) -> str:
        return f"{'#' * self.level} {str(self.content)}"
    
    def __repr__(self) -> str:
        return repr(self.write())
    
    def __add__(self, value: str | BaseNode):
        return Heading(self.content + value, self.level)
