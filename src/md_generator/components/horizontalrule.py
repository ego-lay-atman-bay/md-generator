from .base import BaseBlockNode

class HorizontalRule(BaseBlockNode):
    def write(self) -> str:
        return '---'
