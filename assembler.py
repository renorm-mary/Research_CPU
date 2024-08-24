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
        self.defines = {}
        self.text_segment = []
        self.static_segment = []
        self.heap_segment = []
        self.stack_segment = []
        self.interrupt_handlers = []
        self.current_segment = self.text_segment
        self.current_address = 0
        self.load_json_config(json_config_file)
        self.data_type_directives = {"db", "dw", "dd"}
        
    def load_json_config(self, json_config_file):
        """
        Load the configuration from a JSON file and initialize instructions and registers.
        """
        try:
            with open(json_config_file, 'r') as file:
                data = json.load(file)
                # Registers should be read with '%' prefix in the JSON itself.
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
        offsets = []
        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments

            if not line:
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
            #if line.startswith('.org'):
            #    _, address = line.split()
            #    print("org addr",address)
            #    self.current_address = int(address, 16)
            #    print(self.current_address)
            #    continue

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
        print(self.current_address)
        parts = line.strip().split()
        if not parts:
            return

        # Handle label definitions
        if parts[0].endswith(':'):
            label = parts[0][:-1]
            self.labels[label] = self.current_address
            print(f"Label '{label}' defined at address {self.current_address}")
            return

        # Handle data label definitions
        if len(parts) > 1 and (parts[0] in self.data_type_directives or parts[0] == ".org"):
            if parts[0].startswith('.org'):
                self.current_address = int(parts[1], 16) * 16
                print(f"Setting address to {self.current_address:04X}")
                return
            else:
                print("data", parts)
                label = parts[0]
                #data_type = parts[1][1:]  # Remove the dot from the data type
                value = parts[1]
                self.labels[label] = (self.current_address, value)
                self.static_segment.append((label, value, self.current_address))
                if label == "db":
                    self.current_address += 4
                elif label == "dw":
                    self.current_address += 4
                elif label == "dd":
                    self.current_address += 4
                
                print(f"Data label '{label}' defined at address {self.current_address}")
                print(f"Value: {value}")
                return

        # Handle instructions
        if parts[0].upper() in self.instructions:
            mnemonic = parts[0].upper()
            instr_info = self.instructions[mnemonic]
            self.current_address += sum(instr_info['field_sizes'].values()) // 8
            print(f"Instruction '{mnemonic}' parsed at address {self.current_address}")
            return

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
        if line.startswith('.org'):
            self.current_address = int(line.split()[1], 16) * 16
            print(f"Setting address to {self.current_address:04X}")
        else:
            print("parts", parts)
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
                addr_bits = []
                #print(self.registers)
                print(operands)
                print(instr_info)
                for i, operand in enumerate(operands):
                    operand = operand.replace(",","")
                    operand_type = instr_info['operand_types'][i]
                    field_name = f"r{i+1}"
                    if operand_type == 'register':
                        operand = operand[1:].replace(",","")
                        #print(self.registers) 
                        if operand in self.registers:
                            operand_bits.append(self.registers[operand])
                        else:
                            print(f"Error: Unknown register {operand}")
                            return
                    elif operand_type == 'immediate':
                        imm_size = instr_info['field_sizes'].get(field_name, 8)
                        if len(operand) == 3 and operand[0] == "'" and operand[2] == "'":
                            operand = ord(operand[1])
                            operand_bits.append(format(operand, f'0{imm_size}b'))
                        elif operand.startswith('0x'):
                            operand_bits.append(format(int(operand, 16), f'0{imm_size}b'))
                        else:
                            operand_bits.append(format(int(operand), f'0{imm_size}b'))

                    elif operand_type == 'memory':
                        mem_size = instr_info['field_sizes'].get(field_name, 16)
                        if operand in self.labels:
                            mem_addr = self.labels[operand]
                            operand_bits.append(format(mem_addr, f'0{mem_size}b'))
                        elif operand.isdigit():
                            operand_bits.append(format(int(operand), f'0{mem_size}b'))
                        else:
                            print(f"Error: Undefined label {operand}")
                            return
                    elif operand_type == 'address':
                        addr_size = instr_info['field_sizes'].get(field_name, 16)
                        if operand in self.labels:
                            address = self.labels[operand]
                            operand_bits.append(format(address, f'0{addr_size}b'))
                        else:
                            print(f"Error: Undefined label {operand}")
                            return
                    elif operand_type == 'port':
                        port_size = instr_info['field_sizes'].get(field_name, 8)
                        if operand.startswith('0x'):
                            operand_bits.append(format(int(operand, 16), f'0{port_size}b'))
                        else:
                            operand_bits.append(format(int(operand), f'0{port_size}b'))
                    elif operand_type == 'interrupt':
                        int_size = instr_info['field_sizes'].get(field_name, 8)
                        if operand.startswith('0x'):
                            operand_bits.append(format(int(operand, 16), f'0{int_size}b'))
                        else:
                            operand_bits.append(format(int(operand), f'0{int_size}b'))
                    else:
                        print(f"Error: Unsupported operand type {operand_type}")
                        return

                # Construct the instruction
                bitwise_instr = instr_info['bitwise_description']['opcode'] + ''.join(operand_bits)
                bitwise_addr = format(self.current_address, '032b')
                self.current_address += 4
                bitwise_instr = bitwise_instr.zfill(32)
                self.text_segment.append((bitwise_instr, bitwise_addr))

    def second_pass(self, lines):
        """
        Second pass to generate machine code from parsed instructions.
        """
        self.text_segment = []
        self.current_address = 0
        for line in lines:
            print("second pass line", line)
            self.parse_line_second_pass(line)
            #if line.startswith('.org'):
            #    self.current_address = int(line.split()[1], 16) * 16
            #    print(f"Setting address to {self.current_address:04X}")
            #    continue
            #else:
            #    self.parse_line_second_pass(line)
            #    self.current_address += 4

    def assemble(self, input_file):
        """
        Assemble the input assembly code file into machine code.
        """
        try:
            with open(input_file, 'r') as file:
                lines = file.readlines()
            preprocessed_lines = self.preprocess(lines)
            print("preprocessed_lines", preprocessed_lines)
            self.first_pass(preprocessed_lines)
            print("preprocessed_lines", preprocessed_lines)
            self.second_pass(preprocessed_lines)
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)



    def write_output(self, output_file):
        """
        Write the assembled machine code to the output text file with addresses and data in hex format.
        """
        try:
            with open(output_file, 'w') as file:
                # Reset current address
                self.current_address = 0

                # Write text segment
                for item in self.text_segment:
                    if isinstance(item, tuple) and item[0] == '.org':
                        # Set current address to the value specified by .org directive
                        self.current_address = int(item[1], 16) * 16
                        print(".ORG", self.current_address)
                        print(f"Setting address to {self.current_address:04X}")
                    else:
                        # Write address and instruction in hex format
                        hex_instruction = hex(int(item[0], 2))[2:].zfill(8)
                        hex_address = hex(int(item[1], 2))[2:].zfill(8)
                        file.write(f"{hex_address}: {hex_instruction}\n")
                        self.current_address += 4
                        print(f"Text segment: {hex_address}: {hex_instruction}")

                # Write data segment
                for item in self.static_segment:
                    if isinstance(item, tuple) and item[0] == '.org':
                        # Set current address to the value specified by .org directive
                        self.current_address = int(item[1], 16)  * 16
                    else:
                        print("item", item)
                        label, value, address = item
                        # Write address and data in hex format
                        hex_value = hex(int(value, 16))[2:].zfill(8)
                        hex_address = hex(address)[2:].zfill(8)
                        print("hex_value", hex_value)
                        file.write(f"{hex_address}: {hex_value}\n")
                        self.current_address += len(hex_value) // 2
                        print(f"Data segment: {hex_address}: {hex_value}")
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
    print("write")
    assembler.write_output(args.output_file)

if __name__ == '__main__':
    main()
