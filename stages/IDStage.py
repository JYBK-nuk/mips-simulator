from typing import Dict, Union
from Instructions import Instruction, Format
from stages.ControlUnit import BaseStage, ControlUnit


class IDStage(BaseStage):
    pc: int
    readData1: int
    readData2: int

    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def excute(self, pc, instruction: Instruction):
        super().excute()
        control: Dict[str, int] = {
            "RegDst": -1,
            "ALUSrc": -1,
            "MemToReg": -1,
            "RegWrite": -1,
            "MemRead": -1,
            "MemWrite": -1,
            "Branch": -1,
        }
        if instruction.format == Format.RFORMAT:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ReadData1": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rs"]),
                "ReadData2": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rt"]),
                #
                "rd": dict(instruction)["rd"] if "rd" in dict(instruction) else None,
                "shamt": dict(instruction)["shamt"] if "shamt" in dict(instruction) else None,
                "funct": dict(instruction)["funct"] if "funct" in dict(instruction) else None,
                #
            }
            state = [1, 0, 0, 1, 0, 0, 0]

        elif instruction.format == Format.IFORMAT:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ReadData1": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rs"]),
                "ReadData2": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rt"]),
                #
                "immediate": dict(instruction)["immediate"]
                if "immediate" in dict(instruction)
                else None,
            }

            if instruction.opcode == "lw":
                state = [0, 1, 1, 1, 1, 0, 0]
            elif instruction.opcode == "sw":
                state = [-1, 1, -1, 0, 0, 1, 0]
            elif instruction.opcode == "beq":
                state = [-1, 0, -1, 0, 0, 0, 1]

        elif instruction.format == Format.JFORMAT:
            pass

        for key in control:
            control[key] = state.pop(0)
        self.output["control"] = control
        return self.output
