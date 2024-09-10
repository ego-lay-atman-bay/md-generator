from copy import copy
import re

from .base import BaseNode
from .group import Group
from ..utils import escape, backtick_count


class Text(BaseNode):
    bold: bool
    italic: bool
    code: bool
    text: str
    
    def __init__(self, text: str = '', bold = False, italic = False, code = False) -> None:
        super().__init__()
        
        self.text = text
        self.bold = bold
        self.italic = italic
        self.code = code
    
    def write(self) -> str:
        text = self.text
        
        if not isinstance(text, BaseNode):
            text = escape(text, '*')
        
        text = str(text)
        if self.code:
            num_ticks = backtick_count(text)
            new_text = '`' * num_ticks
            if text.startswith('`'): new_text += ' '
            new_text += text
            if text.endswith('`'): new_text += ' '
            new_text += '`' * num_ticks

            text = new_text
        if self.bold:
            text = f'**{text}**'
        if self.italic:
            text = f'*{text}*'
        
        return text
    
    def __repr__(self) -> str:
        return repr(self.write())
    
    def __add__(self, value):
        if isinstance(value, str):
            value = value
        elif isinstance(value, Group):
            value = copy(value)
            value.insert(0, self)
            return value
        elif isinstance(value, BaseNode):
            return Group([self, value])
        
        return Text(str(self.text) + str(value), self.bold, self.italic)
    
    def __format__(self, format_spec: str) -> str:
        return super().__format__(format_spec)
