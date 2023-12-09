class Parser:
    def __init__(self, file):
        self.file = file
        self.commands = []
        self.lineNumber = 0
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
        self.lineNumber = 0
        self.currentCommand = ""
    
    def hasMoreCommands(self):
        return self.lineNumber < len(self.commands)
    
    def advance(self):
        self.currentCommand = self.commands[self.lineNumber]
        self.lineNumber += 1

    def commandType(self):
        cmd = self.currentCommand.split(" ")[0]
        if cmd == "push":
            return "C_PUSH"
        elif cmd == "pop":
            return "C_POP"
        else:
            return "C_ARITHMETIC"
        
    def arg1(self):
        if self.commandType() != "C_RETURN":
            if self.commandType() == "C_ARITHMETIC":
                return self.currentCommand
            else:
                return self.currentCommand.split(" ")[1]
    
    def arg2(self):
        if self.commandType() in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return self.currentCommand.split(" ")[2]
    
    
