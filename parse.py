import sys
import xml.etree.ElementTree as ET

from enum import Enum
from lark import Lark, UnexpectedCharacters, UnexpectedToken, Transformer, Visitor
from collections import defaultdict

# If debug set it to True
isdebug = False
# If it is not set input file will be from first argument
input_file = ""

KEYWORDS = {"super", "nil", "class", "self", "true", "false", "main", "Main"}
CLASS_ID = {"Object", "Nil", "True", "False", "Integer", "String", "Block"}

class OBJECT:
    def __init__(self):
        self.methods = {"identicalTo:", "equalTo:", "asString", "isNumber", "isString", "isBlock", "isNil", "new", "from"}
    
    def contain(self, value):
        return value in self.methods
class NIL(OBJECT):
    def __init__(self):
        super().__init__()
class INTEGER(OBJECT):
    def __init__(self):
        super().__init__()
        self.methods.add("greaterThan:")
        self.methods.add("plus:")
        self.methods.add("minus:")
        self.methods.add("multiplyBy:")
        self.methods.add("divBy:")
        self.methods.add("asInteger")
        self.methods.add("timesRepeat:")
class STRING(OBJECT):
    def __init__(self):
        super().__init__()
        self.methods.add("read")
        self.methods.add("print")
        self.methods.add("asInteger")
        self.methods.add("concatenateWith:")
        self.methods.add("startsWith:endsBefore:")
class BLOCK(OBJECT):
    def __init__(self):
        super().__init__()
        self.methods.add("whileTrue:")
class FALSE_TRUE(OBJECT):
    def __init__(self):
        super().__init__()
        self.methods.add("not")
        self.methods.add("and:")
        self.methods.add("or:")
        self.methods.add("ifTrue:ifFalse:")

methodsInClass = defaultdict(list)
numOfParams = defaultdict(list)
InheritanceRelations = defaultdict(list)

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

    cid: /[a-zA-Z][a-zA-Z0-9_]*/ 
    id: /[a-zA-Z_][a-zA-Z0-9_]*/
    id_dot:/[a-zA-Z_][a-zA-Z0-9_]*:/

    int_def : /-?\d+([eE][+-]?\d+)?/
    str_def : /\'(?:.)*\'/
    COMMENT: /\"(?:\\.|[^\\"])*\"/s

    %import common.WS
    %ignore COMMENT
    %ignore WS
"""
grammar_comment = """ 
    start: comment*

    comment: /"([^"\\\\]|\\\\.)*"/  // Match text inside double quotes

    %ignore /[^"]+/  // Ignore everything except double quotes
    %ignore " "  // Ignore spaces
    %ignore "\\n"  // Ignore newlines
"""

class SemanticException(Exception):
    def __init__(self, message):
        super().__init__(message)

class SyntacticException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Error(Enum):
    WRONGPARAM = 10
    INFILEERR = 11     # We will use STDIO
    OUTFILEERR = 12    # We will use STDIO
    LEXERR = 21
    SYNTERR = 22
    SEMERRMAIN = 31
    SEMERRUNDEF = 32
    SEMERRARIT = 33
    SEMERRCOLLISION = 34
    SEMERR = 35
    INTERNERR = 99

class Debug:
    def __init__(self, value, in_file):
        self.debug = value
        self.input_file = in_file 
    def read_from_input_file(self):
        with open(self.input_file, "r") as filein:
            data = filein.read()  # Displays the parse tree
        return data

class TreeToXML(Transformer):
    
    def __init__(self, description = ""):
        if(len(description) > 2):
            self.description = description[1:-1]
        else:
            self.description = description
    
    def program(self, args):
        element = ET.Element("program", {
            "language": "SOL25",
        })
        if(self.description != ""):
                element.attrib={"language": "SOL25", "description": str(self.description)}
                
        for item in args:
            element.append(item)  
        return element

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
        if(str(args[0]) == "nil"):
            return args[0], "Nil"
        elif(str(args[0]) == "true"):
            return args[0], "True"
        elif(str(args[0]) == "false"):
            return args[0], "False"
        elif(args[0] in CLASS_ID):
            return args[0], "class"
        return args[0], "identifier"
    
    def id_dot(self, args):
        return args[0], "identifier"
    
    def int_def(self, args):
        return args[0], "Integer"
    
    def str_def(self, args):
        str_args = args[0]
        str_args = str_args[1:-1]
        return str_args, "String"
    
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
        self.is_in_block = True
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
        self.is_in_block = False
        return element

    def block_par(self, args):
        return args
    
    def block_stat(self, args):
        return args

    def expr(self, args):
        element = ET.Element("expr")
        str_tail, elem_tail = args[1]
        if(str_tail != ""):
            element_send = ET.Element("send", {"selector": str_tail})
            specific_args = args[0]
            if(contains_substring(str(specific_args), "<Element 'expr'")):
                element_send.append(specific_args)
            else:
                element_expr = ET.Element("expr")
                element_expr.append(specific_args)
                element_send.append(element_expr)
            element.append(element_send)
        else:
            element.append(args[0])
        i = 0
        
        # Checking arity for send 
        if((numOfParams[str_tail] != len(elem_tail)) and (len(numOfParams[str_tail]) != 0)):
            sys.exit(print_err_by_errnum(Error.SEMERRARIT.value))
        while i < len(elem_tail):
            element_arg = ET.Element("arg", {"order": str(i+1)})
            specific_elem_tail = elem_tail[i]
            if(contains_substring(str(specific_elem_tail), "<Element 'expr'")):
                element_arg.append(specific_elem_tail)
            else:
                element_expr = ET.Element("expr")
                element_expr.append(specific_elem_tail)
                element_arg.append(element_expr)
            if(str_tail != ""):
                element_send.append(element_arg)
            else:
                element.append(element_arg)
            i+=1
        return element

    def expr_base(self, args):
        if(len(args[0]) > 1):
            val_arg, type_arg = args[0]
            if(type_arg == "identifier"):
                element_next = ET.Element("var", {"name":val_arg})
            else:
                element_next = ET.Element("literal", {"class": type_arg, "value": str(val_arg)})
            return element_next
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

class CommentTree(Transformer):
    def start(self, args):
        return args[0]

    def comment(self, args):
        return args[0]

class PrintVisitor(Visitor):        
    def class_def(self, tree):
        self.LastNameOfClass = str(tree.children[0].children[0].value)
        
        if(self.LastNameOfClass == "Main"):
            obj = OBJECT()
            for item in obj.methods:
                methodsInClass[item].append("Object")
            obj = NIL()
            for item in obj.methods:
                methodsInClass[item].append("Nil")
            obj = INTEGER()
            for item in obj.methods:
                methodsInClass[item].append("Integer")
            obj = STRING()
            for item in obj.methods:
                methodsInClass[item].append("String")
            obj = BLOCK()
            for item in obj.methods:
                methodsInClass[item].append("Block")
            obj = FALSE_TRUE()
            for item in obj.methods:
                methodsInClass[item].append("True")
                methodsInClass[item].append("False")
                
        if(self.LastNameOfClass in CLASS_ID):
            sys.exit(print_err_by_errnum(Error.SEMERR.value))
        CLASS_ID.add(self.LastNameOfClass)
        i = 0
        while i < int(len(tree.children[2].children)):
            iter = 1
            sel_str = tree.children[2].children[i].children[0].children[0].value
            while iter < len(tree.children[2].children[i].children):
                sel_str = f"{sel_str}{tree.children[2].children[i].children[iter].children[0].value}"
                iter+=1
            methodsInClass[sel_str].append(self.LastNameOfClass)
            i+=2
        
        obj = 0
        if(tree.children[1].children[0] == "Object"):
            obj = OBJECT()
        elif(tree.children[1].children[0] == "Nil"):
            obj = NIL()
        elif(tree.children[1].children[0] == "Integer"):
            obj = INTEGER()
        elif(tree.children[1].children[0] == "String"):
            obj = STRING()
        elif(tree.children[1].children[0] == "Block"):
            obj = BLOCK()
        elif((tree.children[1].children[0] == "True") or (tree.children[1].children[0] == "False")):
            obj = FALSE_TRUE()
        else:
            for key, values in InheritanceRelations.items():
                print(f"{key} == {tree.children[1].children[0]}")
                if(tree.children[1].children[0] == key):
                    print(f"{key}: {values}")
                    sys.exit(print_err_by_errnum(Error.SEMERR.value))
            InheritanceRelations[self.LastNameOfClass].append(tree.children[1].children[0])
        
        if(obj == 0):
            for item in methodsInClass:
                if(tree.children[1].children[0] in methodsInClass[item]):
                    methodsInClass[item].append(self.LastNameOfClass)
        else:    
            for item in obj.methods:
                methodsInClass[item].append(self.LastNameOfClass)
     
    def method(self, tree):
        i = 0
        while i < len(tree.children):
            iter = 0
            numberOfParams = 0
            sel_str = ""
            while iter < len(tree.children[i].children):
                if(str(tree.children[i].children[iter].data) == "id_dot"):
                    sel_str = f"{sel_str}{tree.children[i].children[iter].children[0]}"
                    numberOfParams += 1
                iter+=1
            if(sel_str == ""):
                sel_str = str(tree.children[i].children[0].children[0])
            numOfParams[sel_str] = numberOfParams
            # print(f"{sel_str} + {iter}")
            
            if(len(tree.children[i+1].children[0].children) != numOfParams[sel_str]):
                sys.exit(print_err_by_errnum(Error.SEMERRARIT.value))
            i += 2
            
class Visitor_xml:
    def __init__(self):
        self.isInsideSend = False
        self.isMain = False
        self.isRun = False
        
        self.LastNameOfClass = ""
        self.LastNameOfMethod = ""
        
        self.defined_vars = []
        self.isEnableToDefVar = False
        
        # There is no one error
        self.errNum = 0
        
    def traverse(self, element):
        self.atribut_name = ""
        # print(f"Element = {element.tag}")
        if(element.tag == "class"):
            if element.attrib['parent'] in CLASS_ID:
                if(element.attrib['name'] == "Main"):
                    if(self.isMain):
                        self.errNum = Error.SEMERRMAIN.value
                    self.isMain = True
                else:
                    self.atribut_name = element.attrib['name'] 
                self.LastNameOfClass = element.attrib['name'] 
            else:
                self.errNum = Error.SEMERRUNDEF.value
        elif(element.tag == "method"):
            if((element.attrib['selector'] == "run") and self.isMain):
                self.isRun = True
            self.atribut_name = element.attrib['selector'] 
        elif(element.tag == "assign"):
            self.isInsideSend = False
            self.isEnableToDefVar = True
        elif(element.tag == "send"):
            self.isInsideSend = True
            self.atribut_name = element.attrib['selector'] 
            self.LastNameOfMethod = element.attrib['selector'] 
        elif(element.tag == "parameter"):
            self.defined_vars.append(element.attrib['name'])
            self.atribut_name = element.attrib['name'] 
        elif(element.tag == "literal"):
            if(element.attrib['value'] != "nil" and element.attrib['value'] != "false" and element.attrib['value'] != "true"):
                self.atribut_name = element.attrib['value'] 
            # print(f"method: {self.LastNameOfMethod} class:{methodsInClass[self.LastNameOfMethod]}")
            if((element.attrib['class'] == "class")):
                if(((element.attrib['value'] in methodsInClass[self.LastNameOfMethod]) == False)):
                    self.errNum = Error.SEMERRUNDEF.value                
                    
        elif(element.tag == "var"):
            if(((element.attrib['name'] == "self") and (self.isInsideSend == False)) or (element.attrib['name'] != "self")):
                self.atribut_name = element.attrib['name'] 
            if(self.isEnableToDefVar):
                self.defined_vars.append(element.attrib['name'])
                self.isEnableToDefVar = False
            elif(((element.attrib['name'] in self.defined_vars) == False) and (element.attrib['name'] != "self")):
                self.errNum = Error.SEMERRUNDEF.value
                
        if self.atribut_name in KEYWORDS :
            raise SyntacticException("ERROR")
        elif(self.errNum != 0):
            raise SemanticException("ERROR")
        
        for child in element:
            self.traverse(child)

def contains_substring(text, substring):
    return substring in text

def print_err_by_errnum(value):
    match value:
        case Error.WRONGPARAM.value:
            sys.stderr.write("- chybejici parametr skriptu (je-li treba) nebo použiti zakazane kombinace parametru\n")
            return value
        case Error.LEXERR.value:
            sys.stderr.write("- lexikalni chyba ve zdrojovem kodu v SOL25\n")
            return value
        case Error.SYNTERR.value:
            sys.stderr.write("- syntaktická chyba ve zdrojovém kódu v SOL25\n")
            return value
        case Error.SEMERRMAIN.value:
            sys.stderr.write("- sémantická chyba - chybějící třída Main či její instanční metoda run.\n")
            return value
        case Error.SEMERRUNDEF.value:
            sys.stderr.write("- sémantická chyba - použití nedefinované (a tedy i neinicializované) proměnné, formálního parametru, třídy, nebo třídní metody.\n")
            return value
        case Error.SEMERRARIT.value:
            sys.stderr.write("- sémantická chyba arity (špatná arita bloku přiřazeného k selektoru při definici instanční\n")
            return value
        case Error.SEMERRCOLLISION.value:
            sys.stderr.write("- sémantická chyba - kolizní proměnná (lokální proměnná koliduje s formálním parametrem bloku\n")
            return value
        case Error.SEMERR.value:
            sys.stderr.write("- sémantická chyba - ostatní\n")
            return value
        case Error.INTERNERR.value:
            sys.stderr.write("- interni chyba (neovlivnena integraci, vstupnimi soubory ci parametry prikazove radky)\n")
            return value
        case _:
            sys.stderr.write("- not defined err print)\n")
            return value

def print_helping_guide():
    print("Printed helping guides")

def main():
    global isdebug
    global input_file
        
    if (isdebug):
        if(input_file == ""):
            input_file = sys.argv[1]
        debug = Debug(isdebug, input_file)
        data = debug.read_from_input_file()
    elif(len(sys.argv) == 1):
        data = sys.stdin.read()  # Read all input
    elif (len(sys.argv) == 2):
        if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
            print_helping_guide()
            sys.exit(0)
        else:
            sys.exit(print_err_by_errnum(Error.WRONGPARAM.value)) 
            
    else:
        sys.exit(print_err_by_errnum(Error.WRONGPARAM.value))

    # Create the parser
    parser = Lark(grammar, parser="lalr")
    parser_comment = Lark(grammar_comment, parser="lalr")

    try:
        tree = parser.parse(data)
        tree_comment = parser_comment.parse(data)
    except UnexpectedCharacters:
        sys.exit(print_err_by_errnum(Error.LEXERR.value))
    except UnexpectedToken:
        sys.exit(print_err_by_errnum(Error.SYNTERR.value))
    except:
        sys.exit(print_err_by_errnum(Error.INTERNERR.value))
        
    errNumber = 0

    # Helps to have overview over the AST
    if(isdebug):
        with open("./OUTPUTS/2.txt", "w") as file:
            file.write(tree_comment.pretty() + "\n")
            file.write("--------------//----------------\n")
            file.write(tree.pretty())
    # Transform AST into XML
    try:
        comment_transformer = CommentTree()
        try:
            first_comment = str(comment_transformer.transform(tree_comment))
        except:
            first_comment = ""
        
        # First preview of AST for save important information
        visitor = PrintVisitor()
        visitor.visit(tree)
        
        # Transform AST into XML
        transformer = TreeToXML(first_comment)
        xml_tree = transformer.transform(tree)
        xml_str = ET.tostring(xml_tree, encoding="unicode")
        
        # Check XML for syntax and semantics
        visitor = Visitor_xml()
        visitor.traverse(xml_tree)
        
        if((visitor.isMain == False) or (visitor.isRun == False)):
            sys.exit(print_err_by_errnum(Error.SEMERRMAIN.value))
    except SyntacticException:
        sys.exit(print_err_by_errnum(Error.SYNTERR.value))
    except SemanticException:
        sys.exit(print_err_by_errnum(visitor.errNum))
    # except :
    #     sys.exit(print_err_by_errnum(Error.INTERNERR.value))
        
    # Print XML into stdio
    print(xml_str)

if __name__ == "__main__":
    main()