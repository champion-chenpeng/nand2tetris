class VMWriter:
    def __init__(self, output_file):
        self.file = open(output_file, "w")

    def writePush(self, segment, index):
        self.file.write("push " + segment + " " + str(index) + "\n")

    def writePop(self, segment, index):
        self.file.write("pop " + segment + " " + str(index) + "\n")

    def writeArithmetic(self, command):
        self.file.write(command + "\n")

    def writeLabel(self, label):
        self.file.write("label " + label + "\n")

    def writeGoto(self, label):
        self.file.write("goto " + label + "\n")

    def writeIf(self, label):
        self.file.write("if-goto " + label + "\n")

    def writeCall(self, name, nArgs):
        self.file.write("call " + name + " " + str(nArgs) + "\n")

    def writeFunction(self, name, nVars):
        self.file.write("function " + name + " " + str(nVars) + "\n")

    def writeReturn(self):
        self.file.write("return\n")

    def close(self):
        self.file.close()

