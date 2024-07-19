# Pascal Compiler

This is a simple Pascal compiler implemented in Python. The compiler includes a lexer, parser, and a main script to compile Pascal source files for a custom CPU.

## Directory Structure

```
pascal_compiler/
    lexer.py
    parser.py
main.py
README.md
```

## Files

- **lexer.py**: Tokenizes the Pascal source code.
- **parser.py**: Parses the tokens into an Abstract Syntax Tree (AST).
- **main.py**: Main script to compile Pascal source files.
- **README.md**: This file.

## Usage

To use the compiler, run the `main.py` script with the Pascal source file as an argument:

```sh
python main.py <source_file>
```

### Example

```sh
python main.py example.pas
```

This will tokenize, parse, and compile the provided Pascal source file.

## Installation

Ensure you have Python installed. Clone the repository and navigate to the directory:

```sh
git clone <repository-url>
cd pascal_compiler
```

Run the compiler with your Pascal source file.

## Development

The compiler is designed to be extended. You can add more features and improve the existing ones by modifying the lexer and parser.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Contributions are welcome!

## License

This project is licensed under the MIT License. See the LICENSE file for details.
