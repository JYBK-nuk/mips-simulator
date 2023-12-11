from Instructions import Format, Instruction
from stages.ControlUnit import BaseStage, ControlUnit


class EXStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def excute(
        self, pc: int, instruction: Instruction,immediate:int, control: dict, ReadData1: int, ReadData2: int
    ):
        super().excute()
        alu_op = control["ALUOp"]

        if control["ALUSrc"] == 1:
            # lw sw , src = immediate
            ReadData2 = immediate#改動這邊因lw sw是用immediate

        if alu_op == "add":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": self.ALU("add", ReadData1, ReadData2),
            }
        elif alu_op == "sub":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": self.ALU("sub", ReadData1, ReadData2),
            }

        self.output["control"] = control

        # TODO : Branch
        # if control["Branch"] == 1:
        # if self.output["ALUresult"] == 0: # 相等
        # .... pc = pc + 4 + 4*immediate
        return self.output

    def ALU(self, ALUop: str, data1: int, data2: int):
        if ALUop == "add":  # 00
            value = data1 + data2
        elif ALUop == "sub":  # 01
            value = data1 - data2
        return value
