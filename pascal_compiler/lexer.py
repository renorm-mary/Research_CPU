import re
from typing import List, Union

class Token:
    def __init__(self, type: str, value: Union[str, int, float], line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})'

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"Lexer error at line {self.line}, column {self.column}: {self.message}"

TOKEN_SPEC = [
    ('REAL',    r'\d+\.\d+'),
    ('INTEGER', r'\d+'),
    ('ASSIGN',  r':='),
    ('SEMICOLON', r';'),
    ('COLON', r':'),
    ('COMMA', r','),
    ('DOT', r'\.'),
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('LTE', r'<='),
    ('GTE', r'>='),
    ('EQ', r'='),
    ('NEQ', r'<>'),
    ('LT', r'<'),
    ('GT', r'>'),
    ('KEYWORD', r'\b(AND|ARRAY|BEGIN|CASE|CONST|DIV|DO|DOWNTO|ELSE|END|FILE|FOR|FUNCTION|GOTO|IF|IN|LABEL|MOD|NIL|NOT|OF|OR|PACKED|PROCEDURE|PROGRAM|RECORD|REPEAT|SET|THEN|TO|TYPE|UNTIL|VAR|WHILE|WITH)\b'),
    ('BOOLEAN', r'\b(TRUE|FALSE)\b'),
    ('STRING',  r"'[^']*'"),
    ('ID',      r'\b[A-Za-z_][A-Za-z0-9_]*\b'),
    ('COMMENT', r'\{[^}]*\}|\(\*.*?\*\)'),
    ('NEWLINE', r'\n'),
    ('SKIP',    r'[ \t]+'),
    ('MISMATCH',r'.'),
]

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens = []
        self.current_line = 1
        self.current_column = 1

    def tokenize(self) -> List[Token]:
        position = 0
        while position < len(self.code):
            match = None
            for token_type, pattern in TOKEN_SPEC:
                regex = re.compile(pattern)
                match = regex.match(self.code, position)
                if match:
                    value = match.group(0)
                    if token_type == 'INTEGER':
                        value = int(value)
                    elif token_type == 'REAL':
                        value = float(value)
                    elif token_type == 'STRING':
                        value = value[1:-1]  # Remove quotes
                    elif token_type == 'KEYWORD':
                        token_type = value.upper()
                    elif token_type == 'BOOLEAN':
                        token_type = 'BOOLEAN'
                    elif token_type in ('COMMENT', 'SKIP'):
                        position = match.end()
                        self.update_position(match.group(0))
                        break
                    elif token_type == 'NEWLINE':
                        self.current_line += 1
                        self.current_column = 1
                        position = match.end()
                        break
                    
                    if token_type != 'SKIP':
                        token = Token(token_type, value, self.current_line, self.current_column)
                        self.tokens.append(token)
                    
                    self.update_position(match.group(0))
                    position = match.end()
                    break
            
            if not match:
                raise LexerError(f'Unexpected character: {self.code[position]}', 
                                 self.current_line, self.current_column)

        return self.tokens

    def update_position(self, value: str):
        lines = value.split('\n')
        if len(lines) > 1:
            self.current_line += len(lines) - 1
            self.current_column = len(lines[-1]) + 1
        else:
            self.current_column += len(value)

def tokenize(code: str) -> List[Token]:
    lexer = Lexer(code)
    return lexer.tokenize()