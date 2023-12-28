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
        self.memory = np.ones(32, dtype=np.int32)
        #self.memory[6] = 4 

        # test data
        # random memory
        # for i in range(32):
        #     self.memory[i] = np.random.randint(0, 100)
        # # random register
        # for i in range(32):
        #     self.reg[i] = np.random.randint(0, 100)

        self.reg[0] = 0
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
