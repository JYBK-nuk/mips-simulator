from abc import ABC
from typing import Union
from rich.pretty import pprint
from Instructions import Instruction
from MemAndReg import MemAndReg
from colorama import Fore, Back, Style
from collections import defaultdict


def log(string, color=Fore.WHITE):
    print(color + string + Style.RESET_ALL)


class ControlUnit:
    _MemAndReg: 'MemAndReg'
    instructions: list[Instruction]

    cycle: int = 0
    endInstruction = False
    RegWrite = None
    writeReg = None
    writeData = None

    piplineRegistor: dict[str, dict] = {
        "IF/ID": {},
        "ID/EX": {},
        "EX/MEM": {},
        "MEM/WB": {},
    }

    stages: list['BaseStage']

    def __init__(self, MemAndReg: 'MemAndReg', instructions: list[Instruction], pipline: bool):
        self._MemAndReg = MemAndReg
        self.instructions = instructions
        self.pipline = pipline

    def SaveAndGetPiplineRegistor(self, stage: str, data: dict):
        temp = self.piplineRegistor[stage]
        self.piplineRegistor[stage] = data
        return temp

    def start(self):
        if self.pipline:
            while True:
                if self.runPipline() is False:
                    break
        else:
            while True:
                if self.run() is False:
                    break

    def runPipline(self):
        log(F"\n↓ Cycle {(self.cycle) +1} ↓", Back.BLUE + Fore.WHITE)

        # Stages
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        IFOut = self.SaveAndGetPiplineRegistor("IF/ID", self.stages[0].RunWithNop(False))

        pprint(IFOut, expand_all=True)

        log("\nIDStage", Back.WHITE + Fore.BLACK)
        IDOut = self.SaveAndGetPiplineRegistor(
            "ID/EX",
            self.stages[1].RunWithNop(
                self.stages[0].nop,
                IFOut["PC"],
                IFOut["instruction"],
                self.RegWrite,
                self.writeData,
                self.writeReg,
            ),
        )
        pprint(IDOut, expand_all=True)

        log("\nEXStage", Back.WHITE + Fore.BLACK)
        EXOut = self.SaveAndGetPiplineRegistor(
            "EX/MEM",
            self.stages[2].RunWithNop(
                self.stages[1].nop,
                IDOut["PC"],
                IDOut["instruction"],  # 暫時沒用到
                IDOut["immediate"],
                IDOut["control"],  # All control state
                IDOut["ReadData1"],
                IDOut["ReadData2"],
            ),
        )
        pprint(EXOut, expand_all=True)

        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        MEMOut = self.SaveAndGetPiplineRegistor(
            "MEM/WB",
            self.stages[3].RunWithNop(
                self.stages[2].nop,
                EXOut["PC"],
                EXOut["instruction"],  # 暫時沒用到
                EXOut["control"],  # ["MemToReg", "RegWrite", "MemRead", "MemWrite"]
                EXOut["ReadData2"],  # 因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
                # pure passthrough
                EXOut["ALUResult"],
                EXOut["RegDstValue"],
            ),
        )
        pprint(MEMOut, expand_all=True)

        log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].RunWithNop(
            self.stages[3].nop,
            MEMOut["PC"],
            MEMOut["instruction"],  # 暫時沒用到
            MEMOut["control"],  # ["MemToReg", "RegWrite"]
            MEMOut["ReadData"],  # MEM STAGE Read Data
            MEMOut["ALUResult"],  # from EX STAGE ALUresult
            MEMOut["RegDstValue"],  # from EX STAGE RegDst 選的
        )
        if not self.stages[4].nop:
            self.RegWrite = WBOut["control"]["RegWrite"]
            self.writeReg = WBOut["WriteRegister"]
            self.writeData = WBOut["WriteData"]
        pprint(WBOut, expand_all=True)
        self._MemAndReg.print()
        log("\n↑ End Cycle", Back.BLUE + Fore.WHITE)

        # 終止條件
        if self.stages[0].pc >= len(self.instructions):
            return False
        self.cycle += 1
    def run(self):
        log(F"\n↓ Loop {(self.cycle//5)+1} ↓", Back.BLUE + Fore.WHITE)

        # Stages
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        IFOut = self.stages[0].RunWithNop(self.stages[0].pc >= len(self.instructions))
        pprint(IFOut, expand_all=True)

        log("\nIDStage", Back.WHITE + Fore.BLACK)
        IDOut = self.stages[1].RunWithNop(
            self.stages[0].nop,
            IFOut["PC"],
            IFOut["instruction"],
        )
        pprint(IDOut, expand_all=True)

        log("\nEXStage", Back.WHITE + Fore.BLACK)
        EXOut = self.stages[2].RunWithNop(
            self.stages[1].nop,
            IDOut["PC"],
            IDOut["instruction"],
            IDOut["immediate"],
            IDOut["control"],
            IDOut["ReadData1"],
            IDOut["ReadData2"],
        )
        pprint(EXOut, expand_all=True)

        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        MEMOut = self.stages[3].RunWithNop(
            self.stages[2].nop,
            EXOut["PC"],
            EXOut["instruction"],
            EXOut["control"],
            EXOut["ReadData2"],
            # pure passthrough
            EXOut["ALUResult"],
            EXOut["RegDstValue"],
        )
        pprint(MEMOut, expand_all=True)

        log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].RunWithNop(
            self.stages[3].nop,
            MEMOut["PC"],
            MEMOut["instruction"],
            MEMOut["control"],
            MEMOut["ReadData"],
            MEMOut["ALUResult"],
            MEMOut["RegDstValue"],
        )
        pprint(WBOut, expand_all=True)
        self._MemAndReg.print()

        log(F"\n↑ Cycles : {self.cycle} ↑", Back.CYAN + Fore.WHITE)

        # 終止條件
        if self.stages[0].pc >= len(self.instructions):
            return False


class BaseStage(ABC):
    _ControlUnit: 'ControlUnit'
    nop: bool = False
    output: dict = {}

    def __init__(self, ControlUnit: 'ControlUnit'):
        self._ControlUnit = ControlUnit

    def RunWithNop(self, nop: bool, *args):
        if not self._ControlUnit.pipline:
            self._ControlUnit.cycle += 1
        self.nop = nop
        self.EvenNop(*args)
        if nop:
            dict_ = defaultdict(lambda: None)
            dict_["nop"] = True
            return dict_
        return self.execute(*args)

    def EvenNop(self, *args):  # 就算是nop也要執行的
        pass

    def execute(self):  # 這個NOP = True的時候不會執行
        pass

    def showData(self):
        pprint(self.output, expand_all=True)
