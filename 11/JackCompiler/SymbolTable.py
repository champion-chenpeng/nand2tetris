class SymbolTable:
    def __init__(self):
        self.classScope = {}
        self.subroutineScope = {}
        self.index_dict = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0
        }
        self.TYPE = 0
        self.KIND = 1
        self.INDEX = 2
    
    def reset(self):
        self.classScope = {}
        self.subroutineScope = {}
        self.index_dict = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0
        }
        
    def define(self, name, type, kind):
        if kind == "STATIC" or kind == "FIELD":
            self.classScope[name] = [type, kind, self.index_dict[kind]]
        elif kind == "ARG" or kind == "VAR":
            self.subroutineScope[name] = [type, kind, self.index_dict[kind]]
        self.index_dict[kind] += 1

    def varCount(self, kind):
        return self.index_dict[kind]
    
    def kindOf(self, name):
        if name in self.subroutineScope:
            return self.subroutineScope[name][self.KIND]
        elif name in self.classScope:
            return self.classScope[name][self.KIND]
        else:
            return "NONE"
        
    def typeOf(self, name):
        if name in self.subroutineScope:
            return self.subroutineScope[name][self.TYPE]
        elif name in self.classScope:
            return self.classScope[name][self.TYPE]
        else:
            return None
        
    def indexOf(self, name):
        if name in self.subroutineScope:
            return self.subroutineScope[name][self.INDEX]
        elif name in self.classScope:
            return self.classScope[name][self.INDEX]
        else:
            return None
