# IPP - 2. úloha
# Interpret XML reprezentace kódu
# Kateřina Cibulcová (xcibul12]

import sys
import xml.etree.ElementTree as ET
import re

source = None
input_ = None


# Trida chyb

class Error:
    missing_arg = 10
    file_error_read = 11
    file_error_write = 12

    bad_XML_file = 31
    bad_XML_structure = 32

    semantic = 52
    bad_op_type = 53
    no_var = 54
    no_frame = 55
    missing_value = 56
    bad_op_value = 57
    string = 58

    internal = 99

    @staticmethod
    def error_exit(text, code):
        print("Error " + str(code) + "\n" + text)
        sys.exit(code)


# Ramce a jejich zpracovani

class Frame:
    global_frame = {}
    local_frame = None
    temp_frame = None

    frame_stack = []

    @classmethod
    def frame_add(self, frame, var):

        if frame == "GF":
            if var in self.global_frame:
                Error.error_exit("Opakovana definice promenne v jiz existujicim ramci.", Error.semantic)

            self.global_frame[var] = None

        elif frame == "LF":
            if self.local_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var in self.local_frame:
                Error.error_exit("Opakovana definice promenne v jiz existujicim ramci.", Error.semantic)

            self.local_frame[var] = None

        elif frame == "TF":
            if self.temp_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var in self.temp_frame:
                Error.error_exit("Opakovana definice promenne v jiz existujicim ramci.", Error.semantic)

            self.temp_frame[var] = None

    @classmethod
    def frame_update(self, frame, var, value, data_type):

        if frame == "GF":
            if var not in self.global_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            self.global_frame.update({var: value + ":" + data_type})

        elif frame == "LF":
            if self.local_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var not in self.local_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            self.local_frame.update({var: value + ":" + data_type})

        elif frame == "TF":
            if self.temp_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var not in self.temp_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            self.temp_frame.update({var: value + ":" + data_type})

    @classmethod
    def frame_search(self, frame, var):
        if frame == "GF":
            if var not in self.global_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            return self.global_frame.get(var)

        elif frame == "LF":
            if self.local_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var not in self.local_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            return self.local_frame.get(var)

        elif frame == "TF":
            if self.temp_frame is None:
                Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)

            if var not in self.temp_frame:
                Error.error_exit("Pokus o pristup k nedefinovane promenne.", Error.no_var)

            return self.temp_frame.get(var)

    @classmethod
    def CREATEFRAME(self):
        self.temp_frame = {}

    @classmethod
    def PUSHFRAME(self):

        if self.temp_frame is not None:
            self.frame_stack.append(self.temp_frame)

            frames = len(self.frame_stack)
            last_frame = frames - 1

            self.local_frame = self.frame_stack[last_frame]

            self.temp_frame = None
        else:
            Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)
    @classmethod
    def POPFRAME(self):

        if self.local_frame is not None:

            self.temp_frame = self.local_frame
            self.frame_stack.pop()

            frames = len(self.frame_stack)
            last_frame = frames - 1

            if last_frame < 0:
                self.local_frame = None
            else:
                self.local_frame = self.frame_stack[last_frame]

        else:
            Error.error_exit("Pokus o pristup k nedefinovanemu ramci.", Error.no_frame)


# Zpracovani argumentu pro spusteni programu
def program_args():
    global source
    global input_

    if len(sys.argv) < 2:
        Error.error_exit("Spatny pocet argumentu.", Error.missing_arg)

    if (len(sys.argv) == 2) and (sys.argv[1] == "--help"):
        print("Program nacte XML reprezentaci programu a tento program "
              "s vyuzitim vstupu dle parametru prikazove radky generuje a interpretuje vystup.\n"
              "Spusteni:\n"
              "--source=nazevsouboru\t skript interpretuje XML reprezentaci programu ze souboru\n"
              "--input=nazevsouboru\t skript interpretuje nacitani samotneho programu ze souboru\n"
              "Je nutne zadat alespon jeden z techto parametru.\n"
              "Pri nezadani daneho parametru bude skript interpretovat ze standardniho vstupu.\n")
        sys.exit(0)
    elif (len(sys.argv) == 2) and (sys.argv[1][:9] == "--source="):
        source = sys.argv[1].split("=")
        source = source[1]

    elif (len(sys.argv) == 2) and (sys.argv[1][:8] == "--input="):
        input_ = sys.argv[1].split("=")
        input_ = input_[1]

        source = sys.stdin
    elif (len(sys.argv) == 3) and (sys.argv[1][:9] == "--source=") and (sys.argv[2][:8] == "--input="):
        source = sys.argv[1].split("=")
        source = source[1]

        input_ = sys.argv[2].split("=")
        input_ = input_[1]

    elif (len(sys.argv) == 3) and (sys.argv[1][:8] == "--input=") and (sys.argv[2][:9] == "--source="):
        source = sys.argv[2].split("=")
        source = source[1]

        input_ = sys.argv[1].split("=")
        input_ = input_[1]

    else:
        Error.error_exit("Nespravne zadane argumenty.", Error.missing_arg)


# Zpracovani operandu instrukci
def counting(args):

    for arg in args:
        for arg_value in arg:
            if arg_value == "arg1":
                var = arg
            elif arg_value == "arg2":
                op1 = arg
            elif arg_value == "arg3":
                op2 = arg

    if len(args) == 3:
        ops = [var, op1, op2]

        if ops[1][1] == "var" and ops[2][1] == "var":
            op1 = Frame.frame_search(ops[1][2], ops[1][3])
            if op1 == None:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            op1 = op1.split(":")
            op1_value = op1[0]
            op1_data_type = op1[1]

            op2 = Frame.frame_search(ops[2][2], ops[2][3])
            if op2 == None:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            op2 = op2.split(":")
            op2_value = op2[0]
            op2_data_type = op2[1]
        elif ops[1][1] == "var":
            op1 = Frame.frame_search(ops[1][2], ops[1][3])
            if op1 == None:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            op1 = op1.split(":")
            op1_value = op1[0]
            op1_data_type = op1[1]

            if len(args) == 3:
                op2_value = ops[2][2]
                op2_data_type = ops[2][1]
        elif ops[2][1] == "var":
            op2 = Frame.frame_search(ops[2][2], ops[2][3])
            if op2 == None:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            op2 = op2.split(":")
            op2_value = op2[0]
            op2_data_type = op2[1]

            op1_value = ops[1][2]
            op1_data_type = ops[1][1]
        else:
            op1_value = ops[1][2]
            op1_data_type = ops[1][1]
            op2_value = ops[2][2]
            op2_data_type = ops[2][1]
    else:
        ops = [var, op1]

        if ops[1][1] == "var":
            op1 = Frame.frame_search(ops[1][2], ops[1][3])
            if op1 == None:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            op1 = op1.split(":")
            op1_value = op1[0]
            op1_data_type = op1[1]

        else:
            op1_value = ops[1][2]
            op1_data_type = ops[1][1]

    if len(args) == 3:
        ops = [var, op1_value, op2_value, op1_data_type, op2_data_type]
    else:
        ops = [var, op1_value, op1_data_type]

    return ops

# Zpracovani operandu instrukci se dvěma argumenty

def inp(args):
    for arg in args:
        for arg_value in arg:
            if arg_value == "arg1":
                var = arg
            elif arg_value == "arg2":
                symb = arg

    if symb[1] == "var":
        symb = Frame.frame_search(symb[2], symb[3])
        if not symb:
            symb_value = None
            symb_data_type = None
        else:
            symb = symb.split(":")
            symb_value = symb[0]
            symb_data_type = symb[1]
    else:
        symb_value = symb[2]
        symb_data_type = symb[1]

    params = [var, symb_value, symb_data_type]
    return params


# Zpracovani argumentu instrukci a kontroly regularnich vyrazu

def args(instruction):
    list_of_arglists = []
    data_types = ["int", "string", "bool", "nil"]

    for arg in instruction:

        if arg.attrib is not None:
            arg_order = arg.tag
            arg_type = arg.attrib.get("type")

            if not re.match(r'^(\w*arg\w*)[1-3]$', arg_order):
                Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)

            # Kontrola jmena promenne
            if arg_type == "var":
                if arg.text is None:
                    Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)

                processed_arg = re.split("@", arg.text)
                arg_frame = processed_arg[0]
                arg_name = processed_arg[1]

                frames = ["GF", "LF", "TF"]
                # Kontrola jmena ramce
                if arg_frame not in frames:
                    Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)

                if not re.match(r"^[a-zA-Z_$&%*!?]+[0-9]*$", arg_name):
                    Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)

                arg_list = [arg_order, arg_type, arg_frame, arg_name]
            elif arg_type == "label":
                if arg.text is None:
                    Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)
                arg_name = arg.text

                # Kontrola jmena labelu
                if not re.match(r"^[a-zA-Z_$&%*!?]+[0-9]*$", arg_name):
                    Error.error_exit("Neplatna struktura XML.", Error.bad_XML_structure)

                arg_list = [arg_order, arg_type, arg_name]

            elif arg_type in data_types:

                #Kontrola syntaxe datovych typu
                if arg_type == "string":
                    if arg.text is None:
                        arg.text = ""
                    else:
                        if re.match(r"^[\s#\\]+$", arg.text):
                            Error.error_exit("Neplatna struktura XML.", Error.bad_XML_structure)
                        else:
                            escape = re.search(r"\\\d\d\d",arg.text)
                            if escape:
                                while escape:
                                    numb = escape.group()[1:]
                                    numb = int(numb)
                                    char = chr(numb)
                                    arg.text = re.sub(r"\\\d\d\d", char, arg.text, count=1)
                                    escape = re.search(r"\\\d\d\d", arg.text)
                elif arg_type == "int":
                    if arg.text is None:
                        Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)
                    if not re.match(r"^[-+]?\d+$", arg.text):
                        Error.error_exit("Neplatna struktura XML.", Error.bad_XML_structure)
                elif arg_type == "bool":
                    if arg.text is None:
                        Error.error_exit("Neplatna struktura XML kodu.", Error.bad_XML_structure)
                    if arg.text != "true" and arg.text != "false":
                        Error.error_exit("Neplatna struktura XML.", Error.bad_XML_structure)
                elif arg_type == "nil":
                    if arg.text is None:
                        arg_value = "nil"

                arg_value = arg.text
                arg_list = [arg_order, arg_type, arg_value]

            elif arg_type == "type":
                arg_value = arg.text
                arg_list = [arg_order, arg_type, arg_value]
            else:
                Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)
        else:
                Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        # List argumentu dane promenne
        list_of_arglists.append(arg_list)

    return list_of_arglists


# Trida pro zpracovani instrukci

class Instruction:

    loaded_instructions = []

    def MOVE(self, args):
        params = inp(args)

        var = params[0]
        symb_value = params[1]
        symb_data_type = params[2]

        if symb_data_type is None:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if symb_data_type == "nil":
            Frame.frame_update(var[2], var[3], "", symb_data_type)
        else:
            Frame.frame_update(var[2], var[3], symb_value, symb_data_type)

    def DEFVAR(self, args):

        for arg in args:
            Frame.frame_add(arg[2], arg[3])

    def ADD(self, args):
        ops = counting(args)
        if len(ops) != 5:
            Frame.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if ops[3] == ops[4]:
            if ops[4] == "int":
                result = int(ops[1]) + int(ops[2])
                result = str(result)
            else:
                Error.error_exit("Spatne typy operandu.", Error.bad_op_type)
        else:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def SUB(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if ops[3] == ops[4]:
            if ops[4] == "int":
                result = int(ops[1]) - int(ops[2])
                result = str(result)
        else:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def MUL(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if ops[3] == ops[4]:
            if ops[4] == "int":
                result = int(ops[1]) * int(ops[2])
                result = str(result)
        else:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def IDIV(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if ops[3] == ops[4]:
            if ops[4] == "int":
                if int(ops[2]) == 0:
                    Error.error_exit("Spatna hodnota operandu: deleni nulou.", Error.bad_op_value)
                else:
                    result = int(ops[1]) // int(ops[2])
                    result = str(result)
        else:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def LT(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        op1 = ops[1]
        op2 = ops[2]

        if ops[3] != ops[4]:
            Error.error_exit("Rozdilne typy operandu", Error.bad_op_type)

        if ops[3] == "int":
            if int(op1) < int(op2):
                result = "true"
            else:
                result = "false"
        elif ops[3] == "bool":
            if op1 == "false" and op2 == "true":
                result = "true"
            else:
                result = "false"
        elif ops[3] == "string":
            if op1 < op2:
                result = "true"
            else:
                result = "false"
        else:
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, "bool")

    def GT(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op2 = ops[2]

        if ops[3] != ops[4]:
            Error.error_exit("Rozdilne typy operandu", Error.bad_op_type)

        if ops[3] == "int":
            if int(op1) > int(op2):
                result = "true"
            else:
                result = "false"
        elif ops[3] == "bool":
            if op1 == "true" and op2 == "false":
                result = "true"
            else:
                result = "false"
        elif ops[3] == "string":
            if op1 > op2:
                result = "true"
            else:
                result = "false"
        else:
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        Frame.frame_update(ops[0][2], ops[0][3], result, "bool")

    def EQ(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op2 = ops[2]

        if (ops[3] != ops[4]) and (ops[3] != "nil" and ops[4] != "nil"):
            Error.error_exit("Rozdilne typy operandu", Error.bad_op_type)

        if ops[3] == ops[4] == "int":
            if int(op1) == int(op2):
                result = "true"
            else:
                result = "false"
        elif ops[3] == ops[4] == "bool":
            if op1 == "true" and op2 == "true":
                result = "true"
            elif op1 == "false" and op2 == "false":
                result = "true"
            else:
                result = "false"
        elif ops[3] == ops[4] =="string":
            if op1 == op2:
                result = "true"
            else:
                result = "false"
        else:
            if ops[3] == ops[4] == "nil":
                result = "true"
            else:
                result = "false"

        Frame.frame_update(ops[0][2], ops[0][3], result, "bool")

    def AND(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op2 = ops[2]

        if ops[3] != ops[4]:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)
        elif ops[3] != "bool":
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        if (op1 != "true" and op1 != "false") or (op2 != "true" and op2 != "false"):
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if op1 == "true" or op1 == "True":
            op1 = True
        else:
            op1 = False

        if op2 == "true" or op2 == "True":
            op2 = True
        else:
            op2 = False

        result = str(op1 and op2)
        result = result.lower()
        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def NOT(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 3:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]

        if ops[2] != "bool":
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)

        if op1 != "true" and op1 != "false":
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if op1 == "true" or op1 == "True":
            op1 = True
        else:
            op1 = False

        result = str(not op1)
        result = result.lower()
        Frame.frame_update(ops[0][2], ops[0][3], result, ops[2])

    def OR(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op2 = ops[2]

        if ops[3] != ops[4]:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)
        elif ops[3] != "bool":
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        if (op1 != "true" and op1 != "false") or (op2 != "true" and op2 != "false"):
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if op1 == "true" or op1 == "True":
            op1 = True
        else:
            op1 = False

        if op2 == "true" or op2 == "True":
            op2 = True
        else:
            op2 = False

        result = str(op1 or op2)
        result = result.lower()
        Frame.frame_update(ops[0][2], ops[0][3], result, ops[4])

    def INT2CHAR(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 3:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op1_data_type = ops[2]

        if op1_data_type != "int":
            Error.error_exit("Chybny typ operandu.", Error.bad_op_type)

        if int(op1) < 0:
            Error.error_exit("Spatna operace s retezcem.", Error.string)

        try:
            result = chr(int(op1))
        except ValueError:
            Error.error_exit("Chybna hodnota operandu.", Error.string)

        Frame.frame_update(ops[0][2], ops[0][3], result, "string")

    def STR2INT(self, args):
        ops = counting(args)

        if None in ops:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(ops) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        op1 = ops[1]
        op2 = ops[2]

        if (ops[4] != "int") or (ops[3] != "string"):
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if int(op2) > (len(op1) - 1):
            Error.error_exit("Chybna hodnota operandu.", Error.string)

        if int(op2) < 0:
            Error.error_exit("Chybna hodnota operandu.", Error.string)

        try:
            result = str(ord(op1[int(op2)]))
        except TypeError:
            Error.error_exit("Chybna hodnota operandu.", Error.string)

        Frame.frame_update(ops[0][2], ops[0][3], result, "int")

    def READ(self, args):
        params = inp(args)

        data_type = params[1]

        types = ["string", "int", "bool"]
        if data_type not in types:
            Error.error_exit("Spatna hodnota operandu.", Error.bad_op_value)

        try:
            value = input()
        except EOFError:
            value = "nil"
            data_type = "nil"

        if data_type == "int":
            try:
                int(value)
            except:
                data_type = "nil"
                value = "nil"
        elif data_type == "string":
            value = str(value)
        elif data_type == "bool":
            if value.lower() == "true":
                value = "true"
            else:
                value = "false"

        Frame.frame_update(params[0][2], params[0][3], value, data_type)

    def WRITE(self, args):
        for arg in args:
            for arg_value in arg:
                if arg_value == "arg1":
                    symb = arg

        if symb[1] == "var":
            var = Frame.frame_search(symb[2], symb[3])
            if not var:
                Error.error_exit("V promenne se nenachazi zadna hodnota.", Error.missing_value)
            var = var.split(":")
            var_value = var[0]
            if var[1] == "nil":
                var_value = ""

        else:
            var_value = symb[2]
            if symb[1] == "nil":
                var_value = ""

        print(var_value, end="")

    def CONCAT(self, args):
        params = counting(args)

        if None in params:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(params) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        str1 = params[1]
        str2 = params[2]

        if params[3] != params[4]:
            Error.error_exit("Spatne typy operandu.", Error.bad_op_type)
        elif params[3] != "string":
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        concat = str1 + str2
        Frame.frame_update(params[0][2], params[0][3], concat, params[4])

    def GETCHAR(self, args):
        params = counting(args)

        if None in params:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(params) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        str1 = params[1]
        str2 = params[2]

        if params[3] != "string" or params[4] != "int":
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if int(str2) < 0:
            Error.error_exit("Spatna operace s retezcem.", Error.string)

        if int(str2) > (len(str1) - 1):
            Error.error_exit("Spatna operace s retezcem.", Error.string)

        char = str1[int(str2)]
        Frame.frame_update(params[0][2], params[0][3], char, params[3])

    def SETCHAR(self, args):
        params = counting(args)

        if None in params:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)

        if len(params) != 5:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        str1 = params[1]
        str2 = params[2]
        if str2 == "":
            Error.error_exit("Spatna operace s retezcem.", Error.string)
        str2 = str2[0]

        var = Frame.frame_search(params[0][2], params[0][3])
        if not var:
            Error.error_exit("Chybejici hodnota.", Error.missing_value)
        var = var.split(":")
        var_data_type = var[1]
        var_value = var[0]

        if var_data_type != "string" or params[3] != "int" or params[4] != "string":
            Error.error_exit("Chybne typy operandu.", Error.bad_op_type)

        if int(str1) > (len(var_value) - 1):
            Error.error_exit("Spatna operace s retezcem.", Error.string)

        if int(str1) < 0:
            Error.error_exit("Spatna operace s retezcem.", Error.string)

        string = var_value.replace(var_value[int(str1)], str2)
        Frame.frame_update(params[0][2], params[0][3], string, params[4])

    def STRLEN(self, args):
        for arg in args:
            for arg_value in arg:
                if arg_value == "arg1":
                    var = arg
                elif arg_value == "arg2":
                    symb = arg

        if symb[1] == "var":
            symb = Frame.frame_search(symb[2], symb[3])
            if not symb:
                Error.error_exit("V promenne se nenachazi zadna hodnota.", Error.missing_value)
            symb = symb.split(":")
            symb_value = symb[0]
            symb_data_type = symb[1]
        else:
            symb_value = symb[2]
            symb_data_type = symb[1]

        if symb_data_type != "string":
            Error.error_exit("Spatny typ operandu.", Error.bad_op_type)

        length = str(len(symb_value))
        Frame.frame_update(args[0][2], args[0][3], length, "int")

    def TYPE(self, args):
        params = inp(args)

        var = params[0]
        symb = params[2]
        symb_data_type = "string"

        if not symb:
            symb = ""
            symb_data_type = "string"

        Frame.frame_update(var[2], var[3], symb, symb_data_type)


# Zasobnikove instrukce

class Stack:
    value_stack = []
    @classmethod
    def PUSHS(self, args):
        if args[0][1] == "var":
            var = Frame.frame_search(args[0][2], args[0][3])
            if not var:
                Error.error_exit("Chybejici hodnota.", Error.missing_value)
            var = var.split(":")
            value = var[0]
            data_type = var[1]
        else:
            value = args[0][2]
            data_type = args[0][1]

        self.value_stack.append(value + ":" + data_type)
    @classmethod
    def POPS(self, args):
        if len(self.value_stack) == 0:
            Error.error_exit("Na datovem zasobniku neni ulozena zadna hodnota.", Error.missing_value)

        frame = args[0][2]
        var = args[0][3]
        last_value = len(self.value_stack) - 1

        Frame.frame_update(frame, var, self.value_stack[last_value], args[0][1])
        self.value_stack.pop()


# Nalezeni vsech navesti v instrukcich
class Label:

    labels = {}

    @classmethod
    def find_labels(self, instructions):
        for order in instructions:
            instruction = instructions.get(order)
            for label in instruction:
                if label == "LABEL":
                    args = instruction.get(label)
                    label_name = args[0][2]
                    if label_name in self.labels.values():
                            Error.error_exit("Redefenice navesti.", Error.semantic)
                    else:
                        self.labels[order] = label_name


# Funkce pro vykonani programu
def execute(instructions):
    Instrukce = Instruction()

    call_stack = []
    Label.find_labels(instructions)

    x = 1
    y = len(instructions)
    max_order = max(instructions)

    while y > 0:
        # Interni citac instrukci
        next_order = x

        if next_order not in instructions:
            x += 1
            if x > max_order:
                break
            else:
                continue

        next_instruction = instructions.get(next_order)
        instruction_tuple = (next_order, next_instruction)

        if instruction_tuple in Instrukce.loaded_instructions:
            y += 1

        Instrukce.loaded_instructions.append(instruction_tuple)

        for elem in next_instruction:
            opcode = elem
            args = next_instruction.get(opcode)

        opcode = opcode.upper()

        if opcode == "DEFVAR":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Instrukce.DEFVAR(args)
        elif opcode == "MOVE":
            if len(args) != 2:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Instrukce.MOVE(args)
        elif opcode == "CREATEFRAME":
            if len(args) != 0:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Frame.CREATEFRAME()
        elif opcode == "PUSHFRAME":
            if len(args) != 0:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Frame.PUSHFRAME()
        elif opcode == "POPFRAME":
            if len(args) != 0:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Frame.POPFRAME()
        elif opcode == "CALL":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            call_stack.append(next_order)

            for arg in args:
                for arg_value in arg:
                    if arg_value == "arg1":
                        call_arg = arg

            jump_name = call_arg[2]
            if jump_name not in Label.labels.values():
                Error.error_exit("Navesti neexistuje.", Error.semantic)

            for label in Label.labels:
                lab_name = Label.labels.get(label)
                lab_order = label

                if lab_name == jump_name:
                    break

            x = lab_order
            y -= 1
            continue
        elif opcode == "RETURN":
            if len(call_stack) == 0:
                Error.error_exit("V zasobniku volani neni zadna hodnota.", Error.missing_value)

            return_value = call_stack[-1]
            call_stack.pop()

            x = return_value + 1
            y -= 1
            continue
        elif opcode == "PUSHS":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Stack.PUSHS(args)
        elif opcode == "POPS":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Stack.POPS(args)
        elif opcode == "ADD":
            Instrukce.ADD(args)
        elif opcode == "SUB":
            Instrukce.SUB(args)
        elif opcode == "MUL":
            Instrukce.MUL(args)
        elif opcode == "IDIV":
            Instrukce.IDIV(args)
        elif opcode == "LT":
            Instrukce.LT(args)
        elif opcode == "GT":
            Instrukce.GT(args)
        elif opcode == "EQ":
            Instrukce.EQ(args)
        elif opcode == "AND":
            Instrukce.AND(args)
        elif opcode == "OR":
            Instrukce.OR(args)
        elif opcode == "NOT":
            Instrukce.NOT(args)
        elif opcode == "INT2CHAR":
            Instrukce.INT2CHAR(args)
        elif opcode == "STRI2INT":
            Instrukce.STR2INT(args)
        elif opcode == "READ":
            Instrukce.READ(args)
        elif opcode == "WRITE":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            Instrukce.WRITE(args)
        elif opcode == "CONCAT":
            Instrukce.CONCAT(args)
        elif opcode == "STRLEN":
            Instrukce.STRLEN(args)
        elif opcode == "GETCHAR":
            Instrukce.GETCHAR(args)
        elif opcode == "SETCHAR":
            Instrukce.SETCHAR(args)
        elif opcode == "TYPE":
            Instrukce.TYPE(args)
        elif opcode == "LABEL":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)
            pass
        elif opcode == "JUMP":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

            for arg in args:
                for arg_value in arg:
                    if arg_value == "arg1":
                        jump_arg = arg

            jump_name = jump_arg[2]
            if jump_name not in Label.labels.values():
                Error.error_exit("Navesti neexistuje.", Error.semantic)

            for label in Label.labels:
                lab_name = Label.labels.get(label)
                lab_order = label

                if lab_name == jump_name:
                    equals = True
                    break

            if equals:
                equals = False
                x = lab_order
                y -= 1
                continue
            else:
                pass
        elif opcode == "JUMPIFEQ":
            equals = False
            if len(args) != 3:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

            for arg in args:
                for arg_value in arg:
                    if arg_value == "arg1":
                        label = arg
                    elif arg_value == "arg2":
                        symb1 = arg
                    elif arg_value == "arg3":
                        symb2 = arg

            jump_name = label[2]

            if jump_name not in Label.labels.values():
                Error.error_exit("Navesti neexistuje.", Error.semantic)

            if symb1[1] == "var":
                symb1 = Frame.frame_search(symb1[2], symb1[3])
                if not symb1:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb1 = symb1.split(":")
                symb1_value = symb1[0]
                symb1_data_type = symb1[1]

                symb2_value = symb2[2]
                symb2_data_type = symb2[1]
            elif symb2[1] == "var":
                symb2 = Frame.frame_search(symb2[2], symb2[3])
                if not symb2:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb2 = symb2.split(":")
                symb2_value = symb2[0]
                symb2_data_type = symb2[1]

                symb1_value = symb1[2]
                symb1_data_type = symb1[1]
            elif symb1[1] == "var" and symb2[1] == "var":
                symb1 = Frame.frame_search(symb1[2], symb1[3])
                if not symb1:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb1 = symb1.split(":")
                symb1_value = symb1[0]
                symb1_data_type = symb1[1]

                symb2 = Frame.frame_search(symb2[2], symb2[3])
                if not symb2:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb2 = symb2.split(":")
                symb2_value = symb2[0]
                symb2_data_type = symb2[1]
            else:
                symb1_value = symb1[2]
                symb1_data_type = symb1[1]

                symb2_value = symb2[2]
                symb2_data_type = symb2[1]

            if symb1_data_type == "nil" or symb2_data_type == "nil" :
                if symb1_data_type == symb2_data_type == "nil":
                    if symb1_value == symb2_value:
                        for label in Label.labels:
                            lab_name = Label.labels.get(label)
                            lab_order = label

                            if lab_name == jump_name:
                                equals = True
                                break
            elif symb1_data_type == symb2_data_type:
                if symb1_value == symb2_value:
                    for label in Label.labels:
                        lab_name = Label.labels.get(label)
                        lab_order = label

                        if lab_name == jump_name:
                            equals = True
                            break
            else:
                Error.error_exit("Neplatne operandy.", Error.bad_op_type)

            if equals:
                equals = False
                x = lab_order
                y -= 1
                continue
            else:
                pass
        elif opcode == "JUMPIFNEQ":
            equals = False
            if len(args) != 3:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

            for arg in args:
                for arg_value in arg:
                    if arg_value == "arg1":
                        label_jumpifneq = arg
                    elif arg_value == "arg2":
                        symb1 = arg
                    elif arg_value == "arg3":
                        symb2 = arg

            jump_name = label_jumpifneq[2]
            if jump_name not in Label.labels.values():
                Error.error_exit("Navesti neexistuje.", Error.semantic)

            if symb1[1] == "var":
                symb1 = Frame.frame_search(symb1[2], symb1[3])
                if not symb1:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb1 = symb1.split(":")
                symb1_value = symb1[0]
                symb1_data_type = symb1[1]

                symb2_value = symb2[2]
                symb2_data_type = symb2[1]
            elif symb2[1] == "var":
                symb2 = Frame.frame_search(symb2[2], symb2[3])
                if not symb2:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb2 = symb2.split(":")
                symb2_value = symb2[0]
                symb2_data_type = symb2[1]

                symb1_value = symb1[2]
                symb1_data_type = symb1[1]
            elif symb1[1] == "var" and symb2[1] == "var":
                symb1 = Frame.frame_search(symb1[2], symb1[3])
                if not symb1:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb1 = symb1.split(":")
                symb1_value = symb1[0]
                symb1_data_type = symb1[1]

                symb2 = Frame.frame_search(symb2[2], symb2[3])
                if not symb2:
                    Error.error_exit("Chybejici promenna.", Error.missing_value)
                symb2 = symb2.split(":")
                symb2_value = symb2[0]
                symb2_data_type = symb2[1]
            else:
                symb1_value = symb1[2]
                symb1_data_type = symb1[1]

                symb2_value = symb2[2]
                symb2_data_type = symb2[1]

            if symb1_data_type == "nil" or symb2_data_type == "nil":
                if symb1_data_type != symb2_data_type:
                    for label in Label.labels:
                        lab_name = Label.labels.get(label)
                        lab_order = label

                        if lab_name == jump_name:
                            equals = True
                            break
            elif symb1_data_type == symb2_data_type:
                if symb1_value != symb2_value:
                    for label in Label.labels:
                        lab_name = Label.labels.get(label)
                        lab_order = label

                        if lab_name == jump_name:
                            equals = True
                            break
            else:
                Error.error_exit("Neplatne operandy.", Error.bad_op_type)

            if equals:
                equals = False
                x = lab_order
                y -= 1
                continue
            else:
                pass
        elif opcode == "EXIT":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

            if args[0][1] == "var":
                var = Frame.frame_search(args[0][2], args[0][3])
                if not var:
                    Error.error_exit("Chybejici hodnota.", Error.missing_value)
                var_ = var.split(":")
                code = var_[0]
                if var_[1] != "int":
                    Error.error_exit("Spanty typ operandu.", Error.bad_op_type)
            else:
                code = args[0][2]
                if args[0][1] != "int":
                    Error.error_exit("Spanty typ operandu.", Error.bad_op_type)

            if int(code) not in range(50):
                Error.error_exit("Spatna hodnota operandu.", Error.bad_op_value)
            else:
                sys.exit(int(code))
        elif opcode == "DPRINT":
            if len(args) != 1:
                Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

            pass
        elif opcode == "BREAK":
            pass
        else:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        y -= 1
        x += 1


# Hlavni funkce programu

def main():
    global source
    global input_

    program_args()

    if input_ is not None:
        try:
            sys.stdin = open(input_, "r")
        except IOError:
            Error.error_exit("Chyba pri otevirani souboru.", Error.file_error_read)

    try:
        tree = ET.parse(source)
    except ET.ParseError:
        Error.error_exit("Nevalidni XML soubor.", Error.bad_XML_file)

    root = tree.getroot()

    instructions = {}
    orders = []

    for instruction in root:
        # Kontrola validity XML struktury souboru
        if root.tag != "program":
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if len(root.attrib) == 0:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if instruction.tag != "instruction":
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if len(instruction.attrib) != 2:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        if "language" in root.attrib:
            if root.attrib["language"].lower() != "ippcode21":
                Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)
        else:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        # Nacteni potrebnych informaci z XML souboru
        opcode = (instruction.get("opcode"))
        order = (instruction.get("order"))

        orders.append(order)

        if not order.isdigit():
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        order = int(order)
        if order <= 0:
            Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

        arguments = args(instruction)

        if len(arguments) == 1:
            if arguments[0][0] != "arg1":
                    Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

        if len(arguments) > 3:
            Error.error_exit("Neplatna sturktura XML souboru.", Error.bad_XML_structure)

        instruction = {opcode: arguments}
        instructions[order] = instruction

    if len(orders) > len(set(orders)):
        Error.error_exit("Neplatna struktura XML souboru.", Error.bad_XML_structure)

    if len(instructions) == 0:
        sys.exit(0)

    sorted_instructions = {}

    for elem in sorted(instructions.items()):

        sorted_instructions[elem[0]] = elem[1]

    execute(sorted_instructions)


main()
