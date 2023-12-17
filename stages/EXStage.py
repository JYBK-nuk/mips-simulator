from Instructions import Format, Instruction
from stages.ControlUnit import BaseStage, ControlUnit


class EXStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)
        self.ParentUnit = ParentUnit

    def excute(
        self,
        pc: int,
        instruction: Instruction,
        immediate: int,
        control: dict,
        ReadData1: int,
        ReadData2: int,
    ):
        super().excute()
        alu_op = control["ALUOp"]

        if control["ALUSrc"] == 1:
            # lw sw, src = immediate
            ReadData2 = immediate

        # Forwarding
        if self.ParentUnit.prev_instruction is not None:
            prev_instruction = self.ParentUnit.prev_instruction
            prev_dest_reg = prev_instruction.dest_reg

            if (
                prev_instruction.opcode == "lw"
                and prev_dest_reg == instruction.src_reg1
            ):
                ReadData1 = prev_instruction.ALUresult

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

        return self.output

    def ALU(self, ALUop: str, data1: int, data2: int):
        if ALUop == "add":
            value = data1 + data2
        elif ALUop == "sub":
            value = data1 - data2
        return value
