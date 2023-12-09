from enum import Enum

class CommandType(Enum):
    C_PUSH = "C_PUSH"
    C_POP = "C_POP"
    C_ARITHMETIC = "C_ARITHMETIC"
    # Add other command types as needed

class CodeWriter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(file_name + ".asm", "w")
        self.init_constants()
        self.bootstrap()

    def init_constants(self):
        self.SEG_LOCAL = "local"
        self.SEG_ARGUMENT = "argument"
        self.SEG_THIS = "this"
        self.SEG_THAT = "that"
        self.SEG_TEMP = "temp"
        self.SEG_POINTER = "pointer"
        self.SEG_STATIC = "static"
        self.SEG_CONSTANT = "constant"

        self.list_pointer = [self.SEG_LOCAL, self.SEG_ARGUMENT, self.SEG_THIS, self.SEG_THAT]
        self.list_single = ["neg", "not"]
        self.list_compare = ["eq", "gt", "lt"]

        self.RET = "R14"
        self.saved_frame = [self.RET, "LCL", "ARG", "THIS", "THAT"]

    def bootstrap(self):
        self.init_ram()

    def init_ram(self):
        self.writter_write(["@256", "D=A", "@SP", "M=D"])

    def close(self):
        self.end_loop()
        self.file.close()

    def writter_write(self, lines):
        for line in lines:
            self.file.write(line + "\n")

    def write_push_x(self, value):
        self.writter_write(["@SP", "A=M", f"M={value}", "@SP", "M=M+1"])

    def write_pop_d(self):
        self.writter_write(["@SP", "M=M-1", "A=M", "D=M"])

    def address_i(self, segment, index):
        lines = []
        if segment == self.SEG_STATIC:
            lines.append(f"@{self.file_name}.{index}")
        else:
            lines.extend([
                f"@{index}", "D=A",
                f"@{self.get_segment_address(segment)}",
                "A=D+A"
            ])
        return lines

    def get_segment_address(self, segment):
        return {
            self.SEG_LOCAL: "LCL",
            self.SEG_ARGUMENT: "ARG",
            self.SEG_THIS: "THIS",
            self.SEG_THAT: "THAT",
            self.SEG_TEMP: "R5",
            self.SEG_POINTER: "THIS",
        }.get(segment, "")

    def write_push_pop(self, command_type, segment, index):
        if command_type == CommandType.C_PUSH:
            self.writter_write(self.address_i(segment, index) + ["D=M"])
            self.write_push_x("D")
        elif command_type == CommandType.C_POP:
            self.writter_write(self.address_i(segment, index) + ["D=A", "@R13", "M=D"])
            self.write_pop_d()
            self.writter_write(["@R13", "A=M", "M=D"])

    def write_get_args(self, command):
        self.write_pop_d()
        if command not in self.list_single:
            self.write_pop_d()

    def write_compare(self, command):
        label = f"{self.caller_function}$cmp.{self.N_compare}"
        true_label = f"{label}.TRUE"
        end_label = f"{label}.END"
        self.writter_write([
            "D=M-D",
            f"@{true_label}",
            f"D;J{command.upper()}",
            "D=0",
            f"@{end_label}",
            "0;JMP",
            f"({true_label})",
            "D=-1",
            f"({end_label})"
        ])
        self.N_compare += 1

    def write_arithmetic_d(self, command):
        if command in self.list_single:
            self.writter_write([f"D={self.dict_op[command]}D"])
        else:
            if command in self.list_compare:
                self.write_compare(command)
            else:
                self.writter_write([f"D=M{self.dict_op[command]}D"])

    def write_arithmetic(self, command):
        self.write_get_args(command)
        self.write_arithmetic_d(command)
        self.write_push_x("D")

    def write_label(self, label):
        self.writter_write([f"({self.caller_function}${label})"])

    def write_goto(self, label):
        self.writter_write([f"@{self.caller_function}${label}", "0;JMP"])

    def write_if(self, label):
        self.write_pop_d()
        self.writter_write([f"@{self.caller_function}${label}", "D;JNE"])

    def write_saved_frame(self, name):
        self.writter_write([f"@{name}", "D=M"])
        self.write_push_x("D")

    def write_restore_frame(self, frame, index):
        self.writter_write([f"@{index}", "D=A", f"@{frame}", "A=M-D", "D=M", f"@{self.saved_frame[-index]}", "M=D"])

    def write_call(self, function_name, num_args):
        callee_function = function_name
        return_address = f"{self.caller_function}$ret.{self.N_ret}"
        self.N_ret += 1
        # push return_address
        self.writter_write([f"@{return_address}", "D=A"])
        self.write_push_x("D")
        # push saved_frame
        for name in self.saved_frame[1:]:  # exclude RET
            self.write_saved_frame(name)
        # ARG = SP - num_args - 5
        self.writter_write([
            "@SP", "D=M",
            f"@{num_args}", "D=D-A",
            "@5", "D=D-A",
            "@ARG", "M=D"
        ])
        # LCL = SP
        self.writter_write(["@SP", "D=M", "@LCL", "M=D"])
        # goto callee_function
        self.writter_write([f"@{callee_function}", "0;JMP"])
        # (return_address)
        self.writter_write([f"({return_address})"])

    def write_return(self):
        # *FRAME = *LCL
        frame = "R13"
        self.writter_write(["@LCL", "D=M", f"@{frame}", "M=D"])
        # **ARG = pop(), return value
        self.write_pop_d()
        self.writter_write(["@ARG", "A=M", "M=D"])
        # *SP = ARG + 1
        self.writter_write(["@ARG", "D=M+1", "@SP", "M=D"])
        # write restore frame
        for i in range(1, len(self.saved_frame) + 1):
            self.write_restore_frame(frame, i)
        # goto RET
        self.writter_write([f"@{self.RET}", "A=M", "0;JMP"])

    def write_function(self, function_name, num_locals):
        self.caller_function = function_name
        self.N_ret = 0
        self.writter_write([f"({self.caller_function})"])
        # init local with 0
        for _ in range(int(num_locals)):
            self.write_push_x("0")
