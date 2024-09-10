import csv
import io
import os
from typing import IO, Any, Iterable, Literal, Optional, Callable
from itertools import zip_longest
import itertools
import operator
from copy import deepcopy
import re

from ..utils import escape, strbool
from .base import BaseBlockNode
from .enums import ALIGNMENT, ALIGNMENT_SHORT
from .. import csv_tools


from ..md_format import parse_format_spec

class Table(BaseBlockNode):
    def __init__(
        self,
        header: Iterable,
        rows: Optional[Iterable[Iterable]] = None,
        alignment: list[Literal[ALIGNMENT.LEFT, ALIGNMENT.CENTER, ALIGNMENT.RIGHT]] = None,
    ) -> None:
        super().__init__()
        
        if rows == None:
            if isinstance(header[0], (list, tuple, set)):
                rows = header[1::]
                header = header[0]
        
        self.header = header
        self.display_header = None
        self.rows = rows
        self.alignment = alignment
    
    @property
    def header(self) -> list[Any]:
        return self.__header
    @header.setter
    def header(self, value: Iterable[Any]):
        if value == None:
            self.__header = []
        else:
            self.__header = list(value)
    
    @property
    def display_header(self):
        header = []
        for cell in zip_longest(self.__display_header[0:len(self.header)], self.header):
            header.append(cell[0] if cell[0] else cell[1])
        self.__display_header = header
        return header
    
    @display_header.setter
    def display_header(self, header: list[str]):
        if header == None:
            self.__display_header = []
        else:
            self.__display_header = list(header)
    
    @property
    def rows(self) -> list[list[Any]]:
        rows: list[list[Any]] = []
        
        header_length = len(self.header)
        
        for row in self.__rows:
            row = list(row)
            
            if len(row) > header_length:
                row = row[0:header_length]
            elif len(row) < header_length:
                for i in range(header_length - len(row)):
                    row.append('')
            
            rows.append(row)
        
        self.__rows = rows
        return self.__rows
    @rows.setter
    def rows(self, value):
        if value == None:
            value = []
        self.__rows: list[list[Any]] = [list(x) for x in value]
    
    @property
    def alignment(self) -> list[Literal[ALIGNMENT.LEFT, ALIGNMENT.CENTER, ALIGNMENT.RIGHT]]:
        header_length = len(self.header)
        alignment: list[Literal[ALIGNMENT.LEFT, ALIGNMENT.CENTER, ALIGNMENT.RIGHT]] = self.__alignment

        if not isinstance(alignment, (list, tuple)):
            alignment = [alignment]
        
        if len(alignment) > header_length:
            alignment = alignment[0:header_length]
        elif len(alignment) < header_length:
            base_alignment = ALIGNMENT.LEFT
            if len(alignment) > 0:
                base_alignment = alignment[-1]
            
            for i in range(header_length - len(alignment)):
                alignment.append(base_alignment)
        
        for column in range(len(alignment)):
            alignment[column] = str(alignment[column]).lower()

            if alignment[column] in ALIGNMENT_SHORT:
                alignment[column] = {
                    ALIGNMENT_SHORT.LEFT: ALIGNMENT.LEFT,
                    ALIGNMENT_SHORT.CENTER: ALIGNMENT.CENTER,
                    ALIGNMENT_SHORT.RIGHT: ALIGNMENT.RIGHT,
                }[alignment[column]]
            
            if alignment[column] not in ALIGNMENT:
                alignment[column] = ALIGNMENT.LEFT
            
        
        self.alignment = alignment
        return alignment
    
    @alignment.setter
    def alignment(self, value):
        self.__alignment = value
    
    def as_dict(self):
        return [{self.header[index]: cell for index, cell in enumerate(row)} for row in self.rows]
        
    def sort(self, keys: list[str | tuple[str, bool]]):
        key_items = []
        
        for value in keys:
            key = value
            reverse = False
            if isinstance(value, (list, tuple)):
                key = value[0]
                if len(value) > 1:
                    reverse = value[1]

            if not key in self.header:
                raise KeyError(f'key "{key}" is not in header')
            
            key_items.append((self.header.index(key), reverse))
        
        for sort_value in key_items:
            self.rows.sort(key = operator.itemgetter(sort_value[0]), reverse = sort_value[1])
    
    def filter(self, keys: dict[str, str | re.Pattern]):
        rules = []
        
        for key, item in keys.items():
            if not key in self.header:
                raise KeyError(f'key "{key}" is not in header')
            
            rules.append((self.header.index(key), item))
        
        def keep(row: list[str]):
            for index, pattern in rules:
                if not isinstance(pattern, re.Pattern):
                    pattern = re.compile(pattern)
                    
                if not pattern.match(row[index]):
                    return False
                elif row[index] != pattern.pattern:
                    return False
            
            return True
        
        if len(rules):
            self.rows = filter(lambda row: keep(row), self.rows)
    
    def set_header_order(self, new_header: list[str] | dict[str, str]):
        if isinstance(new_header, (list, tuple)):
            new_header = {cell: cell for cell in new_header}

        new_rows = [[row[self.header.index(name)] if name in self.header else '' for name in new_header] for row in self.rows]
        
        self.header = new_header.items()
        self.display_header = new_header.values()
        self.rows = new_rows
    
    def _create_row(self, row: list, lengths: list[int], alignment: list[Literal[ALIGNMENT.LEFT, ALIGNMENT.CENTER, ALIGNMENT.RIGHT]], pad_char: str = " "):
        padding_directions = {
            ALIGNMENT.LEFT: '<',
            ALIGNMENT.CENTER: '^',
            ALIGNMENT.RIGHT: '>',
        }
        
        result = []
        
        for row_index in range(len(row)):
            result.append(f"{pad_char}{str(row[row_index]):{pad_char}{padding_directions.get(alignment[row_index], '<')}{lengths[row_index]}}{pad_char}")
        
        return result
    
    def _create_under_header_row(self, lengths: list[int], alignment: list[Literal[ALIGNMENT.LEFT, ALIGNMENT.CENTER, ALIGNMENT.RIGHT]], pad_char: str = "-"):
        padding_sides = {
            ALIGNMENT.LEFT: (':', '-'),
            ALIGNMENT.CENTER: (':', ':'),
            ALIGNMENT.RIGHT: ('-', ':'),
        }
        
        left_aligned = (len(filtered_alignment := set(alignment)) == 1 and str(ALIGNMENT.LEFT) in filtered_alignment) or len(filtered_alignment) <= 0
        
        result = []
        
        for row_index in range(len(lengths)):
            if left_aligned:
                sides = ['-', '-']
            else:
                sides = padding_sides.get(alignment[row_index], ('-', '-'))
            
            result.append(f"{sides[0]}{pad_char * lengths[row_index]}{sides[1]}")
        
        return result
    
    def write(self) -> str:
        table = []
        
        text = ""
        
        header = [escape(str(cell).replace('\n', '<br>'), '|') for cell in self.header]
        display_header = [escape(cell).replace('\n', '<br>') for cell in self.display_header]
        rows = [[escape(str(cell).replace('\n', '<br>'), '|') for cell in row] for row in self.rows]
        column_lengths = [max([len(escape(cell, '|')) for cell in column]) for column in zip(display_header, *rows)]
        
        table.append(self._create_row(display_header, column_lengths, self.alignment))
        table.append(self._create_under_header_row(column_lengths, self.alignment))
        for row in rows:
            table.append(self._create_row(row, column_lengths, self.alignment))
        
        text = '\n'.join([f"|{'|'.join(r)}|" for r in table])
        
        return text
    
    @classmethod
    def from_csv(cls, csv_file: str | IO) -> "Table":
        table = csv_tools.load_csv(csv_file)

        return Table(table[0], table[1::])
    
    @classmethod
    def table_from_dict(cls, table: list[dict]):
        header = list(set(itertools.chain(*[row.keys() for row in table])))
        
        rows = []
        
        for row in table:
            rows.append([row.get(col, '') for col in header])
        
        return header, rows
    
    @classmethod
    def from_dict(cls, table: list[dict]):
        header, rows = cls.table_from_dict(table)
        
        return Table(header, rows)

    def __format__(self, format_spec: str) -> str:
        formatted_table = deepcopy(self)
        
        split_spec = parse_format_spec(format_spec)
        for part in split_spec:
            if isinstance(part, tuple):
                if part[0] == 'sort':
                    sort_order = []
                    if isinstance(part[1], str):
                        sort_order.append((part[1], False))
                    elif isinstance(part[1], list):
                        for key in part[1]:
                            reverse = False
                            if isinstance(key, str):
                                if key[-1] in ['<', '>', '=']:
                                    reverse = key[-1] == '>'
                                    key = key[:-1]
                            elif isinstance(key, list):
                                if len(key) > 1:
                                    if key[1] == '>':
                                        reverse = True
                                    else:
                                        reverse = strbool(key[1])
                            
                            sort_order.append((key, reverse))

                    formatted_table.sort(sort_order)
                
                elif part[0] == 'filter':
                    filter_rules = {}
                    if isinstance(part[1], list):
                        for rule in part[1]:
                            if isinstance(rule[0], list):
                                rule[0] = '='.join(rule[0])
                            if isinstance(rule, list):
                                filter_rules[rule[0]] = rule[1]
                    
                    formatted_table.filter(filter_rules)
                
                elif part[0] == 'order':
                    order = {}
                    if isinstance(part[1], str):
                        order[part[1]] = part[1]
                    elif isinstance(part[1], list):
                        for cell in part[1]:
                            if isinstance(cell, str):
                                order[cell] = cell
                            elif isinstance(cell, list):
                                if len(cell) == 1:
                                    order[cell[0]] = cell[0]
                                if len(cell) > 1:
                                    order[cell[0]] = cell[1]
                    
                    formatted_table.set_header_order(order)
                
                elif part[0] == 'align':
                    align = formatted_table.alignment
                    
                    if isinstance(part[1], str):
                        alignment = part[1].lower()
                        if alignment in ALIGNMENT:
                            align = [alignment]
                        else:
                            align = list(alignment)
                    elif isinstance(part[1], list):
                        index = 0
                        for cell in part[1]:
                            if isinstance(cell, list):
                                if cell[0] in formatted_table.header:
                                    index = formatted_table.header.index(cell[0])
                                    align[index] = cell[1]
                            else:
                                if index < len(align):
                                    align[index] = cell
                            
                            index += 1
                    formatted_table.alignment = align
                    
        return str(formatted_table)
