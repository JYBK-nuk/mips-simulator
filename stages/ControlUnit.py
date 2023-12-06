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
        EXOut = self.stages[2].excute(IDOut["PC"], IDOut["instruction"])
        pprint(EXOut, expand_all=True)


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
