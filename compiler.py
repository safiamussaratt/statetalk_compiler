"""
StateTalk Compiler - CS4031 Course Project
Converts .st (StateTalk) files into executable Python chatbot code
"""

import ply.lex as lex
import ply.yacc as yacc
import sys
import os

# ============================================================================
# LEXER - Token Definitions
# ============================================================================

# List of token names
tokens = (
    'STATE', 'PROMPT', 'STORE', 'GOTO', 'IF', 'ELIF', 'ELSE', 'END',
    'SET', 'CALL', 'IDENTIFIER', 'STRING', 'NUMBER', 'VARIABLE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'EQ', 'EQEQ', 'NOTEQ',
    'LT', 'GT', 'PLUS', 'MINUS', 'COMMENT', 'BOOL', 'INT_TYPE', 'STR_TYPE',
    'INPUT', 'AS', 'COMMA'
)

# Reserved words
reserved = {
    'state': 'STATE',
    'prompt': 'PROMPT',
    'store': 'STORE',
    'goto': 'GOTO',
    'if': 'IF',
    'elif': 'ELIF',
    'else': 'ELSE',
    'end': 'END',
    'set': 'SET',
    'call': 'CALL',
    'true': 'BOOL',
    'false': 'BOOL',
    'int': 'INT_TYPE',
    'str': 'STR_TYPE',
    'input': 'INPUT',
    'as': 'AS',
}

# Token regex rules
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_EQ = r'='
t_EQEQ = r'=='
t_NOTEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_COMMA = r','

# Ignored characters (spaces and tabs)
t_ignore = ' \t'

def t_VARIABLE(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_COMMENT(t):
    r'\#.*'
    pass  # Ignore comments

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# ============================================================================
# PARSER - Grammar Rules
# ============================================================================

# AST Node classes
class Program:
    def __init__(self, states):
        self.states = states

class State:
    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

class PromptStmt:
    def __init__(self, message):
        self.message = message

class StoreStmt:
    def __init__(self, var_name, var_type=None):
        self.var_name = var_name
        self.var_type = var_type

class GotoStmt:
    def __init__(self, target):
        self.target = target

class SetStmt:
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value

class IfStmt:
    def __init__(self, condition, body, elifs, else_body):
        self.condition = condition
        self.body = body
        self.elifs = elifs
        self.else_body = else_body

class Condition:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class CallStmt:
    def __init__(self, function, args):
        self.function = function
        self.args = args

# Parser rules
def p_program(p):
    '''program : state_list'''
    p[0] = Program(p[1])

def p_state_list(p):
    '''state_list : state
                  | state_list state'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_state(p):
    '''state : STATE IDENTIFIER LBRACE statement_list RBRACE'''
    p[0] = State(p[2], p[4])

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = p[1] + ([p[2]] if p[2] else [])

def p_statement(p):
    '''statement : prompt_stmt
                 | store_stmt
                 | goto_stmt
                 | set_stmt
                 | if_stmt
                 | call_stmt
                 | COMMENT'''
    p[0] = p[1] if len(p) > 1 else None

def p_prompt_stmt(p):
    '''prompt_stmt : PROMPT STRING'''
    p[0] = PromptStmt(p[2])

def p_store_stmt(p):
    '''store_stmt : STORE INPUT AS VARIABLE
                  | STORE INPUT AS VARIABLE LPAREN INT_TYPE RPAREN
                  | STORE INPUT AS VARIABLE LPAREN STR_TYPE RPAREN'''
    if len(p) == 5:
        p[0] = StoreStmt(p[4], None)
    elif len(p) == 8:
        p[0] = StoreStmt(p[5], p[7])
    else:
        p[0] = StoreStmt(p[5], None)

def p_goto_stmt(p):
    '''goto_stmt : GOTO IDENTIFIER'''
    p[0] = GotoStmt(p[2])

def p_set_stmt(p):
    '''set_stmt : SET VARIABLE EQ expression'''
    p[0] = SetStmt(p[2], p[4])

def p_if_stmt(p):
    '''if_stmt : IF expression LBRACE statement_list RBRACE elif_list else_opt END'''
    p[0] = IfStmt(p[2], p[4], p[6], p[7])

def p_elif_list(p):
    '''elif_list : ELIF expression LBRACE statement_list RBRACE elif_list
                 | empty'''
    if len(p) == 7:
        p[0] = [(p[2], p[4])] + p[6]
    else:
        p[0] = []

def p_else_opt(p):
    '''else_opt : ELSE LBRACE statement_list RBRACE
                | empty'''
    if len(p) == 5:
        p[0] = p[3]
    else:
        p[0] = []

def p_call_stmt(p):
    '''call_stmt : CALL IDENTIFIER LPAREN arg_list RPAREN'''
    p[0] = CallStmt(p[2], p[4])

def p_arg_list(p):
    '''arg_list : expression
                | arg_list COMMA expression
                | empty'''
    if len(p) == 2:
        if p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]

def p_expression_basic(p):
    '''expression : STRING
                  | NUMBER
                  | BOOL
                  | VARIABLE'''
    p[0] = p[1]

def p_expression_arithmetic(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression'''
    p[0] = Condition(p[1], p[2], p[3])

def p_expression_comparison(p):
    '''expression : expression EQEQ expression
                  | expression NOTEQ expression
                  | expression LT expression
                  | expression GT expression'''
    p[0] = Condition(p[1], p[2], p[3])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
        print(f"Token type: {p.type}")
    else:
        print("Syntax error at EOF")

# ============================================================================
# CODE GENERATOR - Converts AST to Python
# ============================================================================

class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        self.variables = set()
        
    def indent(self):
        return "    " * self.indent_level
        
    def emit(self, code):
        self.output.append(self.indent() + code)
        
    def generate(self, program):
        """Generate Python code from AST"""
        
        # Header
        self.emit('"""')
        self.emit('Auto-generated chatbot from StateTalk compiler')
        self.emit('CS4031 Compiler Construction Project')
        self.emit('"""')
        self.emit('')
        self.emit('import sys')
        self.emit('')
        self.emit('')
        self.emit('class ChatBot:')
        self.indent_level += 1
        self.emit('def __init__(self):')
        self.indent_level += 1
        self.emit('# Initialize variables')
        self.emit('self.vars = {}')
        self.emit('self.current_state = None')
        self.indent_level -= 1
        self.emit('')
        
        # Generate state methods
        for state in program.states:
            self.generate_state(state)
            
        # Generate run method
        self.emit('def run(self, start_state="Welcome"):')
        self.indent_level += 1
        self.emit('self.current_state = start_state')
        self.emit('while self.current_state != "END":')
        self.indent_level += 1
        self.emit('if hasattr(self, f"state_{self.current_state}"):')
        self.indent_level += 1
        self.emit('getattr(self, f"state_{self.current_state}")()')
        self.indent_level -= 1
        self.emit('else:')
        self.indent_level += 1
        self.emit(f'print(f"Error: State \'{{self.current_state}}\' not found!")')
        self.emit('break')
        self.indent_level -= 1
        self.indent_level -= 1
        self.emit('print("\\n[Chat session ended]")')
        self.indent_level -= 1
        self.indent_level -= 1
        
        # Main execution block
        self.emit('')
        self.emit('if __name__ == "__main__":')
        self.indent_level += 1
        self.emit('bot = ChatBot()')
        self.emit('bot.run()')
        
        return '\n'.join(self.output)
    
    def generate_state(self, state):
        """Generate a method for a state"""
        method_name = f"state_{state.name}"
        self.emit(f'def {method_name}(self):')
        self.indent_level += 1
        self.emit(f'"""State: {state.name}"""')
        
        for stmt in state.statements:
            self.generate_statement(stmt)
            
        self.indent_level -= 1
        self.emit('')
    
    def generate_statement(self, stmt):
        """Generate code for a single statement"""
        if isinstance(stmt, PromptStmt):
            # Handle variable interpolation in strings
            message = stmt.message
            # Simple interpolation: replace {$var} with {self.vars.get('var', '')}
            import re
            interpolated = re.sub(r'\{\s*\$(\w+)\s*\}', r'{self.vars.get("\1", "")}', message)
            self.emit(f'print(f"{interpolated}")')
            
        elif isinstance(stmt, StoreStmt):
            var_name = stmt.var_name[1:]  # Remove $ prefix
            self.variables.add(var_name)
            
            if stmt.var_type == 'int':
                self.emit(f'while True:')
                self.indent_level += 1
                self.emit(f'try:')
                self.indent_level += 1
                self.emit(f'{var_name}_input = input("> ")')
                self.emit(f'self.vars["{var_name}"] = int({var_name}_input)')
                self.emit(f'break')
                self.indent_level -= 1
                self.emit(f'except ValueError:')
                self.indent_level += 1
                self.emit(f'print("Error: Please enter a valid number.")')
                self.indent_level -= 1
                self.indent_level -= 1
            elif stmt.var_type == 'str':
                self.emit(f'self.vars["{var_name}"] = input("> ")')
            else:
                self.emit(f'self.vars["{var_name}"] = input("> ")')
                
        elif isinstance(stmt, GotoStmt):
            self.emit(f'self.current_state = "{stmt.target}"')
            self.emit('return')
            
        elif isinstance(stmt, SetStmt):
            var_name = stmt.var_name[1:]  # Remove $ prefix
            self.variables.add(var_name)
            
            if isinstance(stmt.value, str):
                self.emit(f'self.vars["{var_name}"] = "{stmt.value}"')
            elif isinstance(stmt.value, bool):
                self.emit(f'self.vars["{var_name}"] = {stmt.value}')
            elif isinstance(stmt.value, int):
                self.emit(f'self.vars["{var_name}"] = {stmt.value}')
            elif isinstance(stmt.value, Condition):
                expr_code = self.generate_expression(stmt.value)
                self.emit(f'self.vars["{var_name}"] = {expr_code}')
                
        elif isinstance(stmt, IfStmt):
            # Generate if condition
            cond_code = self.generate_expression(stmt.condition)
            self.emit(f'if {cond_code}:')
            self.indent_level += 1
            for s in stmt.body:
                self.generate_statement(s)
            self.indent_level -= 1
            
            # Generate elif blocks
            for elif_cond, elif_body in stmt.elifs:
                cond_code = self.generate_expression(elif_cond)
                self.emit(f'elif {cond_code}:')
                self.indent_level += 1
                for s in elif_body:
                    self.generate_statement(s)
                self.indent_level -= 1
                
            # Generate else block
            if stmt.else_body:
                self.emit('else:')
                self.indent_level += 1
                for s in stmt.else_body:
                    self.generate_statement(s)
                self.indent_level -= 1
                
        elif isinstance(stmt, CallStmt):
            # Generate arguments without extra quotes for variables
            args_list = []
            for arg in stmt.args:
                if isinstance(arg, str) and arg.startswith('$'):
                    var_name = arg[1:]
                    args_list.append(f'self.vars.get("{var_name}", "")')
                elif isinstance(arg, str):
                    args_list.append(f'"{arg}"')
                elif isinstance(arg, bool):
                    args_list.append(str(arg))
                elif isinstance(arg, int):
                    args_list.append(str(arg))
                elif isinstance(arg, Condition):
                    args_list.append(self.generate_expression(arg))
                else:
                    args_list.append(str(arg))
            
            args_str = ', '.join(args_list)
            func_name = stmt.function
            
            self.emit(f'# Calling API: {func_name}({args_str})')
            # Use string concatenation to avoid nested quote issues
            self.emit(f'print("[Simulating API call: {func_name}(" + str({args_str}) + ")]")')
    
    def generate_expression(self, expr):
        """Convert expression AST to Python code string"""
        if isinstance(expr, str):
            # Check if it's a variable (starts with $)
            if expr.startswith('$'):
                var_name = expr[1:]
                return f'self.vars.get("{var_name}", "")'
            else:
                return f'"{expr}"'
        elif isinstance(expr, int):
            return str(expr)
        elif isinstance(expr, bool):
            return str(expr)
        elif isinstance(expr, Condition):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            
            op_map = {
                '==': '==',
                '!=': '!=',
                '<': '<',
                '>': '>',
                '+': '+',
                '-': '-'
            }
            return f'{left} {op_map.get(expr.op, expr.op)} {right}'
        return str(expr)

# ============================================================================
# COMPILER - Main Interface
# ============================================================================

class StateTalkCompiler:
    def __init__(self):
        self.lexer = lex.lex()
        self.parser = yacc.yacc()
        
    def compile(self, input_file, output_file=None):
        """Compile a .st file to Python"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Parse the source
            ast = self.parser.parse(source_code)
            
            if ast is None:
                print("Compilation failed: Syntax errors detected")
                return False
                
            # Generate code
            generator = CodeGenerator()
            python_code = generator.generate(ast)
            
            # Determine output filename
            if output_file is None:
                output_file = input_file.replace('.st', '_bot.py')
                
            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
                
            print(f"✓ Successfully compiled '{input_file}' -> '{output_file}'")
            print(f"✓ Run the chatbot with: python {output_file}")
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            return False
        except Exception as e:
            print(f"Compilation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input_file.st> [output_file.py]")
        print("Example: python compiler.py example.st")
        sys.exit(1)
        
    compiler = StateTalkCompiler()
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = compiler.compile(input_file, output_file)
    sys.exit(0 if success else 1)