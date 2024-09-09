from .group import Group

class Lines(Group):
    block = True
    
    def write(self) -> str:
        return '\n'.join([str(x) for x in self])
