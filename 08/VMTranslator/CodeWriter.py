class CodeWriter:
    def __init__(self, file):
        file = file + ".asm"
        self.writter = open(file, "w")
        
        self.dict_RAM = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "R5", "pointer": "THIS"}
        self.dict_op = {"add": "+", "sub": "-", "and": "&", "or": "|", "neg": "-", "not": "!"}
        self.list_pointer = ["local", "argument", "this", "that"]
        self.list_single = ["neg", "not"]
        self.list_compare = ["eq", "gt", "lt"]
        self.NCompare= 0

        self.RET = "R14"
        self.savedFrame = [self.RET, "LCL", "ARG", "THIS", "THAT"] # RET is virtual savedFrame, indeed is in temp R14

        self.currentFile = ""
        self.callerFunction = "" # in file.function format
        self.Nret = 0

        self.bootstrap()
    
    def setFileName(self, file):
        file = file.split(".")[0]
        self.currentFile = file

    def bootstrap(self):
        self.initRAM()
        # call Sys.init, currently add in VMTranslator
    
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

    def close(self):
        self.endLoop()
        self.writter.close()

    def writePushX(self, X):
        self.writter.write("@SP\n")
        self.writter.write("A=M\n")
        self.writter.write("M=" + X + "\n")
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
            self.writter.write("@" + self.currentFile + "." + arg2 + "\n") # filename.arg2
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
            self.writePushX("D") # A is messed up
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
        label = self.callerFunction + "$cmp." + str(self.NCompare)
        true_label = label + ".TRUE"
        end_label = label + ".END"
        self.writter.write("D=M-D\n")
        self.writter.write("@" + true_label + "\n")
        self.writter.write("D;J" + command.upper() + "\n")
        self.writter.write("D=0\n")
        self.writter.write("@" + end_label + "\n")
        self.writter.write("0;JMP\n")
        self.writter.write("(" + true_label + ")\n")
        self.writter.write("D=-1\n") # so that D = 0xFFFF, !-1 = 0, this can be seen a bug in ! (bitwise)
        self.writter.write("(" + end_label + ")\n")
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
        self.writePushX("D")

    def writeLabel(self, label):
        self.writter.write("(" + self.callerFunction + "$" + label + ")\n")

    def writeGoto(self, label):
        self.writter.write("@" + self.callerFunction + "$" + label + "\n")
        self.writter.write("0;JMP\n")

    def writeIf(self, label):
        self.writePopD()
        self.writter.write("@" + self.callerFunction + "$" + label + "\n")
        self.writter.write("D;JNE\n") #JNZ, 0 = false, !0 = true, true maybe 1 or -1
    
    def writeSavedFrame(self, name):
        self.writter.write("@" + name + "\n")
        self.writter.write("D=M\n")
        self.writePushX("D")
    
    def writeRestoreFrame(self, FRAME, index):
        self.writter.write("@" + str(index) + "\n")
        self.writter.write("D=A\n")
        self.writter.write("@" + FRAME + "\n")
        self.writter.write("A=M-D\n")
        self.writter.write("D=M\n")
        self.writter.write("@" + self.savedFrame[-index] + "\n")
        self.writter.write("M=D\n")

    def writeCall(self, functionName, numArgs):
        calleeFunction = functionName
        returnAddress = self.callerFunction + "$ret." + str(self.Nret)
        self.Nret += 1
        # push returnAddress
        self.writter.write("@" + returnAddress + "\n")
        self.writter.write("D=A\n")
        self.writePushX("D")
        # push saevdFrame
        for name in self.savedFrame[1:]: # exclude RET
            self.writeSavedFrame(name)
        # ARG = SP-n-5
        self.writter.write("@SP\n")
        self.writter.write("D=M\n")
        self.writter.write("@" + str(numArgs) + "\n")
        self.writter.write("D=D-A\n")
        self.writter.write("@5\n")
        self.writter.write("D=D-A\n")
        self.writter.write("@ARG\n")
        self.writter.write("M=D\n")
        # LCL = SP
        self.writter.write("@SP\n")
        self.writter.write("D=M\n")
        self.writter.write("@LCL\n")
        self.writter.write("M=D\n")
        # goto calleeFunction
        self.writter.write("@" + calleeFunction + "\n")
        self.writter.write("0;JMP\n")
        # (returnAddress)
        self.writter.write("(" + returnAddress + ")\n")
        
    def writeReturn(self):
        # *FRAME = *LCL
        FRAME = "R13"
        self.writter.write("@LCL\n")
        self.writter.write("D=M\n")
        self.writter.write("@" + FRAME + "\n")
        self.writter.write("M=D\n")
        # **ARG = pop(), return value
        self.writePopD()
        self.writter.write("@ARG\n")
        self.writter.write("A=M\n")
        self.writter.write("M=D\n")
        # *SP = ARG+1
        self.writter.write("@ARG\n")
        self.writter.write("D=M+1\n")
        self.writter.write("@SP\n")
        self.writter.write("M=D\n")
        # write restore frame
        for i in range(1, len(self.savedFrame)+1):
            self.writeRestoreFrame(FRAME, i)
        
        # goto RET
        self.writter.write("@" + self.RET + "\n")
        self.writter.write("A=M\n")
        self.writter.write("0;JMP\n")
    
    def writeFunction(self, functionName, numLocals):
        self.callerFunction = functionName
        self.Nret = 0
        self.writter.write("(" + self.callerFunction + ")\n")
        # init local with 0
        for i in range(int(numLocals)):
            self.writePushX("0")
    

