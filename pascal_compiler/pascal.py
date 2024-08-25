import argparse
import json
from typing import Dict, Any
from lexer import tokenize
from pascal_parser import parse, ASTNode  # Assuming you renamed parser.py to pascal_parser.py
from semantic_analyzer import analyze, CompilerError

def compile_pascal_code(source_code: str) -> Dict[str, Any]:
    """
    Compiles the given Pascal source code into an AST and performs semantic analysis.

    :param source_code: The Pascal source code as a string.
    :return: The AST as a dictionary.
    """
    try:
        tokens = tokenize(source_code)
        ast = parse(tokens)
        analyze(ast)
        return ast_to_dict(ast)
    except CompilerError as e:
        return {"error": str(e)}

def ast_to_dict(node: Any) -> Dict[str, Any]:
    """
    Converts an AST node to a dictionary representation.
    """
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif not isinstance(node, ASTNode):
        return node

    result = {'type': type(node).__name__}
    for attr, value in vars(node).items():
        if attr == 'token':
            result[attr] = {'type': value.type, 'value': value.value}
        else:
            result[attr] = ast_to_dict(value)
    return result

def main():
    parser = argparse.ArgumentParser(description='Compile Pascal source code.')
    parser.add_argument('source_file', type=str, help='The Pascal source code file to compile.')
    parser.add_argument('-o', '--output', type=str, help='Output file for the AST (default: stdout)')
    args = parser.parse_args()

    try:
        with open(args.source_file, 'r') as file:
            source_code = file.read()
    except IOError as e:
        print(f"Error reading source file: {e}")
        return

    result = compile_pascal_code(source_code)
    
    if "error" in result:
        print(f"Compilation error: {result['error']}")
    else:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"AST written to {args.output}")
        else:
            print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()