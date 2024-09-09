from .group import Group

class BlockQuote(Group):
    block = True
    
    def write(self) -> str:
        lines = []
        text = super().write()
        
        for line in text.splitlines():
            if line.startswith('>'):
                lines.append(f'>{line}')
            elif line == '':
                lines.append(f'>')
            else:
                lines.append(f'> {line}')
        
        return '\n'.join(lines)
