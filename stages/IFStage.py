from stages.ControlUnit import BaseStage, ControlUnit
from collections import defaultdict


class IFStage(BaseStage):
    pc: int = 0

    def __init__(self, ParentUnit: ControlUnit, pc: int = 0):
        super().__init__(ParentUnit)
        self.pc = pc

    def execute(self):
        super().execute()
        if self.pc >= len(self._ControlUnit.instructions):
            self.output = defaultdict(lambda: None)
            self.output["nop"] = True
            return self.output
        self.output = {
            "PC": self.pc + 1,
            "instruction": self._ControlUnit.instructions[self.pc],
            "nop": self.nop,
        }
        self.pc += 1
        return self.output
