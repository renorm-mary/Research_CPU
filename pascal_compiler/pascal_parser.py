from typing import List, Tuple, Optional, Union
from lexer import Token

class CompilerError(Exception):
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token

    def __str__(self):
        if self.token:
            return f"Error at line {self.token.line}, column {self.token.column}: {self.message}"
        return self.message
    
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, name: str, block: 'Block'):
        self.name = name
        self.block = block

class Block(ASTNode):
    def __init__(self, declarations: List[ASTNode], compound_statement: 'CompoundStatement'):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(ASTNode):
    def __init__(self, var_node: 'Var', type_node: Union['SimpleType', 'ArrayType']):
        self.var_node = var_node
        self.type_node = type_node

class Const(ASTNode):
    def __init__(self, name: str, value: Union['Num', 'String', 'Boolean']):
        self.name = name
        self.value = value

class Type(ASTNode):
    def __init__(self, name: str, type_spec: Union['SimpleType', 'ArrayType']):
        self.name = name
        self.type_spec = type_spec

class Procedure(ASTNode):
    def __init__(self, name: str, params: List[VarDecl], block: 'Block'):
        self.name = name
        self.params = params
        self.block = block

class Function(ASTNode):
    def __init__(self, name: str, params: List[VarDecl], return_type: Union['SimpleType', 'ArrayType'], block: 'Block'):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block

class SimpleType(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class ArrayType(ASTNode):
    def __init__(self, element_type: SimpleType, start: 'Num', end: 'Num'):
        self.element_type = element_type
        self.start = start
        self.end = end

class Var(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class Assign(ASTNode):
    def __init__(self, left: Var, op: Token, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class BinOp(ASTNode):
    def __init__(self, left: ASTNode, op: Token, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op: Token, expr: ASTNode):
        self.op = op
        self.expr = expr

class Num(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class String(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

class Boolean(ASTNode):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value.lower() == 'true'

class CompoundStatement(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class If(ASTNode):
    def __init__(self, condition: ASTNode, then_statement: ASTNode, else_statement: Optional[ASTNode] = None):
        self.condition = condition
        self.then_statement = then_statement
        self.else_statement = else_statement

class While(ASTNode):
    def __init__(self, condition: ASTNode, statement: ASTNode):
        self.condition = condition
        self.statement = statement

class For(ASTNode):
    def __init__(self, var: Var, start: ASTNode, end: ASTNode, statement: ASTNode, direction: str):
        self.var = var
        self.start = start
        self.end = end
        self.statement = statement
        self.direction = direction

class Case(ASTNode):
    def __init__(self, expr: ASTNode, cases: List[Tuple[Union[Num, String], ASTNode]], else_case: Optional[ASTNode] = None):
        self.expr = expr
        self.cases = cases
        self.else_case = else_case

class ProcedureCall(ASTNode):
    def __init__(self, name: str, actual_params: List[ASTNode]):
        self.name = name
        self.actual_params = actual_params

class NoOp(ASTNode):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def eat(self, token_type: str):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f"Expected {token_type}, found {self.current_token.type if self.current_token else 'EOF'}")

    def error(self, message: str):
        raise CompilerError(message, self.current_token)

    def create_token(self, type: str, value: str, line: int = 0, column: int = 0) -> Token:
        return Token(type, value, line, column)

    def parse(self) -> Program:
        node = self.program()
        if self.current_token is not None:
            self.error("Unexpected token after end of program")
        return node

    def program(self) -> Program:
        self.eat('PROGRAM')
        program_name = self.current_token.value
        self.eat('ID')
        self.eat('SEMICOLON')
        block = self.block()
        self.eat('DOT')
        return Program(program_name, block)

    def block(self) -> Block:
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        return Block(declarations, compound_statement)

    def declarations(self) -> List[ASTNode]:
        declarations = []
        if self.current_token.type == 'VAR':
            declarations.extend(self.var_declaration())
        while self.current_token.type in ('PROCEDURE', 'FUNCTION'):
            if self.current_token.type == 'PROCEDURE':
                declarations.append(self.procedure_declaration())
            else:
                declarations.append(self.function_declaration())
        return declarations

    def var_declaration(self) -> List[VarDecl]:
        var_declarations = []
        self.eat('VAR')
        while self.current_token.type == 'ID':
            var_decl = self.variable_declaration()
            var_declarations.extend(var_decl)
            self.eat('SEMICOLON')
        return var_declarations

    def variable_declaration(self) -> List[VarDecl]:
        var_nodes = [Var(self.current_token)]
        self.eat('ID')
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            var_nodes.append(Var(self.current_token))
            self.eat('ID')
        self.eat('COLON')
        type_node = self.type_spec()
        var_declarations = [VarDecl(var_node, type_node) for var_node in var_nodes]
        return var_declarations

    def type_spec(self) -> Union[SimpleType, ArrayType]:
        token = self.current_token
        if token.type in ('INTEGER', 'REAL', 'BOOLEAN', 'CHAR', 'STRING'):
            self.eat(token.type)
            return SimpleType(token)
        elif token.type == 'ARRAY':
            return self.array_type_spec()
        elif token.type == 'ID':
            self.eat('ID')
            return SimpleType(token)
        else:
            self.error(f"Unexpected type: {token.type}")

    def array_type_spec(self) -> ArrayType:
        self.eat('ARRAY')
        self.eat('LBRACKET')
        start = self.expr()
        self.eat('DOT')
        self.eat('DOT')
        end = self.expr()
        self.eat('RBRACKET')
        self.eat('OF')
        element_type = self.type_spec()
        return ArrayType(element_type, start, end)

    def procedure_declaration(self) -> Procedure:
        self.eat('PROCEDURE')
        proc_name = self.current_token.value
        self.eat('ID')
        params = []
        if self.current_token.type == 'LPAREN':
            params = self.formal_parameter_list()
        self.eat('SEMICOLON')
        block = self.block()
        self.eat('SEMICOLON')
        return Procedure(proc_name, params, block)

    def function_declaration(self) -> Function:
        self.eat('FUNCTION')
        func_name = self.current_token.value
        self.eat('ID')
        params = []
        if self.current_token.type == 'LPAREN':
            params = self.formal_parameter_list()
        self.eat('COLON')
        return_type = self.type_spec()
        self.eat('SEMICOLON')
        block = self.block()
        self.eat('SEMICOLON')
        return Function(func_name, params, return_type, block)

    def formal_parameter_list(self) -> List[VarDecl]:
        self.eat('LPAREN')
        params = self.formal_parameters()
        self.eat('RPAREN')
        return params

    def formal_parameters(self) -> List[VarDecl]:
        if self.current_token.type == 'ID':
            param_nodes = self.variable_declaration()
            while self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
                param_nodes.extend(self.variable_declaration())
            return param_nodes
        return []

    def compound_statement(self) -> CompoundStatement:
        self.eat('BEGIN')
        statements = self.statement_list()
        self.eat('END')
        return CompoundStatement(statements)

    def statement_list(self) -> List[ASTNode]:
        statement = self.statement()
        results = [statement]
        while self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
            results.append(self.statement())
        return results

    def statement(self) -> ASTNode:
        if self.current_token.type == 'BEGIN':
            return self.compound_statement()
        elif self.current_token.type == 'ID':
            return self.assignment_statement()
        elif self.current_token.type == 'IF':
            return self.if_statement()
        elif self.current_token.type == 'WHILE':
            return self.while_statement()
        elif self.current_token.type == 'FOR':
            return self.for_statement()
        elif self.current_token.type == 'CASE':
            return self.case_statement()
        elif self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
            return NoOp()
        else:
            return self.empty()

    def assignment_statement(self) -> Union[Assign, ProcedureCall]:
        left = self.variable()
        if self.current_token.type == 'ASSIGN':
            token = self.current_token
            self.eat('ASSIGN')
            right = self.expr()
            return Assign(left, token, right)
        else:
            return self.procedure_call(left.value)

    def if_statement(self) -> If:
        self.eat('IF')
        condition = self.expr()
        self.eat('THEN')
        then_statement = self.statement()
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_statement = self.statement()
        else:
            else_statement = None
        return If(condition, then_statement, else_statement)

    def while_statement(self) -> While:
        self.eat('WHILE')
        condition = self.expr()
        self.eat('DO')
        statement = self.statement()
        return While(condition, statement)

    def for_statement(self) -> For:
        self.eat('FOR')
        var = self.variable()
        self.eat('ASSIGN')
        start = self.expr()
        if self.current_token.type == 'TO':
            direction = 'TO'
            self.eat('TO')
        else:
            direction = 'DOWNTO'
            self.eat('DOWNTO')
        end = self.expr()
        self.eat('DO')
        statement = self.statement()
        return For(var, start, end, statement, direction)

    def case_statement(self) -> Case:
        self.eat('CASE')
        expr = self.expr()
        self.eat('OF')
        cases = []
        while self.current_token.type in ('INTEGER', 'STRING'):
            case_value = self.expr()
            self.eat('COLON')
            case_statement = self.statement()
            cases.append((case_value, case_statement))
            self.eat('SEMICOLON')
        else_case = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_case = self.statement()
            self.eat('SEMICOLON')
        self.eat('END')
        return Case(expr, cases, else_case)

    def procedure_call(self, proc_name: str) -> ProcedureCall:
        actual_params = []
        if self.current_token.type == 'LPAREN':
            self.eat('LPAREN')
            if self.current_token.type != 'RPAREN':
                actual_params.append(self.expr())
                while self.current_token.type == 'COMMA':
                    self.eat('COMMA')
                    actual_params.append(self.expr())
            self.eat('RPAREN')
        return ProcedureCall(proc_name, actual_params)

    def variable(self) -> Union[Var, BinOp]:
        node = Var(self.current_token)
        self.eat('ID')
        
        if self.current_token.type == 'LBRACKET':
            self.eat('LBRACKET')
            index = self.expr()
            self.eat('RBRACKET')
            return BinOp(left=node, op=self.create_token('INDEX', '[]'), right=index)
        
        return node

    def empty(self) -> NoOp:
        return NoOp()
    
    def expr(self) -> ASTNode:
        node = self.simple_expr()
        while self.current_token and self.current_token.type in ('EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.simple_expr())
        return node

    def simple_expr(self) -> ASTNode:
        node = self.term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS', 'OR'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self) -> ASTNode:
        node = self.factor()
        while self.current_token and self.current_token.type in ('MUL', 'DIV', 'AND'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self) -> ASTNode:
        token = self.current_token
        if token.type == 'PLUS':
            self.eat('PLUS')
            return UnaryOp(token, self.factor())
        elif token.type == 'MINUS':
            self.eat('MINUS')
            return UnaryOp(token, self.factor())
        elif token.type == 'INTEGER':
            self.eat('INTEGER')
            return Num(token)
        elif token.type == 'REAL':
            self.eat('REAL')
            return Num(token)
        elif token.type == 'STRING':
            self.eat('STRING')
            return String(token)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return Boolean(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        elif token.type == 'ID':
            return self.variable_or_procedure_call()
        else:
            self.error(f"Unexpected token: {token.type}")

    def variable_or_procedure_call(self) -> Union[Var, ProcedureCall, BinOp]:
        node = self.variable()
        if isinstance(node, Var) and self.current_token.type == 'LPAREN':
            return self.procedure_call(node.value)
        return node

def parse(tokens: List[Token]) -> Program:
    parser = Parser(tokens)
    return parser.parse()