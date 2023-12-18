import numpy as np
from rich.pretty import pprint
from colorama import Fore, Back, Style


def log(string, color=Fore.WHITE):
    print(color + string + Style.RESET_ALL)


class MemAndReg:
    reg: np.ndarray
    memory: np.ndarray

    def __init__(self):
        self.reg = np.ones(32, dtype=np.int32)
        self.reg[0] = 0
        self.memory = np.ones(32, dtype=np.int32)

        # test data
        # self.memory[2] = 4
        # self.memory[4] = 6

    def getReg(self, key: str):
        # $0 => 0
        log(f"Get {self.reg[int(key[1:])]} from Reg{key}", Fore.GREEN)
        return self.reg[int(key[1:])]

    def setReg(self, key: str, value: int):
        log(f"Set Reg{key} to {value}", Fore.GREEN)
        self.reg[int(key[1:])] = value
        return value

    def getMem(self, address: int):
        log(f"Get {self.memory[address]} from Mem${address}", Fore.GREEN)
        return self.memory[address]

    def setMem(self, address: int, value: int):
        log(f"Set Mem${address} to {value}", Fore.GREEN)
        self.memory[address] = value
        return value

    def print(self):
        print("Reg:")
        pprint(self.reg)
        print("Mem:")
        pprint(self.memory)
