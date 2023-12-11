import JackTokenizer, VMWriter, SymbolTable, sys, os
class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.className = ""
        self.tokenizer = JackTokenizer.JackTokenizer(input_file)
        self.symbol_table = SymbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(output_file)
        self.label_index = 0
        self.label_dict = {
            "if": "IF",
            "while": "WHILE"
        }
        
        self.compileClass()
        self.vm_writer.close()

    def close(self):
        self.output_file.close()

    def writePopVar(self, name):
        kind = self.symbol_table.kindOf(name)
        index = self.symbol_table.indexOf(name)
        self.vm_writer.writePop(kind.lower(), index)
    
    def writePushVar(self, name):
        kind = self.symbol_table.kindOf(name)
        index = self.symbol_table.indexOf(name)
        self.vm_writer.writePush(kind.lower(), index)
    
    def compileVarDec(self, isParameter=False):
        kind = "arg" if isParameter else self.tokenizer.keyword() # static or field or var
        kind = kind.upper()
        if not isParameter:
            self.tokenizer.advance() # skip static or field or var

        if self.tokenizer.tokenType() != "SYMBOL": # exclude parameter list void case, following ")"
            type = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
            self.tokenizer.advance() # skip type
            name = self.tokenizer.identifier()
            self.tokenizer.advance() # skip name
            self.symbol_table.define(name, type, kind)
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance() # skip ","
                if isParameter: # not empty parameter list, if empty, next token is ")", a symbol
                    type = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
                    self.tokenizer.advance() # skip type
                name = self.tokenizer.identifier()
                self.tokenizer.advance() # skip name
                self.symbol_table.define(name, type, kind)
        if not isParameter:
            self.tokenizer.advance() # skip ";"
        
    def compileClass(self):
        self.tokenizer.advance() # skip "class"
        self.className = self.tokenizer.identifier()
        self.tokenizer.advance() # skip class name
        self.tokenizer.advance() # skip "{"
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["static", "field"]:
            self.compileVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.tokenizer.advance() # skip "}"

    def compileSubroutine(self):
        self.symbol_table.reset()
        self.label_index = 0
        self.tokenizer.advance() # skip "constructor" or "function" or "method"
        # returnType = self.tokenizer.keyword() # void or type
        self.tokenizer.advance() # skip void or type, the subroutine return type will be determined in subroutineBody
        name = self.tokenizer.identifier()
        self.vm_writer.writeFunction(self.className + "." + name, self.symbol_table.varCount("VAR")) # need to run SymbolTable first?
        self.tokenizer.advance() # skip subroutine name
        self.tokenizer.advance() # skip "("
        self.compileVarDec(isParameter=True)
        self.tokenizer.advance() # skip ")"
        self.compileSubroutineBody()
        
    def compileSubroutineBody(self):
        self.tokenizer.advance() # skip "{"
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "var":
            self.compileVarDec()
        self.compileStatements()
        self.tokenizer.advance() # skip "}"
    
    def compileStatements(self):
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.keyword() == "let":
                self.compileLet()
            elif self.tokenizer.keyword() == "if":
                self.compileIf()
            elif self.tokenizer.keyword() == "while":
                self.compileWhile()
            elif self.tokenizer.keyword() == "do":
                self.compileDo()
            elif self.tokenizer.keyword() == "return":
                self.compileReturn()
    def compileLet(self):
        self.tokenizer.advance() # skip "let"
        name = self.tokenizer.identifier()
        self.tokenizer.advance() # skip name
        # array case
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.writePushVar(name)
            self.tokenizer.advance() # skip "["
            self.compileExpression()
            self.tokenizer.advance() # skip "]"
            self.vm_writer.writeArithmetic("add")
            self.tokenizer.advance()
        
        self.tokenizer.advance() # skip "="
        self.compileExpression()
        self.writePopVar(name)
        self.tokenizer.advance() # skip ";"
    
    def compileReturn(self):
        self.tokenizer.advance() # skip "return"
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compileExpression()
        else:
            self.vm_writer.writePush("constant", 0)
        self.vm_writer.writeReturn()
        self.tokenizer.advance() # skip ";"

    def compileDo(self):
        self.tokenizer.advance() # skip "do"
        self.compileExpression()
        self.vm_writer.writePop("temp", 0)
        self.tokenizer.advance() # skip ";"

    def compileIf(self):
        self.tokenizer.advance() # skip "if"
        self.tokenizer.advance() # skip "("
        self.compileExpression()
        self.tokenizer.advance() # skip ")"
        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(self.label_dict["if"] + str(self.label_index))# if goto L1
        self.tokenizer.advance() # skip "{"
        self.compileStatements()
        self.tokenizer.advance() # skip "}"
        self.vm_writer.writeGoto(self.label_dict["if"] + str(self.label_index + 1)) # goto L2
        self.vm_writer.writeLabel(self.label_dict["if"] + str(self.label_index)) # label L1
        self.label_index += 1
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "else":
            self.tokenizer.advance() # skip "else"
            self.tokenizer.advance() # skip "{"
            self.compileStatements()
            self.tokenizer.advance() # skip "}"
        self.vm_writer.writeLabel(self.label_dict["if"] + str(self.label_index)) # label L2
        self.label_index += 1

    def compileWhile(self):
        self.tokenizer.advance() # skip "while"
        self.tokenizer.advance() # skip "("
        self.vm_writer.writeLabel(self.label_dict["while"] + str(self.label_index)) # label L1
        self.label_index += 1
        self.compileExpression()
        self.tokenizer.advance() # skip ")"
        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(self.label_dict["while"] + str(self.label_index)) # if goto L2
        self.tokenizer.advance() # skip "{"
        self.compileStatements()
        self.tokenizer.advance() # skip "}"
        self.vm_writer.writeGoto(self.label_dict["while"] + str(self.label_index - 1)) # goto L1
        self.vm_writer.writeLabel(self.label_dict["while"] + str(self.label_index)) # label L2
        self.label_index += 1

    def compileExpressionList(self):
        NExpr = 0
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.compileExpression()
            NExpr += 1
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.tokenizer.advance() # skip ","
                self.compileExpression()
                NExpr += 1
        return NExpr

    def compileExpression(self):
        self.compileTerm()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compileTerm()
            if op == "+":
                self.vm_writer.writeArithmetic("add")
            elif op == "-":
                self.vm_writer.writeArithmetic("sub")
            elif op == "*":
                self.vm_writer.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.writeCall("Math.divide", 2)
            elif op == "&amp;":
                self.vm_writer.writeArithmetic("and")
            elif op == "|":
                self.vm_writer.writeArithmetic("or")
            elif op == "&lt;":
                self.vm_writer.writeArithmetic("lt")
            elif op == "&gt;":
                self.vm_writer.writeArithmetic("gt")
            elif op == "=":
                self.vm_writer.writeArithmetic("eq")

    def compileTerm(self):
        if self.tokenizer.tokenType() == "INTEGER_CONSTANT":
            self.vm_writer.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "STRING_CONSTANT":
            string = self.tokenizer.stringVal()
            self.vm_writer.writePush("constant", len(string))
            self.vm_writer.writeCall("String.new", 1)
            for char in string:
                self.vm_writer.writePush("constant", ord(char))
                self.vm_writer.writeCall("String.appendChar", 2)
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            if self.tokenizer.keyword() == "true":
                self.vm_writer.writePush("constant", 1)
                self.vm_writer.writeArithmetic("neg")
            elif self.tokenizer.keyword() == "false" or self.tokenizer.keyword() == "null":
                self.vm_writer.writePush("constant", 0)
            elif self.tokenizer.keyword() == "this":
                self.vm_writer.writePush("pointer", 0)
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.tokenizer.advance()
            self.compileExpression()
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["-", "~"]:
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.compileTerm()
            if op == "-":
                self.vm_writer.writeArithmetic("neg")
            elif op == "~":
                self.vm_writer.writeArithmetic("not")
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            name = self.tokenizer.identifier()
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.writePopVar(name)
                self.tokenizer.advance()
                self.compileExpression()
                self.writeSymbol("]")
            elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
                self.vm_writer.writePush("pointer", 0)
                self.tokenizer.advance()
                NExpr = self.compileExpressionList()
                self.tokenizer.advance()
                self.vm_writer.writeCall(self.className + "." + name, NExpr)
            elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
                self.tokenizer.advance()
                funcName = self.tokenizer.identifier()
                self.tokenizer.advance()
                self.tokenizer.advance()
                NExpr = self.compileExpressionList()
                self.tokenizer.advance()
                self.vm_writer.writeCall(name + "." + funcName, NExpr)
            else:
                self.writePushVar(name)
        else:
            raise TypeError("Error: invalid term: " + self.tokenizer.currentToken)


