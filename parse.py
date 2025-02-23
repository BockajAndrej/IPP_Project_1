from lark import Lark

# Grammar for basic arithmetic expressions
grammar = """
    ?start: expr
    ?expr: expr "+" term   -> add
         | expr "-" term   -> sub
         | term
    ?term: term "*" factor -> mul
         | term "/" factor -> div
         | factor
    ?factor: NUMBER        -> e
           | "(" expr ")"

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

def main():
    print("Hello, World!")
    # Create the parser
    parser = Lark(grammar, start="start", parser="lalr")
    tree = parser.parse("3 + 5 * (2 - 8)")
    print(tree.pretty())  # Displays the parse tree

if __name__ == "__main__":
    main()