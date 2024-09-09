import csv
import io
import os
import sys
from typing import IO
from itertools import zip_longest

import charset_normalizer

def load_csv(csv_file: str | IO) -> list[list[str | None]]:
    table = None
    if hasattr(csv_file, 'read'):
        table = list[csv.reader(file)]
    else:
        try:
            csv_file = str(csv_file)
            if os.path.isfile(csv_file):
                encoding = charset_normalizer.from_path(csv_file).best().encoding

                with open(csv_file, 'r', newline = '', encoding = encoding) as file:
                    table = list(csv.reader(file))
            else:
                table = list(csv.reader(io.StringIO(csv_file, newline = '')))
    # else:
        except:
            e = TypeError('input is not a csv')
            e.add_note(str(csv_file))
            raise e
    
    return minify_table(table)

def isnumeric(value: str):
    try:
        float(value)
        return True
    except:
        return False

def align_table(table: list[list[str]], dialect: csv.Dialect = csv.excel):
    columns = []
    
    for column in zip_longest(*table, fillvalue = ''):
        max_length = max([len(cell) for cell in column]) + 1

        columns.append([f'{cell:{['<', '>'][isnumeric(cell)]}{max_length}}' for cell in column])
    
    return list(zip_longest(*columns, fillvalue = ''))

def escape_table(table: list[list[str]], dialect: csv.Dialect = csv.excel):
    return [[escape_cell(cell, dialect) for cell in row] for row in table]

def escape_cell(cell: str, dialect: csv.Dialect = csv.excel):
    quote = False | dialect.quoting == csv.QUOTE_ALL
    
    if dialect.quoting == csv.QUOTE_NONNUMERIC:
        if not isnumeric(cell):
            quote = True
    elif dialect.quoting == csv.QUOTE_STRINGS:
        if not isnumeric(cell):
            quote = True
        elif cell == None:
            quote = False
            cell = ""
    elif dialect.quoting == csv.QUOTE_NOTNULL:
        if cell == None:
            quote = False
            cell = ""
        else:
            quote = True
    
    cell = str(cell)
    if dialect.escapechar and dialect.escapechar in cell:
        cell = cell.replace(dialect.escapechar, dialect.escapechar + dialect.delimiter)
    
    if dialect.delimiter in cell:
        if dialect.quoting == csv.QUOTE_NONE:
            if not dialect.escapechar:
                raise csv.Error('need to escape, but no escapechar set')

            cell = cell.replace(dialect.delimiter, dialect.escapechar + dialect.delimiter)
        else:
            quote = True
    
    if dialect.quotechar in cell:
        if dialect.doublequote:
            cell = cell.replace(dialect.quotechar, dialect.quotechar + dialect.quotechar)
            quote = True
        else:
            if not dialect.escapechar:
                raise csv.Error('need to escape, but no escapechar set')
            
            cell = cell.replace(dialect.quotechar, dialect.escapechar + dialect.quotechar)
    
    if dialect.lineterminator in cell:
        if dialect.quoting == csv.QUOTE_NONE:
            if not dialect.escapechar:
                raise csv.Error('need to escape, but no escapechar set')

            cell = cell.replace(dialect.lineterminator, dialect.escapechar + dialect.lineterminator)
        else:
            quote = True
    
    if quote:
        cell = dialect.quotechar + cell + dialect.quotechar
        
    return cell
    

def minify_table(table: list[list[str]]):
    return [[str(cell).strip() if cell != None else cell for cell in row] for row in table]

def aligned_csv(table: list[list[str]], **kwargs):
    writer = csv.writer(io.StringIO(), **kwargs)
    dialect = writer.dialect
    
    table = align_table(escape_table(minify_table(table)))
    
    rows = []
    
    for row in table:
        rows.append(dialect.delimiter.join([str(cell) for cell in row]).strip())

    return '\n'.join(rows)

if __name__ == "__main__":
    args = sys.argv[1::]

    if len(args) < 1:
        print("usage: align_csv.py <input> <output>")
        exit()
    
    input = args[0]
    output = args[0]
    if len(args) > 1:
        output = args[1]
    
    encoding = charset_normalizer.from_path(input,).best().encoding
    
    with open(input, 'r', newline = '', encoding = encoding) as file:
        table = list(csv.reader(file))
    
    with open(output, 'w', encoding = encoding) as file:
        file.write(aligned_csv(table))
