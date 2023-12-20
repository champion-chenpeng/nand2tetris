class VMWriter:
    def __init__(self, output_file):
        self.file = open(output_file, "w")
        self.segment_dict = {
            "var": "local",
            "field": "this",
            "arg": "argument",
        }

    def writePush(self, segment, index):
        if segment in self.segment_dict:
            segment = self.segment_dict[segment]
        self.file.write("push " + segment + " " + str(index) + "\n")

    def writePop(self, segment, index):
        if segment in self.segment_dict:
            segment = self.segment_dict[segment]
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
    
    def writeComment(self, comment):
        self.file.write("// " + comment + "\n")
    def close(self):
        self.file.close()

