from stages.ControlUnit import BaseStage, ControlUnit
from Instructions import Instruction

class WBStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)
        
    def excute(self, pc: int, instruction: Instruction, control: dict, ReadData: int, ALUresult: int):
        super().excute()
        
        if control["RegWrite"] == 1:
          reg = instruction.dict_['rd'] if control["RegDst"] == 1 else instruction.dict_['rt'] 
          self._ControlUnit._MemAndReg.setReg(reg, ReadData)
          self.output["WriteRegister"] = reg
          self.output["WriteData"] = ReadData
        else:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": ALUresult,
                "WriteRegister": None,
                "WriteData": None
            }
            
        self.output["control"] = control
        return self.output