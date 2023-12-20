import sys
class JackTokenizer:
    def __init__(self, file):
        self.file = file
        self.tokens = []
        self.currentTokenIndex = 0
        self.currentToken = ""
        self.currentTokenType = ""
        self.currentTokenValue = ""
        self.TYPE = 0
        self.VALUE = 1
        self.dict_keyword = {
            "class": "CLASS",
            "constructor": "CONSTRUCTOR",
            "function": "FUNCTION",
            "method": "METHOD",
            "field": "FIELD",
            "static": "STATIC",
            "var": "VAR",
            "int": "INT",
            "char": "CHAR",
            "boolean": "BOOLEAN",
            "void": "VOID",
            "true": "TRUE",
            "false": "FALSE",
            "null": "NULL",
            "this": "THIS",
            "let": "LET",
            "do": "DO",
            "if": "IF",
            "else": "ELSE",
            "while": "WHILE",
            "return": "RETURN"
        }

        self.list_symbol = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
        self.escape_symbol = {
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "&": "&amp;"
        }

        self.tokenizer()
        self.advance() # initialize currentToken

    def hasMoreTokens(self):
        return self.currentTokenIndex < len(self.tokens)
    
    def advance(self):
        if self.hasMoreTokens():
            self.currentToken = self.tokens[self.currentTokenIndex]
            self.currentTokenIndex += 1
            self.currentTokenType = self.currentToken[self.TYPE]
            self.currentTokenValue = self.currentToken[self.VALUE]
            print(self.currentTokenIndex, self.currentToken)

    def tokenType(self):
        return self.currentTokenType
    
    def keyword(self):
        if self.currentTokenType == "KEYWORD":
            return self.currentTokenValue
        else:
            raise TypeError("Error: current token is not a keyword: /n" + self.currentToken)

    def symbol(self):
        if self.currentTokenType == "SYMBOL":
            return self.currentTokenValue
        else:
            raise TypeError("Error: current token is not a symbol: /n" + str(self.currentToken))

    def identifier(self):
        if self.currentTokenType == "IDENTIFIER":
            return self.currentTokenValue
        else:
            raise TypeError("Error: current token is not a identifier: /n" + str(self.currentToken))

    def intVal(self):
        if self.currentTokenType == "INTEGER_CONSTANT":
            return self.currentTokenValue
        else:
            raise TypeError("Error: current token is not a integer: /n" + str(self.currentToken))

    def stringVal(self):
        if self.currentTokenType == "STRING_CONSTANT":
            return self.currentTokenValue
        else:
            raise TypeError("Error: current token is not a string: /n" + str(self.currentToken))
    
    def tokenizeLine(self, line):
        # help split symbols
        for symbol in self.list_symbol:
            line = line.replace(symbol, " " + symbol + " ")
        
        brokenStrTokens = line.split()
        isString = False
        currentString = ""
        rawTokens = []
        for token in brokenStrTokens:
            if not isString and token.startswith("\""):
                isString = True
                currentString = token
            elif isString and token.endswith("\""):
                isString = False
                currentString += " " + token
                rawTokens.append(currentString)
            elif isString and "\"" not in token:
                currentString += " " + token
            else:
                rawTokens.append(token)
        return rawTokens
    
    def storeTokens(self, rawTokens):
        for token in rawTokens:
            if token in self.dict_keyword:
                self.tokens.append(["KEYWORD", token])
            elif token in self.list_symbol:
                if token in self.escape_symbol:
                    token = self.escape_symbol[token]
                self.tokens.append(["SYMBOL", token])
            elif token.isdigit():
                self.tokens.append(["INTEGER_CONSTANT", token])
            elif len(token) >= 2 and token.startswith("\"") and token.endswith("\""):
                self.tokens.append(["STRING_CONSTANT", token[1:-1]])
            else:
                self.tokens.append(["IDENTIFIER", token])

    def tokenizer(self): # comment skip mainly
        with open(self.file, "r") as f:
            lines = f.readlines()
            isComment = False
            for line in lines:         
                line = line.strip()
                if line.startswith("/**"):
                    isComment = True
                if line.endswith("*/"):
                    isComment = False
                if isComment or line.startswith("//") or line.startswith("/**") or line.endswith("*/") or line.startswith("*") or line == "":
                    continue
                else:
                    line = line.split("//")[0].strip()
                    
                    rawTokens = self.tokenizeLine(line)
                    self.storeTokens(rawTokens)
                    
                    
        # print(self.tokens)

