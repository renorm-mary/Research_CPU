from lexer import lexer
from parser import parse
from typing import List, Dict

def compile_pascal_code(source_code: str) -> List[Dict[str, str]]:
    """
    Compiles the given Pascal source code into an AST.

    :param source_code: The Pascal source code as a string.
    :return: The AST as a list of dictionaries.
    """
    tokens = lexer(source_code)
    ast = parse(tokens)
    return ast

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Compile Pascal source code.')
    parser.add_argument('source_file', type=str, help='The Pascal source code file to compile.')
    args = parser.parse_args()

    with open(args.source_file, 'r') as file:
        source_code = file.read()
    
    ast = compile_pascal_code(source_code)
    print(ast)
