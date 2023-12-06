import numpy as np


class MemAndReg:
    reg: np.ndarray
    memory: np.ndarray

    def __init__(self):
        self.reg = np.ones(32, dtype=np.int32)
        self.reg[0] = 0
        self.memory = np.ones(32, dtype=np.int32)



    def getReg(self, key: str):
        # $0 => 0
        return self.reg[int(key[1:])]

    def setReg(self, key: str, value: int):
        self.reg[int(key[1:])] = value
        return value

    def getMem(self, address: int):
        return self.memory[address]

    def setMem(self, address: int, value: int):
        self.memory[address] = value
        return value

    def __repr__(self) -> str:
        return "Reg:\t" + str(self.reg) + "\nMem:\t" + str(self.memory)
