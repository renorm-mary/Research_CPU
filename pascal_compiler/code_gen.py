import json
import sys
import argparse

class Translator:
    def __init__(self, ast, isa):
        self.ast = ast
        self.isa = isa
        self.instructions = []
        self.label_counter = 0
        self.variable_map = {}
        self.current_offset = 0

    def generate_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def allocate_variable(self, var_name):
        if var_name not in self.variable_map:
            self.variable_map[var_name] = self.current_offset
            self.current_offset += 4  # Assuming 4-byte alignment for simplicity

    def translate(self):
        self.instructions.append(".text")
        self.instructions.append(".globl main")
        self.instructions.append("main:")
        self.instructions.append("    addi sp, sp, -1024")  # Allocate stack frame
        self.visit(self.ast)
        self.instructions.append("    addi sp, sp, 1024")  # Deallocate stack frame
        self.instructions.append("    li a0, 0")  # Return 0
        self.instructions.append("    ret")
        self.instructions.append("")
        self.instructions.append(".data")
        for var, offset in self.variable_map.items():
            self.instructions.append(f"{var}: dw 0")
        return "\n".join(self.instructions)

    def visit(self, node):
        method_name = f"visit_{node['type']}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        print(f"Unhandled node type: {node['type']}")

    def visit_Program(self, node):
        self.visit(node['block'])

    def visit_Block(self, node):
        for decl in node['declarations']:
            self.visit(decl)
        self.visit(node['compound_statement'])

    def visit_VarDecl(self, node):
        var_name = node['var_node']['value']
        self.allocate_variable(var_name)

    def visit_Assign(self, node):
        right_reg = self.visit(node['right'])
        left = node['left']
        if left['type'] == 'Var':
            var_name = left['value']
            self.allocate_variable(var_name)
            offset = self.variable_map[var_name]
            self.instructions.append(f"    sw {right_reg}, {offset}(sp)")
        elif left['type'] == 'BinOp' and left['op']['type'] == 'INDEX':
            array_name = left['left']['value']
            index_reg = self.visit(left['right'])
            self.instructions.append(f"    slli {index_reg}, {index_reg}, 2")
            self.instructions.append(f"    la t0, {array_name}")
            self.instructions.append(f"    add t0, t0, {index_reg}")
            self.instructions.append(f"    sw {right_reg}, 0(t0)")

    def visit_Var(self, node):
        var_name = node['value']
        self.allocate_variable(var_name)
        offset = self.variable_map[var_name]
        dest_reg = self.get_free_register()
        self.instructions.append(f"    lw {dest_reg}, {offset}(sp)")
        return dest_reg

    def visit_Num(self, node):
        dest_reg = self.get_free_register()
        self.instructions.append(f"    li {dest_reg}, {node['value']}")
        return dest_reg

    def visit_String(self, node):
        label = self.generate_label()
        self.instructions.append(f"{label}: .string \"{node['value']}\"")
        dest_reg = self.get_free_register()
        self.instructions.append(f"    la {dest_reg}, {label}")
        return dest_reg

    def visit_Boolean(self, node):
        dest_reg = self.get_free_register()
        value = 1 if node['value'] else 0
        self.instructions.append(f"    li {dest_reg}, {value}")
        return dest_reg

    def visit_BinOp(self, node):
        left_reg = self.visit(node['left'])
        right_reg = self.visit(node['right'])
        dest_reg = self.get_free_register()
        op = node['op']['type']
        if op == 'PLUS':
            self.instructions.append(f"    add {dest_reg}, {left_reg}, {right_reg}")
        elif op == 'MINUS':
            self.instructions.append(f"    sub {dest_reg}, {left_reg}, {right_reg}")
        elif op == 'MUL':
            self.instructions.append(f"    mul {dest_reg}, {left_reg}, {right_reg}")
        elif op == 'DIV':
            self.instructions.append(f"    div {dest_reg}, {left_reg}, {right_reg}")
        elif op in ['EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE']:
            self.instructions.append(f"    sub {dest_reg}, {left_reg}, {right_reg}")
            if op == 'EQ':
                self.instructions.append(f"    seqz {dest_reg}, {dest_reg}")
            elif op == 'NEQ':
                self.instructions.append(f"    snez {dest_reg}, {dest_reg}")
            elif op == 'LT':
                self.instructions.append(f"    sltz {dest_reg}, {dest_reg}")
            elif op == 'LTE':
                self.instructions.append(f"    slez {dest_reg}, {dest_reg}")
            elif op == 'GT':
                self.instructions.append(f"    sgtz {dest_reg}, {dest_reg}")
            elif op == 'GTE':
                self.instructions.append(f"    sltz {dest_reg}, {dest_reg}")
                self.instructions.append(f"    xori {dest_reg}, {dest_reg}, 1")
        return dest_reg

    def visit_UnaryOp(self, node):
        expr_reg = self.visit(node['expr'])
        op = node['op']['type']
        if op == 'PLUS':
            return expr_reg
        elif op == 'MINUS':
            dest_reg = self.get_free_register()
            self.instructions.append(f"    neg {dest_reg}, {expr_reg}")
            return dest_reg

    def visit_CompoundStatement(self, node):
        for statement in node['statements']:
            self.visit(statement)

    def visit_If(self, node):
        condition_reg = self.visit(node['condition'])
        else_label = self.generate_label()
        end_label = self.generate_label()
        
        self.instructions.append(f"    beqz {condition_reg}, {else_label}")
        self.visit(node['then_statement'])
        self.instructions.append(f"    j {end_label}")
        self.instructions.append(f"{else_label}:")
        if node['else_statement']:
            self.visit(node['else_statement'])
        self.instructions.append(f"{end_label}:")

    def visit_While(self, node):
        start_label = self.generate_label()
        end_label = self.generate_label()
        
        self.instructions.append(f"{start_label}:")
        condition_reg = self.visit(node['condition'])
        self.instructions.append(f"    beqz {condition_reg}, {end_label}")
        self.visit(node['statement'])
        self.instructions.append(f"    j {start_label}")
        self.instructions.append(f"{end_label}:")

    def visit_For(self, node):
        start_label = self.generate_label()
        end_label = self.generate_label()
        
        var_name = node['var']['value']
        self.allocate_variable(var_name)
        var_offset = self.variable_map[var_name]
        
        start_reg = self.visit(node['start'])
        end_reg = self.visit(node['end'])
        
        self.instructions.append(f"    sw {start_reg}, {var_offset}(sp)")
        self.instructions.append(f"{start_label}:")
        self.instructions.append(f"    lw t0, {var_offset}(sp)")
        if node['direction'] == 'TO':
            self.instructions.append(f"    bgt t0, {end_reg}, {end_label}")
        else:  # 'DOWNTO'
            self.instructions.append(f"    blt t0, {end_reg}, {end_label}")
        
        self.visit(node['statement'])
        
        self.instructions.append(f"    lw t0, {var_offset}(sp)")
        if node['direction'] == 'TO':
            self.instructions.append(f"    addi t0, t0, 1")
        else:  # 'DOWNTO'
            self.instructions.append(f"    addi t0, t0, -1")
        self.instructions.append(f"    sw t0, {var_offset}(sp)")
        self.instructions.append(f"    j {start_label}")
        self.instructions.append(f"{end_label}:")

    def get_free_register(self):
        # For simplicity, we're using t0-t6 registers. In a real compiler, we'd implement proper register allocation.
        return "t0"

def main():
    parser = argparse.ArgumentParser(description='Translate Pascal AST to RISC-V assembly.')
    parser.add_argument('ast_file', help='Input JSON file containing Pascal AST')
    parser.add_argument('isa_file', help='Input JSON file containing RISC-V ISA')
    parser.add_argument('-o', '--output', help='Output assembly file (default: output.s)', default='output.s')
    args = parser.parse_args()

    try:
        with open(args.ast_file, 'r') as f:
            ast = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing {args.ast_file}: {e}")
        print(f"Error occurred at line {e.lineno}, column {e.colno}")
        return
    except FileNotFoundError:
        print(f"{args.ast_file} file not found.")
        return

    try:
        with open(args.isa_file, 'r') as f:
            isa_content = f.read()
            try:
                isa = json.loads(isa_content)
            except json.JSONDecodeError as e:
                print(f"Error parsing {args.isa_file}: {e}")
                print(f"Error occurred at line {e.lineno}, column {e.colno}")
                print("Content near error:")
                lines = isa_content.splitlines()
                start = max(0, e.lineno - 2)
                end = min(len(lines), e.lineno + 2)
                for i in range(start, end):
                    print(f"{i+1}: {lines[i]}")
                return
    except FileNotFoundError:
        print(f"{args.isa_file} file not found.")
        return

    translator = Translator(ast, isa)
    assembly_code = translator.translate()
    
    try:
        with open(args.output, 'w') as f:
            f.write(assembly_code)
        print(f"Assembly code has been written to {args.output}")
    except IOError as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()