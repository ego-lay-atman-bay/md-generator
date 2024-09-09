from .base import BaseNode

class NewLine(BaseNode):
    def write(self) -> str:
        return "<br>"
