import re

# Token specification
token_specification = [
    ('NUMBER',  r'\d+(\.\d*)?'),       # Integer or decimal number
    ('ASSIGN',  r':='),                # Assignment operator
    ('END',     r';'),                 # Statement terminator
    ('BEGIN',   r'BEGIN'),             # BEGIN keyword
    ('END',     r'END'),               # END keyword
    ('IF',      r'IF'),                # IF keyword
    ('THEN',    r'THEN'),              # THEN keyword
    ('ELSE',    r'ELSE'),              # ELSE keyword
    ('WHILE',   r'WHILE'),             # WHILE keyword
    ('DO',      r'DO'),                # DO keyword
    ('FOR',     r'FOR'),               # FOR keyword
    ('TO',      r'TO'),                # TO keyword
    ('PROCEDURE', r'PROCEDURE'),       # PROCEDURE keyword
    ('FUNCTION', r'FUNCTION'),         # FUNCTION keyword
    ('VAR',     r'VAR'),               # VAR keyword
    ('ARRAY',   r'ARRAY'),             # ARRAY keyword
    ('OF',      r'OF'),                # OF keyword
    ('STRING',  r'STRING'),            # STRING keyword
    ('TYPE',    r'TYPE'),              # TYPE keyword
    ('INTEGER', r'INTEGER'),           # INTEGER keyword
    ('REAL',    r'REAL'),              # REAL keyword
    ('CHAR',    r'CHAR'),              # CHAR keyword
    ('BOOLEAN', r'BOOLEAN'),           # BOOLEAN keyword
    ('TRUE',    r'TRUE'),              # TRUE keyword
    ('FALSE',   r'FALSE'),             # FALSE keyword
    ('DIRECTIVE', r'\{\$[^}]+\}'),     # Compiler directives
    ('COMMENT', r'\(\*.*?\*\)', re.S), # Multi-line comments
    ('SINGLE_COMMENT', r'\{[^}]*\}'),  # Single-line comments
    ('STRING_LITERAL', r"'[^']*'|\"[^\"]*\""),  # String literals
    ('ID',      r'[A-Za-z_][A-Za-z0-9_]*'),  # Identifiers
    ('OP',      r'[+\-*/<>]'),         # Arithmetic and comparison operators
    ('NEWLINE', r'\n'),                # Line endings
    ('SKIP',    r'[ \t]+'),            # Skip over spaces and tabs
    ('MISMATCH',r'.'),                 # Any other character
]

token_re = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

def tokenize(code):
    tokens = []
    for mo in re.finditer(token_re, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'STRING_LITERAL':
            kind = 'STRING'
        elif kind == 'ID' and value.upper() in ('BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'PROCEDURE', 'FUNCTION', 'VAR', 'ARRAY', 'OF', 'STRING', 'TYPE', 'INTEGER', 'REAL', 'CHAR', 'BOOLEAN', 'TRUE', 'FALSE'):
            kind = value.upper()
        elif kind in ('SKIP', 'COMMENT', 'SINGLE_COMMENT'):
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected')
        tokens.append((kind, value))
    return tokens