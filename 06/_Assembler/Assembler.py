import Parser, Code, SymbolTable, sys

class Assembler:
    def __init__(self, file):
        self.file = file
        self.parser = Parser.Parser(file)
        self.code = Code.Code()
        self.symbolTable = SymbolTable.SymbolTable()
        self.output = []
        self.address = 16

    def assemble(self):
        self.firstPass()
        self.secondPass()

    def firstPass(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == "L_COMMAND":
                self.parser.outlineNumber -= 1
                self.symbolTable.addEntry(self.parser.symbol(), self.parser.getLineNumber())
            # print("First pass: " + self.parser.getCurrentCommand() + " " + str(self.parser.getLineNumber()))
            # print(self.symbolTable.table)
            # print(self.output)
        self.parser.reset()

    def secondPass(self):
        while self.parser.hasMoreCommands():
            self.parser.advance()
            if self.parser.commandType() == "A_COMMAND":
                self.aCommand()
            elif self.parser.commandType() == "C_COMMAND":
                self.cCommand()
            # print("Second pass: " + self.parser.getCurrentCommand() + " " + str(self.parser.getLineNumber()))
            # print(self.output)
        self.parser.reset()

    def aCommand(self):
        symbol = self.parser.symbol()
        if symbol.isdigit():
            self.output.append(self.code.aCommand(symbol))
        else:
            if not self.symbolTable.contains(symbol):
                self.symbolTable.addEntry(symbol, self.address)
                self.address += 1
            self.output.append(self.code.aCommand(self.symbolTable.getAddress(symbol)))

    def cCommand(self):
        self.output.append(self.code.cCommand(self.parser.dest(), self.parser.comp(), self.parser.jump()))

    def write(self):
        with open(self.file.replace(".asm", ".hack"), "w") as output:
            for line in self.output:
                output.write(line + "\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Assembler.py [file.asm]")
    else:
        assembler = Assembler(sys.argv[1])
        assembler.assemble()
        assembler.write()
