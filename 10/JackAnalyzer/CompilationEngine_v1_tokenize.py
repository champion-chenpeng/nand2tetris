import JackTokenizer
class CompilationEngine:
    # first version, simple list all tokens from tokenizer

    def __init__(self, file, output_file):
        self.file = file
        self.output_file = output_file
        self.tokenizer = JackTokenizer.JackTokenizer(file)
        self.output = open(self.output_file, "w")
        self.indent = 0
        self.compileClass()
        self.close()

    def close(self):
        self.output.close()

    def snack2camel(self, snack_str):
        camel_str = ""
        snack_str = snack_str.split("_")
        for i in range(len(snack_str)):
            token = snack_str[i].lower()
            if i == 0:
                camel_str += token
            else:
                camel_str += token.capitalize()
        return camel_str
    
    def compileClass(self):
        self.writeTag("tokens")
        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            tokenType = self.tokenizer.currentTokenType
            tokenType = self.snack2camel(tokenType)
            tokenValue = self.tokenizer.currentTokenValue
            self.output.write("<{0}> {1} </{0}>\n".format(tokenType, tokenValue))
        self.writeTag("/tokens")
    
    def writeTag(self, tag):
        self.output.write("<" + tag + ">\n")
        self.indent += 1
