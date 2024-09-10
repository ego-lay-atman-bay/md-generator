from copy import deepcopy

from furl import furl

from ..md_format import parse_format_spec, md_format
from ..utils import escape
from .base import BaseNode
from .group import Group


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
        
        if self.label and not self.link:
            return str(self.label)
        if self.label:
            return f"[{str(self.label)}]({link}{f' "{escape(self.title, '()"')}"' if self.title else ''})"
        elif not self.label and self.title:
            return f'[{str(self.link)}]({link} "{escape(self.title, '()"')}")'
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
    
    def __format__(self, format_spec: str) -> str:
        try:
            return super().__format__(format_spec)
        except:
            new_link = deepcopy(self)
            split_spec = parse_format_spec(format_spec)
            for part in split_spec:
                format_dict = {
                    'title': new_link.title,
                    'link': new_link.link,
                    'title': new_link.title,
                }
                
                if isinstance(part, str):
                    if not new_link.label:
                        new_link.label = new_link.link
                        new_link.link = md_format(part, **format_dict)
                    elif not new_link.title:
                        new_link.title = md_format(part, **format_dict)
                    else:
                        new_link.link = md_format(part, **format_dict)
                elif isinstance(part, tuple):
                    if part[0] == 'link':
                        if not new_link.label:
                            new_link.label = new_link.link
                        new_link.link = md_format(part[1], **format_dict)
                    elif part[0] == 'label':
                        new_link.label = md_format(part[1], **format_dict)
                    elif part[0] == 'title':
                        new_link.title = md_format(part[1], **format_dict)
            
            return str(new_link)
                        
