from .lines import Lines
from ..utils import backtick_count

class CodeBlock(Lines):
    lang: str
    
    def __init__(self, *group, lang = ''):
        super().__init__(*group)
        self.lang = lang
    
    def write(self) -> str:
        contents = super().write()
        
        num_ticks = backtick_count(contents, 3)
        
        result = '`' * num_ticks
        if self.lang:
            result += str(self.lang)
        result += '\n' + contents + '\n'
        result += '`' * num_ticks
        
        return result
