from stages.ControlUnit import BaseStage, ControlUnit
from Instructions import Instruction, Format


class WBStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def excute(self, PC, instruction: Instruction, control, ALUresult, ReadData):
        if control["RegWrite"]:
            if control["MemToReg"]:
                self._ControlUnit._MemAndReg.setReg(instruction.dict_["rt"], ReadData)
            else:
                self._ControlUnit._MemAndReg.setReg(instruction.dict_["rt"], ALUresult)
        return {
            "PC": PC,
            "instruction": instruction,
            "control": control,
            "ALUresult": ALUresult,
            "ReadData": ReadData,
        }
