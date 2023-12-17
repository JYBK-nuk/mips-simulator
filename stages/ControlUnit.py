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
    cycle: int = 0
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

    def run(self):
        RegWrite = None
        writeReg = None
        writeData = None
        if self.stages[0].pc >= len(self.instructions):
            return False
        self.cycle += 1
        log(F"\nCycle {self.cycle}", Back.BLUE + Fore.WHITE)

        # Stages
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        IFOut = self.stages[0].excute()
        pprint(IFOut, expand_all=True)

        log("\nIDStage", Back.WHITE + Fore.BLACK)
        IDOut = self.stages[1].excute(
            IFOut["PC"], IFOut["instruction"], RegWrite, writeData, writeReg
        )
        pprint(IDOut, expand_all=True)

        log("\nEXStage", Back.WHITE + Fore.BLACK)
        EXOut = self.stages[2].excute(
            IDOut["PC"],
            IDOut["instruction"],  # 暫時沒用到
            IDOut["immediate"],
            IDOut["control"],  # All control state
            IDOut["ReadData1"],
            IDOut["ReadData2"],
        )
        pprint(EXOut, expand_all=True)

        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        MEMOut = self.stages[3].excute(
            EXOut["PC"],
            EXOut["instruction"],  # 暫時沒用到
            EXOut["control"],  # ["MemToReg", "RegWrite", "MemRead", "MemWrite"]
            EXOut["ReadData2"],  # 因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
            # pure passthrough
            EXOut["ALUResult"],
            EXOut["RegDstValue"],
        )
        pprint(MEMOut, expand_all=True)

        log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].excute(
            MEMOut["PC"],
            MEMOut["instruction"],  # 暫時沒用到
            MEMOut["control"],  # ["MemToReg", "RegWrite"]
            MEMOut["ReadData"],  # MEM STAGE Read Data
            MEMOut["ALUResult"],  # from EX STAGE ALUresult
            MEMOut["RegDstValue"],  # from EX STAGE RegDst 選的
        )
        RegWrite = WBOut["control"]["RegWrite"]
        writeReg = WBOut["WriteRegister"]
        writeData = WBOut["WriteData"]
        pprint(WBOut, expand_all=True)
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
