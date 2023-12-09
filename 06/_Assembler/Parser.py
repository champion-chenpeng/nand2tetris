class Parser:
    def __init__(self, file):
        self.file = file
        self.commands = []
        self.inlineNumber = 0
        self.outlineNumber = 0
        self.currentCommand = ""
        self.reset()
    
    def reset(self):
        self.commands = []
        with open(self.file, "r") as input:
            for line in input:
                line = line.strip()
                if line != "" and line[0:2] != "//":
                    if "//" in line:
                        line = line[0:line.index("//")].strip()
                    self.commands.append(line)
        self.inlineNumber = 0
        self.currentCommand = ""
    
    def hasMoreCommands(self):
        return self.inlineNumber < len(self.commands)
    
    def advance(self):
        self.currentCommand = self.commands[self.inlineNumber]
        self.inlineNumber += 1
        self.outlineNumber += 1

    def commandType(self):
        if self.currentCommand[0] == "@":
            return "A_COMMAND"
        elif self.currentCommand[0] == "(":
            return "L_COMMAND"
        else:
            return "C_COMMAND"
        
    def symbol(self):
        if self.commandType() == "A_COMMAND":
            return self.currentCommand[1:]
        elif self.commandType() == "L_COMMAND":
            return self.currentCommand[1:-1]
        
    def dest(self):
        if self.commandType() == "C_COMMAND":
            if "=" in self.currentCommand:
                return self.currentCommand[0:self.currentCommand.index("=")]
            else:
                return ""
        
    def comp(self):
        if self.commandType() == "C_COMMAND":
            if "=" in self.currentCommand:
                return self.currentCommand[self.currentCommand.index("=")+1:]
            else:
                return self.currentCommand[0:self.currentCommand.index(";")]
            
    def jump(self):
        if self.commandType() == "C_COMMAND":
            if ";" in self.currentCommand:
                return self.currentCommand[self.currentCommand.index(";")+1:]
            else:
                return ""
            
    def getLineNumber(self):
        return self.outlineNumber

    def getCurrentCommand(self):
        return self.currentCommand

