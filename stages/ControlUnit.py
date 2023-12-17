from abc import ABC
from rich.pretty import pprint
from Instructions import Instruction
from MemAndReg import MemAndReg
from colorama import Fore, Back, Style


def log(string, color=Fore.WHITE):
    print(color + string + Style.RESET_ALL)


class ControlUnit:
    _MemAndReg: "MemAndReg"
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

    stages: list["BaseStage"]

    def __init__(self, MemAndReg: "MemAndReg", instructions: list[Instruction]):
        self.prev_instruction: Instruction = None
        self._MemAndReg = MemAndReg
        self.instructions = instructions
        # IF excute(self)
        # ID excute(self, pc, instruction: Instruction)

    def run(self):
        for instruction in self.instructions:
            log(f"\nExecuting Instruction: {instruction}", Fore.YELLOW)
            log("IFStage", Back.WHITE + Fore.BLACK)
            IFOut = self.stages[0].excute()
            pprint(IFOut, expand_all=True)

            log("\nIDStage", Back.WHITE + Fore.BLACK)
            IDOut = self.stages[1].excute(IFOut["PC"], instruction)
            pprint(IDOut, expand_all=True)

            log("\nEXStage", Back.WHITE + Fore.BLACK)
            EXOut = self.stages[2].excute(
                IDOut["PC"],
                IDOut["instruction"],
                IDOut["immediate"],
                IDOut["control"],
                IDOut["ReadData1"],
                IDOut["ReadData2"],
            )
            pprint(EXOut, expand_all=True)

            log("\nMEMStage", Back.WHITE + Fore.BLACK)
            MEMOut = self.stages[3].excute(
                EXOut["PC"],
                EXOut["instruction"],
                EXOut["control"],
                IDOut["ReadData2"],
                EXOut["ALUresult"],
            )
            pprint(MEMOut, expand_all=True)

            log("\nWBStage", Back.WHITE + Fore.BLACK)
            WBOut = self.stages[4].excute(
                MEMOut["PC"],
                MEMOut["instruction"],
                MEMOut["control"],
                MEMOut["ALUresult"],
                MEMOut["ReadData"],
            )
            pprint(WBOut, expand_all=True)


class BaseStage(ABC):
    _ControlUnit: "ControlUnit"
    nop: bool = False
    output: dict = {}

    def __init__(self, ControlUnit: "ControlUnit"):
        self._ControlUnit = ControlUnit

    def excute(self):
        pass

    def showData(self):
        pprint(self.output, expand_all=True)
