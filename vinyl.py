import re
import sys
import time

class Lexer:
    def __init__(self, code):
        code = re.sub(r'#.*', '', code)
        self.tokens = re.findall(
            r'\s*(=>|==|<=|>=|[(),{}:;]|!=|\d+\.\d+|\d+|[-+*/=]|"[^"]*"|true|false|int|float|bool|string|input|wait|print|[A-Za-z_]\w*)',
            code
        )
        self.current = 0

    def next_token(self):
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        return None

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.next_token()

    def eat(self, token_type):
        if self.current_token == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(f'Unexpected token: {self.current_token}, expected: {token_type}')

    def parse(self):
        statements = []
        while self.current_token is not None:
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.current_token in ('int', 'float', 'bool', 'string'):
            return self.variable_declaration()
        elif self.current_token == 'print':
            return self.print_statement()
        elif self.current_token == 'input':
            return self.input_statement()
        elif self.current_token == 'wait':
            return self.wait_statement()
        else:
            raise SyntaxError(f'Unexpected statement: {self.current_token}')

    def variable_declaration(self):
        var_type = self.current_token
        self.eat(var_type)
        var_name = self.current_token
        self.eat(var_name)
        self.eat('=')
        expr = self.expression()
        return ('assign', var_type, var_name, expr)

    def print_statement(self):
        self.eat('print')
        expr = self.expression()
        return ('print', expr)

    def input_statement(self):
        self.eat('input')
        var_name = self.current_token
        self.eat(var_name)
        self.eat('=')
        prompt = self.current_token
        self.eat(prompt)
        return ('input', var_name, prompt)

    def wait_statement(self):
        self.eat('wait')
        duration = self.expression()
        return ('wait', duration)

    def expression(self):
        left = self.term()
        while self.current_token in ('+', '-', '==', '!=', '>', '<', '>=', '<='):
            op = self.current_token
            self.eat(op)
            right = self.term()
            left = (op, left, right)
        return left

    def term(self):
        left = self.factor()
        while self.current_token in ('*', '/'):
            op = self.current_token
            self.eat(op)
            right = self.factor()
            left = (op, left, right)
        return left

    def factor(self):
        token = self.current_token
        if re.match(r'\d+\.\d+', token):
            self.eat(token)
            return ('float', float(token))
        elif token.isdigit():
            self.eat(token)
            return ('int', int(token))
        elif token.startswith('"') and token.endswith('"'):
            self.eat(token)
            return ('string', token[1:-1])
        elif token == 'true':
            self.eat('true')
            return ('bool', True)
        elif token == 'false':
            self.eat('false')
            return ('bool', False)
        elif token.isidentifier():
            self.eat(token)
            return ('var', token)
        elif token == '(':
            self.eat('(')
            expr = self.expression()
            self.eat(')')
            return expr
        else:
            raise SyntaxError(f'Unexpected token: {token}')

class Interpreter:
    def __init__(self):
        self.variables = {}

    def evaluate(self, node):
        if isinstance(node, tuple):
            op = node[0]
            if op in ('int', 'float', 'string', 'bool'):
                return node[1]
            elif op == 'var':
                if node[1] in self.variables:
                    return self.variables[node[1]]
                else:
                    raise NameError(f'Undefined variable: {node[1]}')
            elif op in ('+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<='):
                left = self.evaluate(node[1])
                right = self.evaluate(node[2])
                return self.perform_operation(op, left, right)
            elif op == 'assign':
                var_type, var_name, expr = node[1], node[2], node[3]
                value = self.evaluate(expr)
                self.variables[var_name] = self.cast_type(var_type, value)
                return value
            elif op == 'print':
                value = self.evaluate(node[1])
                print(value)
                return value
            elif op == 'input':
                var_name, prompt = node[1], node[2]
                user_input = input(prompt + ": ")
                self.variables[var_name] = user_input
                return user_input
            elif op == 'wait':
                duration = self.evaluate(node[1])
                time.sleep(duration)
                return None
        else:
            return node

    def perform_operation(self, op, left, right):
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '>':
            return left > right
        elif op == '<':
            return left < right
        elif op == '>=':
            return left >= right
        elif op == '<=':
            return left <= right

    def cast_type(self, var_type, value):
        if var_type == 'int':
            return int(value)
        elif var_type == 'float':
            return float(value)
        elif var_type == 'bool':
            return bool(value)
        elif var_type == 'string':
            return str(value)
        else:
            raise TypeError(f'Unknown type: {var_type}')

    def execute(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        for statement in ast:
            self.evaluate(statement)

    def run_file(self, filename):
        with open(filename, 'r') as file:
            code = file.read()
            self.execute(code)

def display_homepage():
    print("""
Vinyl Interpreter [v0.2]
==========================
Usage: vinyl <filename.vy>

Features:
- Variable declarations (int, float, bool, string)
- Arithmetic and logical expressions
- Input, print, and wait commands
==========================
""")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        display_homepage()
        sys.exit(1)

    filename = sys.argv[1]
    if not filename.endswith('.vy'):
        print("Error: Only '.vy' files are supported.")
        sys.exit(2)

    interpreter = Interpreter()
    try:
        interpreter.run_file(filename)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(3)
