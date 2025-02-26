import sys
from enum import Enum
from lark import Lark, UnexpectedCharacters, UnexpectedToken, Transformer

class Color(Enum):
    WRONGPARAM = 10, 
    INFILEERR = 11,     # We will use STDIO
    OUTFILEERR = 12,    # We will use STDIO
    LEXERR = 21,
    SYNTERR = 22,
    SEMERRMAIN = 31,
    SEMERRUNDEF = 32,
    SEMERRARIT = 33,
    SEMERRCOLLISION = 34,
    SEMERR = 35,
    INTERNERR = 99

grammar = """
    ?start: program

    program: class*  // Allows multiple class definitions

    class: "class" CID ":" CID "{" method "}"

    method: (selector block)*

    selector: ID
            | ID ":" selector_tail
    selector_tail: (ID ":")*

    block: "[" block_par "|" block_stat "]"
    block_par: (":" ID)*
    block_stat: (ID ":=" expr ".")*

    expr: expr_base expr_tail
    expr_base: ID 
             | CID 
             | STR 
             | INT
             | "(" expr ")"
             | block
    expr_tail: ID
             | expr_sel
    expr_sel: (ID ":" expr_base)*

    CID: /[a-zA-Z][a-zA-Z0-9_]*/   // Uppercase for token rules
    ID: /[a-zA-Z_][a-zA-Z0-9_]*/

    INT : /-?\d+([eE][+-]?\d+)?/
    COMMENT: /\"(?:\\.|[^\\"])*\"/s

    %import common.ESCAPED_STRING -> STR
    %import common.WS
    %ignore COMMENT
    %ignore WS
"""
def main():

    if len(sys.argv) > 1:
        sys.stderr.write("- chybejici parametr skriptu (je-li treba) nebo použiti zakazane kombinace parametru\n")
        sys.exit(Color.WRONGPARAM.value)

    data = sys.stdin.read()  # Read all input

    # Create the parser
    parser = Lark(grammar, parser="lalr")

    try:
        tree = parser.parse(data)
    except UnexpectedCharacters:
        sys.stderr.write("- lexikalni chyba ve zdrojovem kodu v SOL25\n")
        sys.exit(Color.LEXERR.value)
    except UnexpectedToken:
        sys.stderr.write("- syntakticka chyba ve zdrojovem kodu v SOL25\n")
        sys.exit(Color.SYNTERR.value)

    
    print(tree.pretty())  # Displays the parse tree

if __name__ == "__main__":
    main()