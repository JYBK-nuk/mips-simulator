from stages.ControlUnit import BaseStage, ControlUnit
from Instructions import Instruction


class WBStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def excute(
        self,
        pc: int,
        instruction: Instruction,
        control: dict,
        ReadData: int,  # MEM STAGE Read Data
        ALUResult: int,
        # passthrough
        RegDstValue: str,  # from EX STAGE RegDst 選的
    ):
        super().excute()
        self.output = {
            "PC": pc,
            "instruction": instruction,
            "nop": self.nop,
            "WriteRegister": None,
            "WriteData": None,
        }
        self.output["WriteRegister"] = RegDstValue
        
        if control["MemToReg"] == 1:  # 切換 ReadData  or ALUresult
            self.output["WriteData"] = ReadData
        else:
            self.output["WriteData"] = ALUResult

        # 該stage 要傳給下一個stage的 control 值
        self.output["control"] = {}
        for c in ["RegWrite"]:
            self.output["control"][c] = control[c]
        return self.output
