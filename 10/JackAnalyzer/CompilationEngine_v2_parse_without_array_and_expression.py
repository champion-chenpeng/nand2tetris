import JackTokenizer
class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer.JackTokenizer(input_file)
        self.output_file = open(output_file, "w") 
        self.indentation = 0
        self.compileClass()
        self.close()
    
    def compileClass(self):
        self.writeTag("class")
        self.indentation += 1
        self.writeKeyword("class")
        self.tokenizer.advance()

        self.writeIdentifier(self.tokenizer.identifier())
        self.writeSymbol("{")
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["static", "field"]:
            self.compileClassVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.writeSymbol("}")
        self.indentation -= 1
        self.writeTag("/class")

    def compileClassVarDec(self):
        self.writeTag("classVarDec")
        self.indentation += 1
        self.writeKeyword(self.tokenizer.keyword())
        self.compileType()
        self.writeIdentifier(self.tokenizer.identifier())
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.writeSymbol(",")
            self.writeIdentifier(self.tokenizer.identifier())
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/classVarDec")
    
    def compileType(self):
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["int", "char", "boolean"]:
            self.writeKeyword(self.tokenizer.keyword())
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.writeIdentifier(self.tokenizer.identifier())
        else:
            raise Exception("Error: invalid type")
        
    def compileSubroutine(self):
        self.writeTag("subroutineDec")
        self.indentation += 1
        self.writeKeyword(self.tokenizer.keyword())
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "void":
            self.writeKeyword("void")
        else:
            self.compileType()
        self.writeIdentifier(self.tokenizer.identifier())
        self.writeSymbol("(")
        self.compileParameterList()
        self.writeSymbol(")")
        self.compileSubroutineBody()
        self.indentation -= 1
        self.writeTag("/subroutineDec")
    
    def compileParameterList(self):
        self.writeTag("parameterList")
        self.indentation += 1
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["int", "char", "boolean"]:
            self.compileType()
            self.writeIdentifier(self.tokenizer.identifier())
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.writeSymbol(",")
                self.compileType()
                self.writeIdentifier(self.tokenizer.identifier())
        self.indentation -= 1
        self.writeTag("/parameterList")

    def compileSubroutineBody(self):
        self.writeTag("subroutineBody")
        self.indentation += 1
        self.writeSymbol("{")
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "var":
            self.compileVarDec()
        self.compileStatements()
        self.writeSymbol("}")
        self.indentation -= 1
        self.writeTag("/subroutineBody")

    def compileVarDec(self):
        self.writeTag("varDec")
        self.indentation += 1
        self.writeKeyword("var")
        self.compileType()
        self.writeIdentifier(self.tokenizer.identifier())
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.writeSymbol(",")
            self.writeIdentifier(self.tokenizer.identifier())
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/varDec")
    
    def compileStatements(self):
        self.writeTag("statements")
        self.indentation += 1
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
        self.indentation -= 1
        self.writeTag("/statements")

    def compileDo(self):
        self.writeTag("doStatement")
        self.indentation += 1
        self.writeKeyword("do")
        self.writeIdentifier(self.tokenizer.identifier())
        self.compileSubroutineCall()
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/doStatement")

    def compileLet(self):
        self.writeTag("letStatement")
        self.indentation += 1
        self.writeKeyword("let")
        self.writeIdentifier(self.tokenizer.identifier())
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.writeSymbol("[")
            self.compileExpression()
            self.writeSymbol("]")
        self.writeSymbol("=")
        self.compileExpression()
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/letStatement")

    def compileWhile(self):
        self.writeTag("whileStatement")
        self.indentation += 1
        self.writeKeyword("while")
        self.writeSymbol("(")
        self.compileExpression()
        self.writeSymbol(")")
        self.writeSymbol("{")
        self.compileStatements()
        self.writeSymbol("}")
        self.indentation -= 1
        self.writeTag("/whileStatement")
    
    def compileReturn(self):
        self.writeTag("returnStatement")
        self.indentation += 1
        self.writeKeyword("return")
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ";":
            self.compileExpression()
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/returnStatement")
    
    def compileIf(self):
        self.writeTag("ifStatement")
        self.indentation += 1
        self.writeKeyword("if")
        self.writeSymbol("(")
        self.compileExpression()
        self.writeSymbol(")")
        self.writeSymbol("{")
        self.compileStatements()
        self.writeSymbol("}")
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "else":
            self.writeKeyword("else")
            self.writeSymbol("{")
            self.compileStatements()
            self.writeSymbol("}")
        self.indentation -= 1
        self.writeTag("/ifStatement")

    def compileExpression(self):
        self.writeTag("expression")
        self.indentation += 1
        self.compileTerm()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self.writeSymbol(self.tokenizer.symbol())
            self.compileTerm()
        self.indentation -= 1
        self.writeTag("/expression")
    
    def compileTerm(self):
        self.writeTag("term")
        self.indentation += 1
        if self.tokenizer.tokenType() == "INT_CONST":
            self.writeIntegerConstant(self.tokenizer.intVal())
        elif self.tokenizer.tokenType() == "STRING_CONST":
            self.writeStringConstant(self.tokenizer.stringVal())
        elif self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            self.writeKeyword(self.tokenizer.keyword())
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.writeIdentifier(self.tokenizer.identifier())
            if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.writeSymbol("[")
                self.compileExpression()
                self.writeSymbol("]")
            elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["(", "."]:
                self.compileSubroutineCall()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.writeSymbol("(")
            self.compileExpression()
            self.writeSymbol(")")
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["-", "~"]:
            self.writeSymbol(self.tokenizer.symbol())
            self.compileTerm()
        self.indentation -= 1
        self.writeTag("/term")
    
    def compileSubroutineCall(self):
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.writeSymbol(".")
            self.writeIdentifier(self.tokenizer.identifier())
        self.writeSymbol("(")
        self.compileExpressionList()
        self.writeSymbol(")")

    def compileExpressionList(self):
        self.writeTag("expressionList")
        self.indentation += 1
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.compileExpression()
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.writeSymbol(",")
                self.compileExpression()
        self.indentation -= 1
        self.writeTag("/expressionList")
    
    def writeTag(self, tag):
        self.output_file.write("  " * self.indentation + "<" + tag + ">\n")
    
    def writeKeyword(self, keyword):
        self.output_file.write("  " * self.indentation + "<keyword> " + keyword + " </keyword>\n")
        self.tokenizer.advance()

    def writeSymbol(self, symbol):
        self.output_file.write("  " * self.indentation + "<symbol> " + symbol + " </symbol>\n")
        self.tokenizer.advance()
    
    def writeIdentifier(self, identifier):
        self.output_file.write("  " * self.indentation + "<identifier> " + str(identifier) + " </identifier>\n")
        self.tokenizer.advance()

    def writeIntegerConstant(self, integerConstant):
        self.output_file.write("  " * self.indentation + "<integerConstant> " + integerConstant + " </integerConstant>\n")
        self.tokenizer.advance()

    def writeStringConstant(self, stringConstant):
        self.output_file.write("  " * self.indentation + "<stringConstant> " + stringConstant + " </stringConstant>\n")
        self.tokenizer.advance()

    def close(self):
        self.output_file.close()

    

