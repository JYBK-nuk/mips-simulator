from Instructions import Format, Instruction
from stages.ControlUnit import BaseStage, ControlUnit


class EXStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def execute(
        self,
        pc: int,
        instruction: Instruction,
        immediate: int,
        control: dict,
        ReadData1: int,
        ReadData2: int,
    ):
        super().execute()
        alu_op = control["ALUOp"]
        inputReadData2 = ReadData2  # if MemWrite == 1 MEM STAGE 會用到

        if control["ALUSrc"] == 1:
            # lw sw , ReadData2要變成讀取immediate
            # 例如 lw 是 BaseAddress + Offset 的部分 (ReadData1 + immediate)
            # ex : lw $t0, 4($t1) 4就是immediate
            # (所以要記得在MEMStage要讀取ReadData2要除以4才會是在記憶體中的位置)
            # ps : 我們的記憶體是直接以4byte為單位 np.int32
            ReadData2 = immediate

            # 為了我們的記憶體是直接以4byte為單位 np.int32 才這樣寫
            if control["MemWrite"] == 1 or control["MemRead"] == 1:
                if immediate % 4 != 0:
                    raise Exception("Immediate must be multiple of 4")
                ReadData2 = ReadData2 // 4

        if alu_op == "add":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": self.ALU("add", ReadData1, ReadData2),
            }
        elif alu_op == "sub":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": self.ALU("sub", ReadData1, ReadData2),
            }

        # TODO : Branch
        # if control["Branch"] == 1:
        # if self.output["ALUResult"] == 0: # 相等
        # .... pc = pc + 4 + 4*immediate
        # 我們只要pc = pc(這裡的在IF+過1了) + immediate
            
        #

        if control["RegDst"] == 1:
            self.output["RegDstValue"] = instruction.dict_['rd']
        else:
            self.output["RegDstValue"] = instruction.dict_['rt']

        self.output["ReadData2"] = inputReadData2  # 這個是要傳給MEMStage的

        # 該stage 要傳給下一個stage的 control 值
        self.output["control"] = {}
        for c in ["MemToReg", "RegWrite", "MemRead", "MemWrite"]:
            self.output["control"][c] = control[c]
        return self.output

    def ALU(self, ALUop: str, data1: int, data2: int):
        if ALUop == "add":  # 00
            value = data1 + data2
        elif ALUop == "sub":  # 01
            value = data1 - data2
        return value
