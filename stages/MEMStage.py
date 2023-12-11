from stages.ControlUnit import BaseStage, ControlUnit
from Instructions import Instruction, Format

class MEMStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)
        
    def excute(self, pc: int, instruction: Instruction, control: dict, ReadData2: int ,ALUresult: int):
        super().excute()
        
        if control["MemWrite"] == 1: #大概是sw會用到
            #(addr(need/4),value)
            self._ControlUnit._MemAndReg.setMem(int(ALUresult/4), ReadData2)
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": ALUresult,
                "ReadData": 'setSuccess'
            }
        if control["MemRead"] == 1:
            #從mem array 讀出 ReadData就是如果lw有讀出來的話 要送到wb的值
            print(int(ALUresult)/4)
            ReadData=self._ControlUnit._MemAndReg.getMem(int(ALUresult/4))
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": ALUresult,
                "ReadData": ReadData
            }
        else:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUresult": ALUresult,
                "ReadData": 'null'
            }
        #if control["branch"] == 1:
            #undo
            
        self.output["control"] = control
        return self.output