import JackTokenizer, VMWriter, SymbolTable
class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.className = ""
        self.tokenizer = JackTokenizer.JackTokenizer(input_file)
        self.symbol_table = SymbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(output_file)

        self.op_dict = {
            "+": "add",
            "-": "sub",
            "*": "multiply",
            "/": "divide",
            "&amp;": "and",
            "|": "or",
            "&lt;": "lt",
            "&gt;": "gt",
            "=": "eq"
        }

        self.keywordConstant = ["true", "false", "null", "this"]
        self.unaryOp = ["-", "~"]
        
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
    
    def compileVarDec(self, isParameter=False, isMethod=False):
        kind = "arg" if isParameter else self.tokenizer.keyword() # static or field or var
        kind = kind.upper()
        if not isParameter:
            self.tokenizer.advance() # skip static or field or var
        
        # add "this" to arg list
        if isParameter and isMethod:
            self.symbol_table.define("this", self.className, "ARG")

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
        
    def compileConstructorInit(self):
        nField = self.symbol_table.varCount("FIELD")
        self.vm_writer.writePush("constant", nField)
        self.vm_writer.writeCall("Memory.alloc", 1)
        self.vm_writer.writePop("pointer", 0)

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

        function_type = self.tokenizer.keyword() # constructor or function or method
        self.tokenizer.advance() # skip "constructor" or "function" or "method"
        # returnType = self.tokenizer.keyword() # void or type
        self.tokenizer.advance() # skip void or type, the subroutine return type will be determined in subroutineBody
        name = self.tokenizer.identifier()
        self.tokenizer.advance() # skip subroutine name
        self.tokenizer.advance() # skip "("
        self.compileVarDec(isParameter=True, isMethod=(function_type == "method"))
        self.tokenizer.advance() # skip ")"
        self.compileSubroutineBody(name, function_type)

    def compileSubroutineBody(self, name, function_type):
        self.tokenizer.advance() # skip "{"
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "var":
            self.compileVarDec()
        self.vm_writer.writeFunction(self.className + "." + name, self.symbol_table.varCount("VAR"))
        if function_type == "method":
            self.vm_writer.writePush("argument", 0) # push this
            self.vm_writer.writePop("pointer", 0) # pop this
        # the problem is this is used via FIELD, and this is not ready yet
        if function_type == "constructor":
            self.compileConstructorInit()
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
    
    def getArrayIndex(self, name):
        self.writePushVar(name)
        self.tokenizer.advance() # skip "["
        self.compileExpression()
        self.tokenizer.advance() # skip "]"
        self.vm_writer.writeArithmetic("add")

    def compileLet(self):
        self.tokenizer.advance() # skip "let"
        name = self.tokenizer.identifier()
        self.tokenizer.advance() # skip name
        # array case
        isArray = False
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            isArray = True
            self.getArrayIndex(name)
        
        self.tokenizer.advance() # skip "="
        self.compileExpression()
        if isArray:
            self.vm_writer.writePop("temp", 0) # pop expression result to temp 0
            self.vm_writer.writePop("pointer", 1) # pop array address to pointer 1
            self.vm_writer.writePush("temp", 0) # push expression result to stack
            self.vm_writer.writePop("that", 0) # pop expression result to array address
        else:
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
        self.vm_writer.writePop("temp", 0) # clean the stack of the expression result
        self.tokenizer.advance() # skip ";"

    def compileIf(self):
        controlName = "IF"
        labelIndex = self.symbol_table.label_dict[controlName]
        self.symbol_table.label_dict[controlName] += 1
        labelName = controlName + str(labelIndex)
        label_else = labelName + "_ELSE"
        label_end = labelName + "_END"

        self.tokenizer.advance() # skip "if"
        self.tokenizer.advance() # skip "("
        self.compileExpression()
        self.tokenizer.advance() # skip ")"
        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_else)
        self.tokenizer.advance() # skip "{"
        self.compileStatements()
        self.tokenizer.advance() # skip "}"
        self.vm_writer.writeGoto(label_end) 
        self.vm_writer.writeLabel(label_else) 
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "else":
            self.tokenizer.advance() # skip "else"
            self.tokenizer.advance() # skip "{"
            self.compileStatements()
            self.tokenizer.advance() # skip "}"
        self.vm_writer.writeLabel(label_end) 

        

    def compileWhile(self):
        controlName = "WHILE"
        labelIndex = self.symbol_table.label_dict[controlName]
        self.symbol_table.label_dict[controlName] += 1
        labelName = controlName + str(labelIndex)
        label_begin = labelName + "_BEGIN"
        label_end = labelName + "_END"

        self.tokenizer.advance() # skip "while"
        self.tokenizer.advance() # skip "("
        self.vm_writer.writeLabel(label_begin)
        self.compileExpression()
        self.tokenizer.advance() # skip ")"
        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_end) # 
        self.tokenizer.advance() # skip "{"
        self.compileStatements()
        self.tokenizer.advance() # skip "}"
        self.vm_writer.writeGoto(label_begin) 
        self.vm_writer.writeLabel(label_end) 
        

    def compileExpressionList(self): # used in subrouteCall, so ExpressionList == parameterList
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
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in self.op_dict:
            op = self.tokenizer.symbol()
            operation = self.op_dict[op]
            self.tokenizer.advance()
            self.compileTerm()
            if op in ["*", "/"]:
                self.vm_writer.writeCall("Math." + operation, 2)
            elif op in self.op_dict:
                self.vm_writer.writeArithmetic(operation)

    def compileINT(self):
        self.vm_writer.writePush("constant", self.tokenizer.intVal())
        self.tokenizer.advance()

    def compileSTRING(self):
        string = self.tokenizer.stringVal()
        self.vm_writer.writePush("constant", len(string))
        self.vm_writer.writeCall("String.new", 1)
        for char in string:
            self.vm_writer.writePush("constant", ord(char))
            self.vm_writer.writeCall("String.appendChar", 2)
        self.tokenizer.advance()

    def compileKeywordConstant(self):
        if self.tokenizer.keyword() == "true":
            self.vm_writer.writePush("constant", 0)
            self.vm_writer.writeArithmetic("not")
        elif self.tokenizer.keyword() == "false" or self.tokenizer.keyword() == "null":
            self.vm_writer.writePush("constant", 0)
        elif self.tokenizer.keyword() == "this":
            self.vm_writer.writePush("pointer", 0)
        self.tokenizer.advance()
    
    def compileUnaryOp(self):
        op = self.tokenizer.symbol()
        self.tokenizer.advance()
        self.compileTerm()
        if op == "-":
            self.vm_writer.writeArithmetic("neg")
        elif op == "~":
            self.vm_writer.writeArithmetic("not")

    def compileArray(self, name):
        self.getArrayIndex(name)
        self.vm_writer.writePop("pointer", 1)
        self.vm_writer.writePush("that", 0)

    def compilePartialSubroutineCall(self, className, funcName, isMethod=False):
        self.tokenizer.advance() # skip "("

        NExpr = self.compileExpressionList() + int(isMethod)
        self.tokenizer.advance() # skip ")"
        self.vm_writer.writeCall(className + "." + funcName, NExpr)


    def compileSubroutineCall(self, name):
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(": # current class method call
            self.vm_writer.writePush("pointer", 0) # push this
            self.compilePartialSubroutineCall(self.className, name, isMethod=True)
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".": # class or object call
            self.tokenizer.advance() # skip "."
            funcName = self.tokenizer.identifier()
            self.tokenizer.advance() # skip funcName
            
            type = self.symbol_table.typeOf(name)
            isMethod = (type != None)
            if isMethod: # if type, it's a object call, otherwise, it's a static call
                self.writePushVar(name) # push object as this
            className = type if isMethod else name
            self.compilePartialSubroutineCall(className, funcName, isMethod) # bool(type) == isMethod

    def compileVarName(self):
        name = self.tokenizer.identifier()
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.compileArray(name)
        # subroutineCall
        elif self.tokenizer.tokenType() == "SYMBOL" and (self.tokenizer.symbol() == "(" or self.tokenizer.symbol() == "."):
            self.compileSubroutineCall(name)
        else:
            self.writePushVar(name)

    def compileTerm(self):
        if self.tokenizer.tokenType() == "INTEGER_CONSTANT":
            self.compileINT()
        elif self.tokenizer.tokenType() == "STRING_CONSTANT":
            self.compileSTRING()
        elif self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in self.keywordConstant:
            self.compileKeywordConstant()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.tokenizer.advance() # skip "("
            self.compileExpression()
            self.tokenizer.advance() # skip ")"
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in self.unaryOp:
            self.compileUnaryOp()
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.compileVarName()
        else:
            raise TypeError("Error: invalid term: " + str(self.tokenizer.currentToken))


