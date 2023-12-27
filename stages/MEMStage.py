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
        
        result=self.SW_datahazardUnit()
        if result == 'ALU_HAZARD':
            ReadData2=forwardingValue
        elif result == 'MEM_HAZARD':
            pass
        print(ReadData2)
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

        # forwarding 記得如果是Pipe才有的功能+一下and self._ControlUnit.pipeline==True
        if control["MemToReg"] == 1 and self._ControlUnit.pipeline==True:
            if (
                self.output["RegDstValue"]
                == dict(self._ControlUnit.pipelineRegister["ID/EX"]["instruction"])[
                    "rs"
                ]
            ):
                self._ControlUnit.pipelineRegister["ID/EX"]["ReadData1"] = ReadData
            if (
                self.output["RegDstValue"]
                == dict(self._ControlUnit.pipelineRegister["ID/EX"]["instruction"])[
                    "rt"
                ]
            ):
                self._ControlUnit.pipelineRegister["ID/EX"]["ReadData2"] = ReadData

        self.output["control"] = {}
        for c in ["MemToReg", "RegWrite"]:
            self.output["control"][c] = control[c]
        return self.output
    def SW_datahazardUnit(self):#如果hazard發生 就把ReadData2改成forwarfing來的值
        global forwardingValue
        MemStage=self._ControlUnit.pipelineRegister['EX/MEM']
        WbStage=self._ControlUnit.pipelineRegister['MEM/WB']
        if MemStage['nop']==True or WbStage['nop']==True:
            return
        if MemStage['control']['MemWrite']==1:
            if WbStage['control']["RegWrite"] == 1 and WbStage["RegDstValue"]  != '$0':
                if MemStage["RegDstValue"]==WbStage["RegDstValue"]:
                    forwardingValue=WbStage['ALUResult']
                    return 'ALU_HAZARD'
            pass
            #如果前一指令是alu能直接抓
        pass