import sys
import argparse
import struct
import os
import json

class Assembler:
    def __init__(self, json_config_file):
        self.instructions = {}
        self.registers = {}
        self.labels = {}
        self.data_labels = {}  # Data labels with their addresses and values
        self.defines = {}
        self.text_segment = []  # Instructions go here
        self.data_segment = []  # Separate segment for data
        self.current_address = 0
        self.load_json_config(json_config_file)

    def load_json_config(self, json_config_file):
        """
        Load the configuration from a JSON file and initialize instructions and registers.
        """
        try:
            with open(json_config_file, 'r') as file:
                data = json.load(file)
                self.registers = data.get('registers', {})
                for instr in data.get('instructions', []):
                    mnemonic = instr['mnemonic']
                    self.instructions[mnemonic] = instr
        except FileNotFoundError:
            print(f"Error: Configuration file '{json_config_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: JSON configuration file is malformed.")
            sys.exit(1)

    def preprocess(self, lines):
        """
        Preprocess the assembly code to handle directives and macros.
        """
        preprocessed_lines = []
        include_stack = []
        processing = True
        condition_stack = []

        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments

            if not line:l
                continue

            # Handle #include directive
            if line.startswith('#include'):
                file_to_include = line.split()[1].strip('"')
                if not os.path.isfile(file_to_include):
                    print(f"Error: Included file '{file_to_include}' not found.")
                    sys.exit(1)
                with open(file_to_include, 'r') as f:
                    include_stack.extend(f.readlines())
                continue

            # Handle conditional directives
            if line.startswith('.ifdef'):
                _, macro = line.split()
                condition_stack.append(macro in self.defines)
                processing = processing and (macro in self.defines)
                continue

            if line.startswith('.ifndef'):
                _, macro = line.split()
                condition_stack.append(macro not in self.defines)
                processing = processing and (macro not in self.defines)
                continue

            if line.startswith('.else'):
                if not condition_stack:
                    print("Error: '.else' without matching '.ifdef' or '.ifndef'")
                    sys.exit(1)
                processing = not condition_stack[-1]
                continue

            if line.startswith('.endif'):
                if not condition_stack:
                    print("Error: '.endif' without matching '.ifdef' or '.ifndef'")
                    sys.exit(1)
                condition_stack.pop()
                processing = True
                continue

            if not processing:
                continue

            # Handle .define directive
            if line.startswith('.define'):
                _, key, value = line.split()
                self.defines[key] = value
                continue

            # Handle .org directive
            if line.startswith('.org'):
                _, address = line.split()
                self.current_address = int(address, 16)
                continue

            # Substitute defines
            for key, value in self.defines.items():
                line = line.replace(key, value)

            preprocessed_lines.append(line)

        if include_stack:
            preprocessed_lines = include_stack + preprocessed_lines

        return preprocessed_lines

    def parse_line_first_pass(self, line):
        """
        First pass of parsing to collect labels and calculate addresses.
        """
        parts = line.strip().split()
        if not parts:
            return

        # Handle data label definitions
        if parts[0].endswith(':') and len(parts) > 1 and parts[1] == ".data":
            label = parts[0][:-1]
            value = parts[2] if len(parts) > 2 else "0"
            self.data_labels[label] = (self.current_address, value)
            self.current_address += len(value)  # Assuming 1 byte per value character
            self.data_segment.append((label, value))
            return

        # Handle code labels
        if parts[0].endswith(':'):
            label = parts[0][:-1]
            self.labels[label] = self.current_address
            return

        # Handle instructions
        if parts[0].upper() in self.instructions:
            mnemonic = parts[0].upper()
            instr_info = self.instructions[mnemonic]
            self.current_address += sum(instr_info['field_sizes'].values()) // 8

    def first_pass(self, lines):
        """
        First pass to identify labels and calculate addresses.
        """
        self.current_address = 0
        for line in lines:
            self.parse_line_first_pass(line)

    def parse_line_second_pass(self, line):
        """
        Second pass of parsing to generate machine code.
        """
        parts = line.strip().split()
        if not parts or parts[0].endswith(':'):
            return
        mnemonic = parts[0].upper()
        if mnemonic in self.instructions:
            instr_info = self.instructions[mnemonic]
            opcode = instr_info['opcode']
            operands = parts[1:]
            if len(operands) != instr_info['operand_count']:
                print(f"Error: Incorrect number of operands for {mnemonic}. Expected {instr_info['operand_count']}, got {len(operands)}.")
                return

            # Convert operands to bitwise representation
            operand_bits = []
            for i, operand in enumerate(operands):
                operand_type = instr_info['operand_types'][i]
                field_name = f"r{i+1}"
                if operand_type == 'register':
                    if operand in self.registers:
                        operand_bits.append(self.registers[operand])
                    else:
                        print(f"Error: Unknown register {operand}")
                        return
                elif operand_type == 'immediate':
                    imm_size = instr_info['field_sizes'].get(field_name, 8)
                    operand_bits.append(format(int(operand), f'0{imm_size}b'))
                elif operand_type == 'memory':
                    mem_size = instr_info['field_sizes'].get(field_name, 16)
                    operand_bits.append(format(int(operand), f'0{mem_size}b'))
                elif operand_type == 'address':
                    addr_size = instr_info['field_sizes'].get(field_name, 16)
                    if operand in self.labels:
                        address = self.labels[operand]
                        operand_bits.append(format(address, f'0{addr_size}b'))
                    elif operand in self.data_labels:
                        address = self.data_labels[operand][0]
                        operand_bits.append(format(address, f'0{addr_size}b'))
                    else:
                        print(f"Error: Undefined label {operand}")
                        return
                elif operand_type == 'port':
                    port_size = instr_info['field_sizes'].get(field_name, 8)
                    operand_bits.append(format(int(operand), f'0{port_size}b'))
                elif operand_type == 'interrupt':
                    int_size = instr_info['field_sizes'].get(field_name, 8)
                    operand_bits.append(format(int(operand), f'0{int_size}b'))
                else:
                    print(f"Error: Unsupported operand type {operand_type}")
                    return

            # Construct the instruction
            bitwise_instr = instr_info['bitwise_description']['opcode'] + ''.join(operand_bits)
            self.text_segment.append(bitwise_instr)

    def second_pass(self, lines):
        """
        Second pass to generate machine code from parsed instructions.
        """
        self.text_segment = []
        self.current_address = 0
        for line in lines:
            self.parse_line_second_pass(line)

    def assemble(self, input_file):
        """
        Assemble the input assembly code file into machine code.
        """
        try:
            with open(input_file, 'r') as file:
                lines = file.readlines()
            preprocessed_lines = self.preprocess(lines)
            self.first_pass(preprocessed_lines)
            self.second_pass(preprocessed_lines)
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)

    def write_output(self, output_file):
        """
        Write the assembled machine code to the output binary file.
        """
        try:
            with open(output_file, 'wb') as file:
                # Write data segment first
                for label, value in self.data_segment:
                    # Assume values are string bytes; modify this as needed for your data format
                    file.write(value.encode('utf-8'))  # Fixed the encoding

                # Write text segment
                for instruction in self.text_segment:
                    # Write each instruction as bytes
                    packed_instruction = int(instruction, 2).to_bytes((len(instruction) + 7) // 8, byteorder='big')
                    file.write(packed_instruction)
        except IOError as e:
            print(f"Error: Unable to write to output file '{output_file}'. {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Assemble code into machine language.')
    parser.add_argument('input_file', type=str, help='The input assembly file')
    parser.add_argument('output_file', type=str, help='The output machine code file')
    parser.add_argument('json_config_file', type=str, help='The JSON configuration file for the ISA')
    
    args = parser.parse_args()
    
    assembler = Assembler(args.json_config_file)
    assembler.assemble(args.input_file)
    assembler.write_output(args.output_file)

if __name__ == '__main__':
    main()
