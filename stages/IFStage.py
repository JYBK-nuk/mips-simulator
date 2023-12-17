from stages.ControlUnit import BaseStage, ControlUnit


class IFStage(BaseStage):
    pc: int = 0

    def __init__(self, ParentUnit: ControlUnit, pc: int = 0):
        super().__init__(ParentUnit)
        self.pc = pc

    def execute(self):
        super().execute()
        self.output = {
            "PC": self.pc + 1,
            "instruction": self._ControlUnit.instructions[self.pc],
            "nop": self.nop,
        }
        self.pc += 1
        return self.output
