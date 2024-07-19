import sys
import os
from lexer import tokenize
from parser import Parser

def main(source_file):
    if not os.path.isfile(source_file):
        print(f"File not found: {source_file}")
        return

    with open(source_file, 'r') as file:
        code = file.read()

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        print("Compilation successful!")
        # Here, you would typically have additional steps to generate the target code
        # from the AST and perform any further processing required.
    except RuntimeError as e:
        print(f"Compilation error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file>")
    else:
        main(sys.argv[1])
