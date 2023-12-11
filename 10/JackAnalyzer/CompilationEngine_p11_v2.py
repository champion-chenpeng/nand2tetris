import JackTokenizer
class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer.JackTokenizer(input_file)
        self.output_file = open(output_file, "w") 
        self.indentation = 0
        self.index = {"static": 0, "field": 0, "arg": 0, "local": 0}
        self.symbolTable = {}
        self.compileClass()
        self.close()
    def close(self):
        self.output_file.close()
    
    def compileVarDec(self, isParameter=False):
        globalType = "arg" if isParameter else self.tokenizer.keyword() # static or field or var
        tag = "varDec" if globalType == "var" else "classVarDec"
        if isParameter:
            tag = "parameterList"

        self.writeTag(tag)
        self.indentation += 1
        if not isParameter:
            self.writeKeyword(globalType)
        if self.tokenizer.tokenType() == "KEYWORD": # exclude parameter list void case, following ")"
            self.compileType()
            self.writeIdentifier(self.tokenizer.identifier(), globalType, self.index[globalType], "declared") # class variable name, index is important, usage is important
            self.index[globalType] += 1
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.writeSymbol(",")
                if isParameter: # not empty parameter list, if empty, next token is ")", a symbol
                    self.compileType()
                self.writeIdentifier(self.tokenizer.identifier(), globalType, self.index[globalType], "declared")
                self.index[globalType] += 1
        if not isParameter:
            self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/" + tag)
        
    def compileClass(self):
        self.writeTag("class")
        self.indentation += 1
        self.writeKeyword("class")
        self.tokenizer.advance()

        self.writeIdentifier(self.tokenizer.identifier(), "class", 0, "declared") # class name, since only one class per file, index or usage is not important
        self.writeSymbol("{")
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["static", "field"]:
            self.compileVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.writeSymbol("}")
        self.indentation -= 1
        self.writeTag("/class")
    
    def compileType(self):
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["int", "char", "boolean"]: # basic type
            self.writeKeyword(self.tokenizer.keyword())
        elif self.tokenizer.tokenType() == "IDENTIFIER": # user-defined type
            self.writeIdentifier(self.tokenizer.identifier(), "class", 0, "used") # here a instance of class is used
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
        self.writeIdentifier(self.tokenizer.identifier(), "subroutine", 0, "declared") # subroutine name, index is important, usage is important
        self.writeSymbol("(")
        self.compileVarDec(isParameter=True)
        self.writeSymbol(")")
        self.compileSubroutineBody()
        self.indentation -= 1
        self.writeTag("/subroutineDec")
        
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
        self.writeIdentifier(self.tokenizer.identifier(), "subroutine", 0, "used") # subroutine name, index is important, usage is important
        self.compileSubroutineCall()
        self.writeSymbol(";")
        self.indentation -= 1
        self.writeTag("/doStatement")

    def compileLet(self):
        self.writeTag("letStatement")
        self.indentation += 1
        self.writeKeyword("let")
        self.writeIdentifier(self.tokenizer.identifier(), "??", "??", "used")
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
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            symbol = self.tokenizer.symbol()
            self.writeSymbol(symbol)
            self.compileTerm()
        self.indentation -= 1
        self.writeTag("/expression")
    
    def compileTerm(self):
        self.writeTag("term")
        self.indentation += 1
        if self.tokenizer.tokenType() == "INTEGER_CONSTANT":
            self.writeIntegerConstant(self.tokenizer.intVal())
        elif self.tokenizer.tokenType() == "STRING_CONSTANT":
            self.writeStringConstant(self.tokenizer.stringVal())
        elif self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            self.writeKeyword(self.tokenizer.keyword())
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.writeIdentifier(self.tokenizer.identifier(), "??", "??", "used")
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
        # self.writeIdentifier(self.tokenizer.identifier(), "subroutine", 0, "used") # subroutine name, used. But there remain confusion, if it is current class's method, this first identifier is subroutine name, if it is other class's method, this first identifier is class name; later we should handle this problem
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.writeSymbol(".")
            self.writeIdentifier(self.tokenizer.identifier(), "subroutine", 0, "used") # subroutine name, index is important, usage is important
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
    
    def writeIdentifier(self, identifier, category, index, usage):
        attributes = "category=\"" + category + "\" index=\"" + str(index) + "\" usage=\"" + usage + "\""
        self.output_file.write("  " * self.indentation + "<identifier" + attributes + "> " + str(identifier) + " </identifier>\n")
        self.tokenizer.advance()

    def writeIntegerConstant(self, integerConstant):
        self.output_file.write("  " * self.indentation + "<integerConstant> " + integerConstant + " </integerConstant>\n")
        self.tokenizer.advance()

    def writeStringConstant(self, stringConstant):
        self.output_file.write("  " * self.indentation + "<stringConstant> " + stringConstant + " </stringConstant>\n")
        self.tokenizer.advance()
