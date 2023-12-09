import Parser, CodeWriter, sys, os

class VMTranslator:
    def __init__(self, input):
        self.codeWriter = CodeWriter.CodeWriter(input)
        self.parser = None

    def translate(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == "C_ARITHMETIC":
                self.codeWriter.writeArithmetic(self.parser.arg1())
            elif self.parser.commandType() == "C_PUSH" or self.parser.commandType() == "C_POP":
                self.codeWriter.writter.write("// " + self.parser.currentCommand + "\n")
                self.codeWriter.writePushPop(self.parser.commandType(), self.parser.arg1(), self.parser.arg2())
            elif self.parser.commandType() == "C_LABEL":
                self.codeWriter.writeLabel(self.parser.arg1())
            elif self.parser.commandType() == "C_GOTO":
                self.codeWriter.writeGoto(self.parser.arg1())
            elif self.parser.commandType() == "C_IF":
                self.codeWriter.writeIf(self.parser.arg1())
            elif self.parser.commandType() == "C_FUNCTION":
                self.codeWriter.writeFunction(self.parser.arg1(), self.parser.arg2())
            elif self.parser.commandType() == "C_CALL":
                self.codeWriter.writeCall(self.parser.arg1(), self.parser.arg2())
            elif self.parser.commandType() == "C_RETURN":
                self.codeWriter.writeReturn()
        self.parser.reset()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py [file.vm|folder]")
    else:
        folder_dir = os.path.dirname(sys.argv[1])
        file_name = os.path.basename(sys.argv[1])
        print(sys.argv[1])
        print(folder_dir)
        print(file_name)
        if os.path.isdir(sys.argv[1]):
            vmTranslator = VMTranslator(sys.argv[1] + "/" + file_name + ".asm")
            files = os.listdir(sys.argv[1])
            # Sys must be translated first
            if "Sys.vm" in files:
                sysFile = sys.argv[1] + "/Sys.vm"
                vmTranslator.parser = Parser.Parser(sysFile)
                vmTranslator.codeWriter.setFileName("Sys.vm")
                vmTranslator.translate()
                files.remove("Sys.vm")
            for file in files:
                if file.endswith(".vm"):
                    vmTranslator.parser = Parser.Parser(sys.argv[1] + "/" + file)
                    vmTranslator.codeWriter.setFileName(file)
                    vmTranslator.translate()
        else:
            vmTranslator = VMTranslator(folder_dir + "/" + file_name.replace(".vm", ".asm"))
            vmTranslator.parser = Parser.Parser(sys.argv[1])
            vmTranslator.translate()
        vmTranslator.codeWriter.close()

        


