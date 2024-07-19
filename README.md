# Web-Based Pascal Compiler and CPU Emulator

This project provides a web-based interface for a custom Pascal compiler and CPU emulator. It includes a graphical user interface for writing, saving, and compiling Pascal and assembly programs, as well as features for multi-user support, program storage, and CPU description access.

## Features

- **Graphical User Interface**: Write, edit, and save Pascal and assembly programs.
- **Compilation and Emulation**: Compile Pascal programs and emulate the custom CPU.
- **Multi-User Support**: Users can create accounts, login, and manage their own programs.
- **Program Storage**: Securely store user programs with encryption.
- **CPU Description Access**: Easy access to the custom CPU documentation and resources.

## Directory Structure
## Files and Directories



## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Additional dependencies listed in `requirements.txt`

### Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd web_emulator
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the Flask application:
    ```sh
    python app.py
    ```

4. Open your web browser and go to `http://127.0.0.1:5000/` to access the web interface.

## Usage

1. **Register**: Create a new user account.
2. **Login**: Log in with your user account.
3. **Write Program**: Use the editor to write Pascal or assembly code.
4. **Save Program**: Save your code securely.
5. **Compile**: Compile Pascal code into assembly.
6. **Emulate**: Run the assembly code on the custom CPU emulator.

## Development

### Adding Features

The project is designed to be extensible. You can add new features by modifying the Flask application, adding new routes, or extending the compiler and emulator functionality.

### Frontend Customization

The frontend is built using HTML, CSS, and JavaScript. You can customize the look and feel by editing the files in the `static` and `templates` directories.

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.


# Core functionalit.

# CPU emulator

python cpu.py <memory_dump_file> --image_file <File_with_fat16_image> --start_address <start_address>  --interrupt_file <File_with_interrupt_handlers>

# Custom Assembler for a Hypothetical CPU
This is a custom assembler for a hypothetical CPU. It supports a wide range of instructions, data directives, and preprocessor directives. The assembler takes one or more assembly files as input and produces a hex file as output.

## Features:
    Instructions:               Supports various arithmetic, logic, data transfer, and control flow instructions.
    Data Directives:            Supports defining bytes (db), words (dw), double words (dd), and floats (df).
    Preprocessor Directives:    Supports #define, #include, #ifdef, #ifndef, and #endif.
    Labels:                     Supports labels for defining and referencing addresses in the code.

## Usage

Command Line
To use the assembler, run the following command:

python assembler.py <input_files> <output_file>

<input_files>: One or more assembly files to be assembled.
<output_file>: The output file to store the hex representation of the assembled code.

## Assembly Language Syntax
### Instructions
The assembler supports the following instructions:

-   ADD, SUB, MUL, DIV, LOAD, STORE, CMP, JUMP, JZ, JNZ, HALT
-   FADD, FSUB, FMUL, FDIV, LOADF, STORE, CALL, RET
-   PIM_ADD, PIM_SUB, PIM_MUL, PIM_DIV, PIM_FADD, PIM_FSUB, PIM_FMUL, PIM_FDIV
-   INT, IRET, IN, OUT
### Data Directives
-   db: Define bytes.
-   dw: Define words (2 bytes).
-   dd: Define double words (4 bytes).
-   df: Define floats (4 bytes).
### Preprocessor Directives
-   #define: Define a constant.
-   #include: Include another assembly file.
-   #ifdef: Compile the following lines if the macro is defined.
-   #ifndef: Compile the following lines if the macro is not defined.
-   #endif: End of #ifdef or #ifndef.
### Labels
Labels are used to define and reference addresses in the code.

start:
    LOAD R0, count
    JUMP end

end:
    HALT
    
# FAT16 Image Creator

This Python program creates a FAT16 image containing specified input files and an optional bootloader written to the first sector.

## Requirements

- Python 3.x
- `pyfatfs` library

## Installation

1. Install Python 3.x if not already installed.
2. Install the `pyfatfs` library using pip:

    ```sh
    pip install pyfatfs
    ```

## Usage

Run the script from the command line, providing the files to include in the FAT16 image and the output image file. Optionally, specify a bootloader file to be written to the first sector.

```sh
python image_create.py <input_files> -o <output_image> [-b <bootloader>]


