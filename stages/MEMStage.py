from stages.ControlUnit import BaseStage, ControlUnit
from Instructions import Instruction, Format


class MEMStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def execute(
        self,
        pc: int,
        instruction: Instruction,
        control: dict,
        ReadData2: int,
        ALUresult: int,
        AddrResult: int,
        RegDstValue: str,  # 這個是要存到哪個暫存器 在EXStage已經算好了 傳下去
    ):
        super().execute()
        # 為了我們的記憶體是直接以4byte為單位 np.int32 才這樣寫
        if control["MemWrite"] == 1 or control["MemRead"] == 1:
            if ALUresult % 4 != 0:
                raise Exception("Memory address must be multiple of 4")
            ALUresult = ALUresult // 4

        if control["MemWrite"] == 1:  # 大概是sw會用到
            self._ControlUnit._MemAndReg.setMem(ALUresult, ReadData2)
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": ALUresult,
                "ReadData": None,
                "RegDstValue": RegDstValue,
            }
        if control["MemRead"] == 1:
            # 從mem array 讀出 ReadData就是如果lw有讀出來的話 要送到wb的值
            ReadData = self._ControlUnit._MemAndReg.getMem(ALUresult)
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": ALUresult,
                "ReadData": ReadData,
                "RegDstValue": RegDstValue,
            }
        elif control["Branch"] == 1:  # 如果branch
            if ALUresult == 0:  # 看相減結果是否相等 from ex
                self.output = {
                    "PC": AddrResult,
                    "instruction": instruction,
                    "nop": self.nop,
                    "ALUResult": ALUresult,
                    "ReadData": None,
                    "RegDstValue": RegDstValue,
                }
                self._ControlUnit.stages[0].pc = AddrResult  # 設定下次要執行的pc 反正沒branch就會跟原本一樣

            else:
                self.output = {
                    "PC": pc,
                    "instruction": instruction,
                    "nop": self.nop,
                    "ALUResult": ALUresult,
                    "ReadData": None,
                    "RegDstValue": RegDstValue,
                }
        else:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": ALUresult,
                "ReadData": None,
                "RegDstValue": RegDstValue,
            }
        # if control["branch"] == 1:
        # undo
        # 該stage 要傳給下一個stage的 control 值
        self.output["control"] = {}
        for c in ["MemToReg", "RegWrite"]:
            self.output["control"][c] = control[c]
        return self.output
