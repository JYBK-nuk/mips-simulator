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
    pipeline: bool = True
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

        # Initialize pipeline registers
        self.IFID = {}
        self.IDEX = {}
        self.EXMEM = {}
        self.MEMWB = {}

    def run(self):
        for instruction in self.instructions:
            log(f"\nExecuting Instruction: {instruction}", Fore.YELLOW)

            log("IFStage", Back.WHITE + Fore.BLACK)
            self.stages[0].execute()
            self.IFID = self.stages[0].output
            pprint(self.IFID, expand_all=True)

            log("\nIDStage", Back.WHITE + Fore.BLACK)
            self.stages[1].execute()
            self.IDEX = self.stages[1].output
            pprint(self.IDEX, expand_all=True)

            log("\nEXStage", Back.WHITE + Fore.BLACK)
            self.stages[2].execute()
            self.EXMEM = self.stages[2].output
            pprint(self.EXMEM, expand_all=True)

            log("\nMEMStage", Back.WHITE + Fore.BLACK)
            self.stages[3].execute()
            self.MEMWB = self.stages[3].output
            pprint(self.MEMWB, expand_all=True)

            log("\nWBStage", Back.WHITE + Fore.BLACK)
            self.stages[4].execute()
            pprint(self.stages[4].output, expand_all=True)


class BaseStage(ABC):
    _ControlUnit: "ControlUnit"
    nop: bool = False
    output: dict = {}

    def __init__(self, ControlUnit: "ControlUnit"):
        self._ControlUnit = ControlUnit

    def execute(self):
        pass

    def showData(self):
        pprint(self.output, expand_all=True)
