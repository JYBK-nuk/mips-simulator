from abc import ABC
from rich.pretty import pprint
from Instructions import Instruction
from MemAndReg import MemAndReg
from colorama import Fore, Back, Style


def log(string, color=Fore.WHITE):
    print(color + string + Style.RESET_ALL)


class ControlUnit:
    _MemAndReg: 'MemAndReg'
    instructions: list[Instruction]
    pipline: bool = True
    state = {
        "RegDst": False,
        "ALUSrc": False,
        "Branch": False,
        "MemRead": False,
        "MemWrite": False,
        "RegWrite": False,
        "MemToReg": False,
        
    }

    stages: list['BaseStage']

    def __init__(self, MemAndReg: 'MemAndReg', instructions: list[Instruction]):
        self._MemAndReg = MemAndReg
        self.instructions = instructions
        # IF excute(self)
        # ID excute(self, pc, instruction: Instruction)
        

    def run(self):
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        IFOut = self.stages[0].excute()
        pprint(IFOut, expand_all=True)

        log("\nIDStage", Back.WHITE + Fore.BLACK)
        IDOut = self.stages[1].excute(IFOut["PC"], IFOut["instruction"])
        pprint(IDOut, expand_all=True)

        log("\nEXStage", Back.WHITE + Fore.BLACK)
        EXOut = self.stages[2].excute(
            IDOut["PC"], 
            IDOut["instruction"], # 暫時沒用到
            IDOut["immediate"],
            IDOut["control"],
            IDOut["ReadData1"],
            IDOut["ReadData2"],
        )
        pprint(EXOut, expand_all=True)
        
        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        MEMOut = self.stages[3].excute(
            EXOut["PC"], 
            EXOut["instruction"], # 暫時沒用到
            EXOut["control"],
            IDOut["ReadData2"],#因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
            EXOut["ALUresult"]
        )
        pprint(MEMOut, expand_all=True)
        #control 要留memToReg跟RegWrite就好
        log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].excute(
            MEMOut["PC"], 
            MEMOut["instruction"], # 暫時沒用到
            MEMOut["control"],
            MEMOut["ReadData"],#因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
            MEMOut["ALUresult"]
        )
        pprint(WBOut, expand_all=True)
        


        #print所有reg跟mem
        pprint(self._MemAndReg)
        
        

class BaseStage(ABC):
    _ControlUnit: 'ControlUnit'
    nop: bool = False
    output: dict = {}

    def __init__(self, ControlUnit: 'ControlUnit'):
        self._ControlUnit = ControlUnit

    def excute(self):
        pass

    def showData(self):
        pprint(self.output, expand_all=True)
