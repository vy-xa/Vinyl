import re
import sys
import time

class Lexer:
    def __init__(self, code):
        code = re.sub(r'#.*', '', code)
        self.tokens = re.findall(r'\s*(=>|==|<=|>=|[(),{}:;]|==|!=|\d+\.\d+|\d+|[-+*/=]|"[^"]*"|true|false|int|float|bool|string|input|wait|print|[A-Za-z_]\w*)', code)
        self.current = 0

    def next_token(self):
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        else:
            return None

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.next_token()

    def eat(self, token_type):
        if self.current_token == token_type:
            self.current_token = self.lexer.next_token()
        else:
            raise Exception(f'Unexpected token: {self.current_token}, expected: {token_type}')

    def parse(self):
        result = []
        while self.current_token is not None:
            result.append(self.statement())
        return result
    
    def statement(self):
        if self.current_token in ('int', 'float', 'bool', 'string'):
            var_type = self.current_token
            self.eat(var_type)
            var_name = self.current_token
            self.eat(var_name)
            self.eat('=')
            expr = self.expression()
            return ('assign', var_type, var_name, expr)
        elif self.current_token == 'print':
            self.eat('print')
            expr = self.expression()
            return ('print', expr)
        elif self.current_token == 'input':
            self.eat('input')
            var_name = self.current_token
            self.eat(var_name)
            self.eat('=')
            return ('input', var_name)
        elif self.current_token == 'wait':
            self.eat('wait')
            duration = self.current_token
            self.eat(duration)
            return ('wait', int(duration))
        else:
            raise Exception(f'Unexpected statement: {self.current_token}')

    def expression(self):
        result = self.term()
        while self.current_token in ('+', '-', '==', '!=', '>', '<', '>=', '<='):
            op = self.current_token
            self.eat(op)
            result = (op, result, self.term())
        return result

    def term(self):
        result = self.factor()
        while self.current_token in ('*', '/'):
            op = self.current_token
            self.eat(op)
            result = (op, result, self.factor())
        return result

    def factor(self):
        token = self.current_token
        if re.match(r'\d+\.\d+', token):
            self.eat(token)
            return ('float', float(token))
        elif token.isdigit():
            self.eat(token)
            return ('num', int(token))
        elif token.startswith('"') and token.endswith('"'):
            self.eat(token)
            return ('str', token[1:-1])
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
            result = self.expression()
            self.eat(')')
            return result
        else:
            raise Exception(f'Unexpected token: {token}')

class Interpreter:
    def __init__(self):
        self.variables = {}

    def evaluate(self, node):
        if node[0] == 'num':
            return node[1]
        elif node[0] == 'float':
            return node[1]
        elif node[0] == 'str':
            return node[1]
        elif node[0] == 'bool':
            return node[1]
        elif node[0] == 'var':
            return self.variables.get(node[1], 0)
        elif node[0] in ('+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<='):
            left = self.evaluate(node[1])
            right = self.evaluate(node[2])
            if node[0] == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif node[0] == '-':
                return left - right
            elif node[0] == '*':
                return left * right
            elif node[0] == '/':
                return left / right
            elif node[0] == '==':
                return left == right
            elif node[0] == '!=':
                return left != right
            elif node[0] == '>':
                return left > right
            elif node[0] == '<':
                return left < right
            elif node[0] == '>=':
                return left >= right
            elif node[0] == '<=':
                return left <= right
        elif node[0] == 'assign':
            var_type, var_name, expr = node[1], node[2], node[3]
            value = self.evaluate(expr)
            self.variables[var_name] = value
            return value
        elif node[0] == 'input':
            var_name = node[1]
            user_input = input(f"Enter value for {var_name}: ")
            self.variables[var_name] = user_input
            return user_input
        elif node[0] == 'print':
            value = self.evaluate(node[1])
            print(value)
            return value
        elif node[0] == 'wait':
            duration = node[1]
            time.sleep(duration)
            return None
        else:
            raise Exception(f'Unknown node type: {node[0]}')

    def execute(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        for node in ast:
            self.evaluate(node)

    def run_file(self, filename):
        with open(filename, 'r') as file:
            code = file.read()
            self.execute(code)

def display_homepage():
    print("""
Welcome to the Vinyl!
[ build : 0.1 ]
============================================================================

Usage: vinyl.exe <filename.vy>

Available Commands:
----------------------------------------------------------------------------
int <variable> = <value>     : Declare an integer variable
float <variable> = <value>   : Declare a float variable
bool <variable> = <value>    : Declare a boolean variable (true/false)
string <variable> = <value>  : Declare a string variable
print <expression>           : Print an expression
wait <duration>              : Wait for specified duration (seconds)

Example:
----------------------------------------------------------------------------
int a = 5
float b = 10.2
wait 2
print a + b
          
============================================================================

""")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        display_homepage()
        input("0x4\nPress enter to continue...")
        sys.exit(0x4)

    filename = sys.argv[1]
    if not filename.endswith('.vy'):
        input("0x2")
        sys.exit(0x2)

    interpreter = Interpreter()
    try:
        interpreter.run_file(filename)
        input("0x4\nPress enter to continue...")
        sys.exit(0x4)
    except Exception as e:
        input(f'0x3\n{e}\nPress enter to continue...')
        sys.exit(0x3)
