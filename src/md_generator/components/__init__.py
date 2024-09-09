from typing import Mapping

from ..md_format import MDFormatter
from .base import BaseBlockNode, BaseNode
from .blockquote import BlockQuote
from .codeblock import CodeBlock
from .document import Document
from .group import Group
from .heading import Heading
from .horizontalrule import HorizontalRule
from .image import Image
from .lines import Lines
from .link import Link
from .list import List
from .newline import NewLine
from .paragraph import Paragraph
from .sentence import Sentence
from .table import Table
from .text import Text

for name, component in {
    "document": Document,
    "paragraph": Paragraph,
    "text": Text,
    "table": Table,
    "csv": lambda csv_file: Table.from_csv(csv_file),
    "blockquote": BlockQuote,
    "quote": BlockQuote,
    "code": CodeBlock,
    "codeblock": CodeBlock,
    "list": List,
    "link": Link,
    "image": Image,
    "rule": HorizontalRule,
    "horizontalrule": HorizontalRule,
    "heading": Heading,
    "bold": lambda x: Text(x, bold = True),
    "italic": lambda x: Text(x, italic = True),
    "code": lambda x: Text(x, code = True),
}.items():
    MDFormatter.register_component(name, component)
