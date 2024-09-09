from abc import abstractmethod

class BaseNode():
    block: bool = False
    
    @abstractmethod
    def write(self) -> str:
        return ""
    
    def __str__(self) -> str:
        text = self.write()
        if self.block:
            text = f'\n{text}\n'
        return text
    
    def __format__(self, format_spec: str) -> str:
        return str(self).__format__(format_spec)

class BaseBlockNode(BaseNode):
    block = True
    
    @abstractmethod
    def write(self) -> str:
        return ""
