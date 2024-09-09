from furl import furl

from .base import BaseNode
from .group import Group

from ..utils import escape


class Link(BaseNode):
    label: str | BaseNode
    link: str
    title: str
    
    def __init__(self, label: str | BaseNode, link: str = None, title: str = '') -> None:
        super().__init__()
        
        if not link:
            self.link = label
            self.label = ''
        else:
            self.label = label
            self.link = link
        
        self.title = title
    
    def write(self) -> str:
        link = str(furl(self.link))
        
        if self.label:
            return f"[{str(self.label)}]({link}{f' "{escape(self.title, '()"')}"' if self.title else ''})"
        elif not self.label and self.title:
            return f"[{str(self.link)}]({link} \"{escape(self.title, '()"')}\")"
        else:
            return f"<{link}>"

    def __repr__(self) -> str:
        return repr(self.write())
    
    def __add__(self, value):
        if isinstance(value, Link):
            value = str(value.label)
        elif isinstance(value, BaseNode):
            return Group([self, value])
        
        return Link(self.label + value, self.link)
