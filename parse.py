import sys
import xml.etree.ElementTree as ET

from enum import Enum
from lark import Lark, UnexpectedCharacters, UnexpectedToken, Transformer

# If debug set it to True
isdebug = False
# If it is not set input file will be from first argument
input_file = ""

class Error(Enum):
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

    class_def: "class" cid ":" cid "{" method "}"

    method: (selector block)*

    selector: id | id_dot (id_dot)*

    block: "[" block_par "|" block_stat "]"
    block_par: (":" id)*
    block_stat: (id ":=" expr ".")*

    expr: expr_base expr_tail
    expr_base: id | cid | str_def | int_def | "(" expr ")" | block
    expr_tail: id | (id_dot expr_base)*

    cid: /[a-zA-Z][a-zA-Z0-9_]*/   // Uppercase for token rules
    id: /[a-zA-Z_][a-zA-Z0-9_]*/
    id_dot:/[a-zA-Z_][a-zA-Z0-9_]*:/

    int_def : /-?\d+([eE][+-]?\d+)?/
    str_def : /\'(?:\\.|[^\\"])*\'/
    COMMENT: /\"(?:\\.|[^\\"])*\"/s

    %import common.WS
    %ignore COMMENT
    %ignore WS
"""

class Debug:
    def __init__(self, value, in_file):
        self.debug = value
        self.input_file = in_file 
    def read_from_input_file(self):
        with open(self.input_file, "r") as filein:
            data = filein.read()  # Displays the parse tree
        return data

class TreeToXML(Transformer):
    def program(self, args):
        program_element = ET.Element("program", {
            "language": "SOL25",
            "description": "- definice metody - bezparametrický selektor run"
        })
        program_element.append(args[0])  # Add the <class> element
        return program_element

    def class_def(self, args):
        class_element = args[2] 
        class_element.attrib = {
            "name": args[0],
            "parent": args[1]
        }
        return class_element

    def cid(self, args):
        return args[0]
    
    def id(self, args):
        return args[0], "identifier"
    
    def id_dot(self, args):
        return args[0], "identifier"
    
    def int_def(self, args):
        return args[0], "Integer"
    
    def str_def(self, args):
        return args[0], "String"
    
    def method(self, args):
        class_element = ET.Element("class")
        
        i = 0
        while i+1 < len(args):
            element = ET.Element("method", {"selector": args[i]})
            element.append(args[i+1])
            i+=2
            class_element.append(element)
            
        return class_element
    
    def selector(self, args):
        element = ""
        for item in args:
            val_arg, type_arg = item
            element = f"{element}{str(val_arg)}"
        return element

    def block(self, args):
        params = args[0]
        element = ET.Element("block", {"arity": str(len(params))})
        i = 1
        for item in params:
            val_arg, type_arg = item
            element_param = ET.Element("parameter", {"order":str(i), "name":str(val_arg)})
            element.append(element_param)
            i+=1
        i = 0
        step = 1
        args_args = args[1]
        while i < len(args_args):
            element_ass = ET.Element("assign", {"order": str(step)})
            val_arg, type_arg = args_args[i]
            element_var = ET.Element("var", {"name": str(val_arg)})
            element_ass.append(element_var)
            element_ass.append(args_args[i+1])
            element.append(element_ass)
            i+=2
            step+=1
        return element

    def block_par(self, args):
        return args
    
    def block_stat(self, args):
        return args

    def expr(self, args):
        element = ET.Element("expr")
        str_tail, elem_tail = args[1]
        element_send = ET.Element("send", {"selector": str_tail})
        element.append(element_send)
        element_send.append(args[0])
        i = 0
        while i < len(elem_tail):
            element_arg = ET.Element("arg", {"order": str(i+1)})
            element_arg.append(elem_tail[i])
            element_send.append(element_arg)
            i+=1
        return element

    def expr_base(self, args):
        element = ET.Element("expr")
        if(len(args[0]) > 1):
            val_arg, type_arg = args[0]
            if(type_arg == "identifier"):
                element_next = ET.Element("var", {"name":val_arg})
            else:
                element_next = ET.Element("literal", {"class": type_arg, "value": str(val_arg)})
            element.append(element_next)
            return element
        elif(contains_substring(str(args[0]), "Element 'block'")):
            element.append(args[0])
            return element
        return args[0]
        
    def expr_tail(self, args):
        selector_str = ""
        element = []
        for item in args:            
            if(len(item) > 1):
                val_arg, type_arg = item
                selector_str = f"{selector_str}{val_arg}"
            else:
                element.append(item)
        return selector_str, element

def contains_substring(text, substring):
    return substring in text

def print_err_by_errnum(value):
    match value:
        case Error.WRONGPARAM.value:
            sys.stderr.write("- chybejici parametr skriptu (je-li treba) nebo použiti zakazane kombinace parametru\n")
            return
        case 2:
            sys.stderr.write("- lexikalni chyba ve zdrojovem kodu v SOL25\n")
            return
        case 3:
            sys.stderr.write("- syntakticka chyba ve zdrojovem kodu v SOL25\n")
            return
        case 4:
            sys.stderr.write("- interni chyba (neovlivnena integraci, vstupnimi soubory ci parametry prikazove radky)\n")
            return
        case _:
            return

def main():
    global isdebug
    global input_file
    
    if ((len(sys.argv) > 1) & (isdebug == False)):
        print_err_by_errnum(Error.WRONGPARAM.value)
        sys.exit(Error.WRONGPARAM.value)
    elif (isdebug):
        if(input_file == ""):
            input_file = sys.argv[1]
        debug = Debug(isdebug, input_file)
        data = debug.read_from_input_file()
    else:
        data = sys.stdin.read()  # Read all input

    # Create the parser
    parser = Lark(grammar, parser="lalr")

    try:
        tree = parser.parse(data)
    except UnexpectedCharacters:
        print_err_by_errnum(Error.LEXERR.value)
        sys.exit(Error.LEXERR.value)
    except UnexpectedToken:
        print_err_by_errnum(Error.SYNTERR.value)
        sys.exit(Error.SYNTERR.value)
    except:
        print_err_by_errnum(Error.INTERNERR.value)
        sys.exit(Error.INTERNERR.value)

    # Helps to have overview over the AST
    if(isdebug):
        with open("./OUTPUTS/2.txt", "w") as file:
            file.write(tree.pretty())  # Displays the parse tree
        transformer = TreeToXML()
        xml_tree = transformer.transform(tree)
        xml_str = ET.tostring(xml_tree, encoding="unicode")
    # Transform AST into XML
    else:
        try:
            transformer = TreeToXML()
            xml_tree = transformer.transform(tree)
            xml_str = ET.tostring(xml_tree, encoding="unicode")
        except:
            print_err_by_errnum(Error.INTERNERR.value)
            sys.exit(Error.INTERNERR.value)

    # Print XML into stdio
    print(xml_str)

if __name__ == "__main__":
    main()