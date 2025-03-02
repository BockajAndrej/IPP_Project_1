import sys
import xml.etree.ElementTree as ET

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

    program: class_def*  // Allows multiple class definitions

    class_def: "class" CID ":" CID "{" method "}"

    method: ((ID | ID ":" (ID ":")*) block)*

    block: "[" (":" ID)* "|" block_stat "]"

    block_stat: (ID ":=" expr ".")*

    expr: (ID | CID | STR | int | "(" expr ")" | block) expr_tail
    expr_tail: ID | (ID ":" (ID | CID | STR | int | "(" expr ")" | block))*

    CID: /[a-zA-Z][a-zA-Z0-9_]*/   // Uppercase for token rules
    ID: /[a-zA-Z_][a-zA-Z0-9_]*/

    int : /-?\d+([eE][+-]?\d+)?/
    COMMENT: /\"(?:\\.|[^\\"])*\"/s

    %import common.ESCAPED_STRING -> STR
    %import common.WS
    %ignore COMMENT
    %ignore WS
"""

# ! Upravenie stringu aby bolo v AST strome 

class TreeToXML(Transformer):
    def __init__(self):
        self.assign_cnt = 1

    def program(self, args):
        program_element = ET.Element("program", {
            "language": "SOL25",
            "description": "- definice metody - bezparametrický selektor run"
        })
        program_element.append(args[0])  # Add the <class> element
        return program_element

    def class_def(self, args):
        class_element = ET.Element("class", {
            "name": args[0],  # Extract class name
            "parent": args[1]
        })
        class_element.append(args[2])  # Add the <method> element
        return class_element
    
    def method(self, args):
        element = ET.Element("method", {"selector": args[0]})
        element.append(args[1])
        return element

    def block(self, args):
        self.assign_cnt = 1
        element = ET.Element("block", {"arity": str(len(args)-1)})
        element.append(args[len(args)-1])
        return element
    
    def block_stat(self, args):
        i = 0
        while i < len(args):
            element_ass = ET.Element("assign", {"order":  str(self.assign_cnt)})
            self.assign_cnt += 1

            element_var = ET.Element("var", {"order":  str(args[i])})
            element_exp = ET.Element("expr")

            element_ass.append(element_var)
            element_ass.append(element_exp)
            element_exp.append(args[i+1])
            i+=2
        
        return element_ass
    
    def expr(self, args):

        selectors = []
        literals_type = []
        literals_val = []
        for item in args[1].children:
            tmp = str(item)
            if(len(find_substring(tmp, " ")) == 0):
                if(len(selectors) == 0):
                    selectors = f"{str(tmp)}:"
                else:
                    selectors = f"{selectors}{str(tmp)}:"
            else:
                literals_type.append(str(item.data.value))
                literals_val.append(str(item.children[0].value))
        
        element = ET.Element("send", {"selector": str(selectors)})

        element_exp = ET.Element("expr")
        element.append(element_exp)

        element_base = ET.Element("var", {"name": args[0]})
        element_exp.append(element_base)

        cnt = 1
        for type in literals_type:
            elem_arg = ET.Element("arg", {"order": str(cnt)})
            element.append(elem_arg)
            elem_exp = ET.Element("expr")
            elem_arg.append(elem_exp)
            elem_lit = ET.Element("literal", {"class": literal_type_convert_to_XML(type), "value": literals_val[cnt-1]})
            elem_exp.append(elem_lit)
            cnt += 1

        return element

def literal_type_convert_to_XML(type):
    if(type == "int"):
        return "Integer"
    
    return "UndefType"

def find_substring(strings, substring):
    return [s for s in strings if substring in s]

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
    except:
        sys.stderr.write("- interni chyba (neovlivnena integraci, vstupnimi soubory ci parametry prikazove radky)\n")
        sys.exit(Color.INTERNERR.value)

    # ! OUTPUT stream into file need to be removed  
    with open("./OUTPUTS/2.txt", "w") as file:
        file.write(tree.pretty())  # Displays the parse tree

    # Transform AST into XML
    transformer = TreeToXML()
    try:
        xml_tree = transformer.transform(tree)
        xml_str = ET.tostring(xml_tree, encoding="unicode")
    except:
        sys.stderr.write("- interni chyba (neovlivnena integraci, vstupnimi soubory ci parametry prikazove radky)\n")
        sys.exit(Color.INTERNERR.value)

    # Print XML
    print(xml_str)

if __name__ == "__main__":
    main()