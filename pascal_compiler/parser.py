
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, blocks):
        self.blocks = blocks

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(ASTNode):
    def __init__(self, value):
        self.value = value

class Str(ASTNode):
    def __init__(self, value):
        self.value = value

class Bool(ASTNode):
    def __init__(self, value):
        self.value = value

class Assign(ASTNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class Var(ASTNode):
    def __init__(self, name):
        self.name = name

class If(ASTNode):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class For(ASTNode):
    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Assembly(ASTNode):
    def __init__(self, instructions):
        self.instructions = instructions

class Procedure(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Function(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

class VarDecl(ASTNode):
    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type

class ArrayDecl(ASTNode):
    def __init__(self, name, element_type, size):
        self.name = name
        self.element_type = element_type
        self.size = size

class StringDecl(ASTNode):
    def __init__(self, name, size):
        self.name = name
        self.size = size

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consume(self, expected_type):
        token_type, token_value = self.tokens[self.pos]
        if token_type == expected_type:
            self.pos += 1
            return token_value
        else:
            raise RuntimeError(f'Expected {expected_type} but got {token_type}')

    def parse(self):
        blocks = []
        while self.pos < len(self.tokens):
            blocks.append(self.block())
        return Program(blocks)

    def block(self):
        statements = []
        self.consume('BEGIN')
        while self.tokens[self.pos][0] != 'END':
            if self.tokens[self.pos][0] == 'IF':
                statements.append(self.if_statement())
            elif self.tokens[self.pos][0] == 'WHILE':
                statements.append(self.while_statement())
            elif self.tokens[self.pos][0] == 'FOR':
                statements.append(self.for_statement())
            elif self.tokens[self.pos][0] == 'PROCEDURE':
                statements.append(self.procedure())
            elif self.tokens[self.pos][0] == 'FUNCTION':
                statements.append(self.function())
            elif self.tokens[self.pos][0] == 'ASM':
                statements.append(self.assembly_block())
            elif self.tokens[self.pos][0] == 'VAR':
                statements.append(self.variable_declaration())
            else:
                statements.append(self.assignment())
        self.consume('END')
        return Block(statements)

    def assignment(self):
        var = self.consume('ID')
        self.consume('ASSIGN')
        expr = self.expr()
        self.consume('END')
        return Assign(var, expr)

    def if_statement(self):
        self.consume('IF')
        condition = self.expr()
        self.consume('THEN')
        true_block = self.block()
        false_block = None
        if self.tokens[self.pos][0] == 'ELSE':
            self.consume('ELSE')
            false_block = self.block()
        return If(condition, true_block, false_block)

    def while_statement(self):
        self.consume('WHILE')
        condition = self.expr()
        self.consume('DO')
        body = self.block()
        return While(condition, body)

    def for_statement(self):
        self.consume('FOR')
        var = self.consume('ID')
        self.consume('ASSIGN')
        start = self.expr()
        self.consume('TO')
        end = self.expr()
        self.consume('DO')
        body = self.block()
        return For(var, start, end, body)

    def assembly_block(self):
        self.consume('ASM')
        instructions = []
        while self.tokens[self.pos][0] != 'ENDASM':
            instructions.append(self.consume('ID'))
        self.consume('ENDASM')
        self.consume('END')
        return Assembly(instructions)

    def procedure(self):
        self.consume('PROCEDURE')
        name = self.consume('ID')
        self.consume('BEGIN')
        params = self.param_list()
        body = self.block()
        return Procedure(name, params, body)

    def function(self):
        self.consume('FUNCTION')
        name = self.consume('ID')
        params = self.param_list()
        return_type = self.consume('ID')
        body = self.block()
        return Function(name, params, return_type, body)
    
    def param_list(self):
        params = []
        while self.tokens[self.pos][0] != 'END':
            param_name = self.consume('ID')
            self.consume('COLON')
            param_type = self.consume('ID')
            params.append((param_name, param_type))
        self.consume('END')
        return params

    def variable_declaration(self):
        self.consume('VAR')
        var_name = self.consume('ID')
        self.consume('COLON')
        var_type = self.consume('ID')
        self.consume('END')
        return VarDecl(var_name, var_type)
    
    def expr(self):
        left = self.term()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] in ('PLUS', 'MINUS'):
            op = self.consume(self.tokens[self.pos][0])
            right = self.term()
            left = BinOp(left, op, right)
        return left
    
    def term(self):
        left = self.factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] in ('MUL', 'DIV'):
            op = self.consume(self.tokens[self.pos][0])
            right = self.factor()
            left = BinOp(left, op, right)
        return left
    
    def factor(self):
        token_type, token_value = self.tokens[self.pos]
        if token_type == 'NUMBER':
            self.pos += 1
            return Num(token_value)
        elif token_type == 'STRING_LITERAL':
            self.pos += 1
            return Str(token_value)
        elif token_type == 'BOOLEAN':
            self.pos += 1
            return Bool(token_value)
        elif token_type == 'ID':
            self.pos += 1
            return Var(token_value)
        else:
            raise RuntimeError(f'Unexpected token {token_value}')
