from typing import Dict, Union, List

from pascal_parser import (
    ASTNode, Program, Block, VarDecl, Const, Type, Procedure, Function,
    SimpleType, ArrayType, Var, Assign, BinOp, UnaryOp, Num, String,
    Boolean, CompoundStatement, If, While, For, Case, ProcedureCall, NoOp
)
from lexer import Token

class CompilerError(Exception):
    def __init__(self, message: str, line: int = None, column: int = None):
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        if self.line and self.column:
            return f"Semantic error at line {self.line}, column {self.column}: {self.message}"
        return f"Semantic error: {self.message}"

class Symbol:
    def __init__(self, name: str, type: Union[SimpleType, ArrayType, 'ProcedureSymbol', 'FunctionSymbol']):
        self.name = name
        self.type = type

class VariableSymbol(Symbol):
    pass

class ConstantSymbol(Symbol):
    def __init__(self, name: str, type: Union[SimpleType, ArrayType], value: Union[int, float, str, bool]):
        super().__init__(name, type)
        self.value = value

class ProcedureSymbol(Symbol):
    def __init__(self, name: str, params: List[VariableSymbol]):
        super().__init__(name, None)
        self.params = params

class FunctionSymbol(ProcedureSymbol):
    def __init__(self, name: str, params: List[VariableSymbol], return_type: Union[SimpleType, ArrayType]):
        super().__init__(name, params)
        self.return_type = return_type

class ScopedSymbolTable:
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self.symbols: Dict[str, Symbol] = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def insert(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only=False):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

class SemanticAnalyzer:
    def __init__(self):
        self.current_scope: ScopedSymbolTable = None

    def visit(self, node: ASTNode):
        if node is None:
            return None
        method_name = f'visit_{type(node).__name__}'
        print(f"Visiting node: {type(node).__name__}")  # Debug print
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise CompilerError(f"No visit method found for {type(node).__name__}")
        result = visitor(node)
        print(f"Result of {method_name}: {result}")  # Debug print
        return result

    def create_type_token(self, type_name: str) -> Token:
        return Token(type_name, type_name, 0, 0)

    def visit_Program(self, node: Program):
        global_scope = ScopedSymbolTable(scope_name='global', scope_level=1)
        self.current_scope = global_scope
        self.visit(node.block)
        self.current_scope = self.current_scope.enclosing_scope

    def visit_Block(self, node: Block):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node: VarDecl):
        type_symbol = self.visit(node.type_node)
        var_name = node.var_node.value
        var_symbol = VariableSymbol(var_name, type_symbol)

        if self.current_scope.lookup(var_name, current_scope_only=True):
            raise CompilerError(f"Duplicate identifier '{var_name}' found")

        self.current_scope.insert(var_symbol)
        return type_symbol  # Return the type of the variable

    def visit_Const(self, node: Const):
        type_symbol = self.visit(node.value)
        const_symbol = ConstantSymbol(node.name, type_symbol, node.value.value)

        if self.current_scope.lookup(node.name, current_scope_only=True):
            raise CompilerError(f"Duplicate identifier '{node.name}' found")

        self.current_scope.insert(const_symbol)

    def visit_Type(self, node: Type):
        # For user-defined types, you might want to create a new type symbol
        # and add it to the symbol table
        pass

    def visit_Procedure(self, node: Procedure):
        proc_name = node.name
        proc_symbol = ProcedureSymbol(proc_name, [])

        if self.current_scope.lookup(proc_name, current_scope_only=True):
            raise CompilerError(f"Duplicate identifier '{proc_name}' found")

        self.current_scope.insert(proc_symbol)

        procedure_scope = ScopedSymbolTable(
            scope_name=proc_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = procedure_scope

        for param in node.params:
            param_type = self.visit(param.type_node)
            param_name = param.var_node.value
            var_symbol = VariableSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)

        self.visit(node.block)

        self.current_scope = self.current_scope.enclosing_scope

    def visit_Function(self, node: Function):
        func_name = node.name
        return_type = self.visit(node.return_type)
        func_symbol = FunctionSymbol(func_name, [], return_type)

        if self.current_scope.lookup(func_name, current_scope_only=True):
            raise CompilerError(f"Duplicate identifier '{func_name}' found")

        self.current_scope.insert(func_symbol)

        function_scope = ScopedSymbolTable(
            scope_name=func_name,
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = function_scope

        for param in node.params:
            param_type = self.visit(param.type_node)
            param_name = param.var_node.value
            var_symbol = VariableSymbol(param_name, param_type)
            self.current_scope.insert(var_symbol)
            func_symbol.params.append(var_symbol)

        self.visit(node.block)

        self.current_scope = self.current_scope.enclosing_scope

    def visit_SimpleType(self, node: SimpleType):
        return node

    def visit_ArrayType(self, node: ArrayType):
        return node

    def visit_Var(self, node: Var):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise CompilerError(f"Symbol(identifier) not found '{var_name}'")
        if var_symbol.type is None:
            raise CompilerError(f"Type information missing for variable '{var_name}'")
        return var_symbol.type

    def visit_Assign(self, node: Assign):
        right_type = self.visit(node.right)
        left = self.visit(node.left)

        if isinstance(left, SimpleType):
            left_type = left
        elif isinstance(left, VariableSymbol):
            left_type = left.type
        else:
            raise CompilerError(f"Invalid left-hand side in assignment: {type(left)}")

        if not self._check_type_compatibility(left_type, right_type):
            raise CompilerError(f"Incompatible types in assignment: {left_type.value} and {right_type.value}")
        return left_type
    def visit_BinOp(self, node: BinOp):
        print(f"Visiting BinOp: {node.op.type}")  # Debug print
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op.type

        # Handle VariableSymbol
        if isinstance(left_type, VariableSymbol):
            left_type = left_type.type
        if isinstance(right_type, VariableSymbol):
            right_type = right_type.type

        print(f"Left operand type: {left_type}")  # Debug print
        print(f"Right operand type: {right_type}")  # Debug print

        if left_type is None:
            raise CompilerError(f"Unable to determine type for left operand of '{op}' operator")
        if right_type is None:
            raise CompilerError(f"Unable to determine type for right operand of '{op}' operator")

        if op == 'INDEX':  # Array indexing
            if not isinstance(left_type, ArrayType):
                raise CompilerError(f"Indexing operation not supported for type {left_type.value}")
            if not isinstance(right_type, SimpleType) or right_type.value != 'INTEGER':
                raise CompilerError(f"Array index must be of type INTEGER, got {right_type.value}")
            return left_type.element_type

        if op in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            if not (isinstance(left_type, SimpleType) and isinstance(right_type, SimpleType)):
                raise CompilerError(f"Invalid types for arithmetic operator '{op}': {left_type.value} and {right_type.value}")
            if left_type.value not in ('INTEGER', 'REAL') or right_type.value not in ('INTEGER', 'REAL'):
                raise CompilerError(f"Invalid types for arithmetic operator '{op}': {left_type.value} and {right_type.value}")
            if left_type.value == 'REAL' or right_type.value == 'REAL':
                return SimpleType(self.create_type_token('REAL'))
            else:
                return SimpleType(self.create_type_token('INTEGER'))
        elif op in ('EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'):
            if not (isinstance(left_type, SimpleType) and isinstance(right_type, SimpleType)):
                raise CompilerError(f"Invalid types for comparison operator '{op}': {left_type.value} and {right_type.value}")
            if left_type.value not in ('INTEGER', 'REAL', 'STRING', 'BOOLEAN') or right_type.value not in ('INTEGER', 'REAL', 'STRING', 'BOOLEAN'):
                raise CompilerError(f"Invalid types for comparison operator '{op}': {left_type.value} and {right_type.value}")
            if left_type.value != right_type.value and not (left_type.value in ('INTEGER', 'REAL') and right_type.value in ('INTEGER', 'REAL')):
                raise CompilerError(f"Incompatible types for comparison operator '{op}': {left_type.value} and {right_type.value}")
            return SimpleType(self.create_type_token('BOOLEAN'))
        elif op in ('AND', 'OR'):
            if not (isinstance(left_type, SimpleType) and isinstance(right_type, SimpleType)):
                raise CompilerError(f"Invalid types for logical operator '{op}': {left_type.value} and {right_type.value}")
            if left_type.value != 'BOOLEAN' or right_type.value != 'BOOLEAN':
                raise CompilerError(f"Invalid types for logical operator '{op}': {left_type.value} and {right_type.value}")
            return SimpleType(self.create_type_token('BOOLEAN'))
        else:
            raise CompilerError(f"Unsupported binary operator: {op}")

    def visit_UnaryOp(self, node: UnaryOp):
        expr_type = self.visit(node.expr)
        op = node.op.type

        if op in ('PLUS', 'MINUS'):
            if not (isinstance(expr_type, SimpleType) and expr_type.value in ('INTEGER', 'REAL')):
                raise CompilerError(f"Invalid type for unary operator '{op}': {expr_type.value}")
            return expr_type
        elif op == 'NOT':
            if not (isinstance(expr_type, SimpleType) and expr_type.value == 'BOOLEAN'):
                raise CompilerError(f"Invalid type for unary operator '{op}': {expr_type.value}")
            return expr_type

    def visit_Num(self, node: Num):
        if isinstance(node.value, int):
            return SimpleType(self.create_type_token('INTEGER'))
        elif isinstance(node.value, float):
            return SimpleType(self.create_type_token('REAL'))
        else:
            raise CompilerError(f"Unexpected numeric type: {type(node.value)}")

    def visit_String(self, node: String):
        return SimpleType(self.create_type_token('STRING'))

    def visit_Boolean(self, node: Boolean):
        return SimpleType(self.create_type_token('BOOLEAN'))

    def visit_CompoundStatement(self, node: CompoundStatement):
        for statement in node.statements:
            if statement is not None:
                self.visit(statement)

    def visit_If(self, node: If):
        condition_type = self.visit(node.condition)
        if not (isinstance(condition_type, SimpleType) and condition_type.value == 'BOOLEAN'):
            raise CompilerError("Condition in IF statement must be of type BOOLEAN")
        self.visit(node.then_statement)
        if node.else_statement:
            self.visit(node.else_statement)

    def visit_While(self, node: While):
        condition_type = self.visit(node.condition)
        if not (isinstance(condition_type, SimpleType) and condition_type.value == 'BOOLEAN'):
            raise CompilerError("Condition in WHILE statement must be of type BOOLEAN")
        self.visit(node.statement)

    def visit_For(self, node: For):
        var_type = self.visit(node.var)
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)

        if not (isinstance(var_type, SimpleType) and var_type.value == 'INTEGER'):
            raise CompilerError("Loop variable in FOR statement must be of type INTEGER")
        if not (isinstance(start_type, SimpleType) and start_type.value == 'INTEGER'):
            raise CompilerError("Start value in FOR statement must be of type INTEGER")
        if not (isinstance(end_type, SimpleType) and end_type.value == 'INTEGER'):
            raise CompilerError("End value in FOR statement must be of type INTEGER")

        self.visit(node.statement)

    def visit_Case(self, node: Case):
        expr_type = self.visit(node.expr)
        for case_value, case_statement in node.cases:
            case_value_type = self.visit(case_value)
            if not self._check_type_compatibility(expr_type, case_value_type):
                raise CompilerError(f"Incompatible types in CASE statement")
            self.visit(case_statement)
        if node.else_case:
            self.visit(node.else_case)

    def visit_ProcedureCall(self, node: ProcedureCall):
        symbol = self.current_scope.lookup(node.name)
        if symbol is None or not isinstance(symbol, (ProcedureSymbol, FunctionSymbol)):
            raise CompilerError(f"Undefined procedure '{node.name}'")

        if len(node.actual_params) != len(symbol.params):
            raise CompilerError(f"Procedure '{node.name}' called with wrong number of arguments")

        for i, (param, arg) in enumerate(zip(symbol.params, node.actual_params)):
            arg_type = self.visit(arg)
            if not self._check_type_compatibility(param.type, arg_type):
                raise CompilerError(f"Incompatible argument type for parameter {i+1} of '{node.name}'")

        if isinstance(symbol, FunctionSymbol):
            return symbol.return_type
        return None

    def visit_NoOp(self, node: NoOp):
        return None

    def _check_type_compatibility(self, type1: Union[SimpleType, ArrayType, VariableSymbol], type2: Union[SimpleType, ArrayType, VariableSymbol]) -> bool:
        if isinstance(type1, VariableSymbol):
            type1 = type1.type
        if isinstance(type2, VariableSymbol):
            type2 = type2.type

        if isinstance(type1, SimpleType) and isinstance(type2, SimpleType):
            # Allow implicit conversion from INTEGER to REAL
            if (type1.value == 'REAL' and type2.value == 'INTEGER') or (type1.value == 'INTEGER' and type2.value == 'REAL'):
                return True
            return type1.value == type2.value
        elif isinstance(type1, ArrayType) and isinstance(type2, ArrayType):
            return (self._check_type_compatibility(type1.element_type, type2.element_type) and
                    type1.start.value == type2.start.value and
                    type1.end.value == type2.end.value)
        return False

def analyze(ast: Program):
    semantic_analyzer = SemanticAnalyzer()
    try:
        semantic_analyzer.visit(ast)
    except CompilerError as e:
        print(f"Semantic error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error during semantic analysis: {e}")
        raise