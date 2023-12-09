import Parser, CodeWriter, sys, os

class VMTranslator:
    def __init__(self, file):
        self.file = file
        self.parser = Parser.Parser(file)
        self.codeWriter = CodeWriter.CodeWriter(file)

    def translate(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == "C_ARITHMETIC":
                self.codeWriter.writeArithmetic(self.parser.arg1())
            elif self.parser.commandType() == "C_PUSH" or self.parser.commandType() == "C_POP":
                self.codeWriter.writter.write("// " + self.parser.currentCommand + "\n")
                self.codeWriter.writePushPop(self.parser.commandType(), self.parser.arg1(), self.parser.arg2())
        self.parser.reset()
        self.codeWriter.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py [file.vm]")
    else:
        if os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if file.endswith(".vm"):
                    vmTranslator = VMTranslator(sys.argv[1] + "/" + file)
                    vmTranslator.translate()
        else:
            vmTranslator = VMTranslator(sys.argv[1])
            vmTranslator.translate()


