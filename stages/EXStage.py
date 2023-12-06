from Instructions import Format, Instruction
from stages.ControlUnit import BaseStage, ControlUnit


class EXStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)
        # PC is PC+1 from IFStage
        self.stageData = {"PC": 0, "instruction": "", "nop": False}

    def excute(self, pc:int, instruction: Instruction):
        super().excute()
        if instruction.format == Format.RFORMAT:
            if instruction.opcode == "add":
                pass
            elif instruction.opcode == "sub":
                pass
        elif instruction.format == Format.IFORMAT:
            if instruction.opcode == "lw":
                pass
            elif instruction.opcode == "sw":
                pass
        elif instruction.format == Format.JFORMAT:
            pass
        return self.output

