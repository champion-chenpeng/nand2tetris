class CodeWriter:
    def __init__(self, file):
        self.file = file
        self.writter = open(file.replace(".vm", ".asm"), "w")
        self.initRAM()
        self.dict_RAM = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "R5", "pointer": "THIS"}
        self.dict_op = {"add": "+", "sub": "-", "and": "&", "or": "|", "neg": "-", "not": "!"}
        self.list_pointer = ["local", "argument", "this", "that"]
        self.list_single = ["neg", "not"]
        self.list_compare = ["eq", "gt", "lt"]
        self.NCompare= 0
    
    def close(self):
        self.endLoop()
        self.writter.close()
    
    def initRAM(self):
        # self.clearRAM()
        self.writter.write("@256\n")
        self.writter.write("D=A\n")
        self.writter.write("@SP\n")
        self.writter.write("M=D\n")

    def endLoop(self):
        self.writter.write("(END)\n")
        self.writter.write("@END\n")
        self.writter.write("0;JMP\n")
    
    def writePushD(self):
        self.writter.write("@SP\n")
        self.writter.write("A=M\n")
        self.writter.write("M=D\n")
        self.writter.write("@SP\n")
        self.writter.write("M=M+1\n")

    def writePopD(self):
        self.writePopM()
        self.writter.write("D=M\n")
    
    def writePopM(self):
        self.writter.write("@SP\n")
        self.writter.write("M=M-1\n")
        self.writter.write("A=M\n")

    def AddressI(self, arg1, arg2): # A = &I
        if arg1 == "static":
            self.writter.write("@" + self.file[:-2] + arg2 + "\n") # filename.arg2
        else:
            self.writter.write("@" + arg2 + "\n")
            self.writter.write("D=A\n")
            if arg1 in self.dict_RAM:
                self.writter.write("@" + self.dict_RAM[arg1] + "\n")
                if arg1 in self.list_pointer:
                    self.writter.write("A=M\n")
                self.writter.write("A=D+A\n") 

    def writePushPop(self, commandType, arg1, arg2):
        # push: I -> D -> SP
        # pop: SP -> T -> I(T_ -> A)
        if commandType == "C_PUSH":
            self.AddressI(arg1, arg2) # D is messed up
            if arg1 != "constant":
                self.writter.write("D=M\n") # D reclared
            self.writePushD() # A is messed up
        elif commandType == "C_POP":
            self.AddressI(arg1, arg2)
            # store A in R13
            self.writter.write("D=A\n")
            self.writter.write("@R13\n")
            self.writter.write("M=D\n")
            self.writePopD() # D ready
            # @T = D
            self.writter.write("@R13\n")
            self.writter.write("A=M\n")
            self.writter.write("M=D\n")

    def writeGetArgs(self, command):
        self.writePopD()
        if command not in self.list_single:
            self.writePopM()

    def writeCompare(self, command):
        self.writter.write("D=M-D\n")
        self.writter.write("@TRUE_COMPARE" + str(self.NCompare) + "\n")
        self.writter.write("D;J" + command.upper() + "\n")
        self.writter.write("D=0\n")
        self.writter.write("@END_COMPARE" + str(self.NCompare) + "\n")
        self.writter.write("0;JMP\n")
        self.writter.write("(TRUE_COMPARE" + str(self.NCompare) + ")\n")
        self.writter.write("D=-1\n") # so that D = 0xFFFF, !-1 = 0, this can be seen a bug in ! (bitwise)
        self.writter.write("(END_COMPARE" + str(self.NCompare) + ")\n")
        self.NCompare+= 1
    
    def writeArithmeticD(self, command):
        if command in self.list_single:
            self.writter.write("D=" + self.dict_op[command] + "D\n")
        else:
            if command in self.list_compare:
                self.writeCompare(command)
            else:
                self.writter.write("D=M" + self.dict_op[command] + "D\n")

    def writeArithmetic(self, command):
        self.writeGetArgs(command) # D = y, M = x
        self.writeArithmeticD(command) # D = x op y
        self.writePushD()
