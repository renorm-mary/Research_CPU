
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

    def load_json_config(self, json_config_file):
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
        preprocessed_lines = []
        include_stack = []
        processing = True
        condition_stack = []

        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments
            if not line:
                continue
            if line.startswith('#include'):
                file_to_include = line.split()[1].strip('"')
                if not os.path.isfile(file_to_include):
                    print(f"Error: Included file '{file_to_include}' not found.")
                    sys.exit(1)
                with open(file_to_include, 'r') as f:
                    include_stack.extend(f.readlines())
                continue
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
            if line.startswith('.define'):
                _, key, value = line.split()
                self.defines[key] = value
                continue
            if line.startswith('.org'):
                _, address = line.split()
                self.current_address = int(address, 16)
                continue
            for key, value in self.defines.items():
                line = line.replace(key, value)

            preprocessed_lines.append(line)

        if include_stack:
            preprocessed_lines = include_stack + preprocessed_lines

        return preprocessed_lines

    def parse_line_first_pass(self, line):
        parts = line.strip().split()
        if not parts:
            return
        if parts[0].endswith(':') and len(parts) > 1 and parts[1] == ".data":
            label = parts[0][:-1]
            value = parts[2] if len(parts) > 2 else "0"
            self.data_labels[label] = (self.current_address, value)
            self.current_address += len(value)
            self.static_segment.append((label, value))
            return
        if parts[0].endswith(':'):
            label = parts[0][:-1]
            self.labels[label] = self.current_address
            return
        if parts[0].upper() in self.instructions:
            mnemonic = parts[0].upper()
            instr_info = self.instructions[mnemonic]
            self.current_address += sum(instr_info['field_sizes'].values()) // 8
            return

    def first_pass(self, lines):
        self.current_address = 0
        for line in lines:
            self.parse_line_first_pass(line)

    def parse_line_second_pass(self, line):
        parts = line.strip().split()
        if not parts or parts[0].endswith(':'):
            return None
        mnemonic = parts[0].upper()
        if mnemonic in self.instructions:
            instr_info = self.instructions[mnemonic]
            opcode = instr_info['opcode']
            operands = parts[1:]
            if len(operands) != instr_info['operand_count']:
                print(f"Error: Incorrect number of operands for {mnemonic}. Expected {instr_info['operand_count']}, got {len(operands)}.")
                return None

            operand_bits = []
            for i, operand in enumerate(operands):
                operand = operand.replace(",","")
                operand_type = instr_info['operand_types'][i]
                field_name = f"r{i+1}"
                if operand_type == 'register':
                    operand = operand[1:].replace(",","")
                    if operand in self.registers:
                        operand_bits.append(self.registers[operand])
                    else:
                        print(f"Error: Unknown register {operand}")
                        return None
                elif operand_type == 'immediate':
                    imm_size = instr_info['field_sizes'].get(field_name, 8)
                    if len(operand) == 3 and operand.startswith('0x'):
                        operand_bits.append(int(operand, 16))
                    else:
                        operand_bits.append(int(operand))
            # Pack the instruction and operands into binary format (simplified here)
            machine_code = struct.pack('B', int(opcode, 2))
            for operand in operand_bits:
                machine_code += struct.pack('B', operand)
            
            # Returning the address and machine code for printing later
            return self.current_address, machine_code

    def second_pass(self, lines):
        self.current_address = 0
        results = []
        for line in lines:
            result = self.parse_line_second_pass(line)
            if result:
                results.append(result)
                self.current_address += len(result[1])  # Adjusting address based on length of machine code
        return results

    def output_hex_format(self, results):
        print("Address	Data")
        for address, data in results:
            data_hex = ' '.join(f'{byte:02X}' for byte in data)
            print(f'{address:08X}	{data_hex}')

def main():
    # Example usage with command-line arguments
    parser = argparse.ArgumentParser(description="Assembler with HEX output format")
    parser.add_argument("config", help="Path to the JSON configuration file")
    parser.add_argument("input", help="Path to the assembly input file")
    args = parser.parse_args()

    assembler = Assembler(args.config)

    # Example of reading an assembly file, preprocessing, running first and second passes
    with open(args.input, 'r') as f:
        lines = f.readlines()

    preprocessed_lines = assembler.preprocess(lines)
    assembler.first_pass(preprocessed_lines)
    results = assembler.second_pass(preprocessed_lines)

    # Output the results in the required format
    assembler.output_hex_format(results)

if __name__ == "__main__":
    main()
