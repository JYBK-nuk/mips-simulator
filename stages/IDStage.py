from typing import Dict, Union
from Instructions import Instruction, Format
from stages.ControlUnit import BaseStage, ControlUnit


class IDStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def excute(
        self,
        pc,
        instruction: Instruction,
        RegWrite: Union[int, None] = None,
        WriteData: Union[int, None] = None,
        WriteRegister: Union[str, None] = None,
    ):
        super().excute()

        control: Dict[str, int] = {
            "RegDst": -1,
            "ALUSrc": -1,
            "MemToReg": -1,
            "RegWrite": -1,
            "MemRead": -1,
            "MemWrite": -1,
            "Branch": -1,
            "ALUOp": "",
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
            if instruction.opcode == "add":
                state.append("add")  # 00
            elif instruction.opcode == "sub":
                state.append("sub")  # 01

        elif instruction.format == Format.IFORMAT:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ReadData1": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rs"]),
                "ReadData2": self._ControlUnit._MemAndReg.getReg(dict(instruction)["rt"]),
            }

            if instruction.opcode == "lw":
                state = [0, 1, 1, 1, 1, 0, 0, "add"]  # 00
            elif instruction.opcode == "sw":
                state = [-1, 1, -1, 0, 0, 1, 0, "add"]  # 00
            elif instruction.opcode == "beq":
                state = [-1, 0, -1, 0, 0, 0, 1, "sub"]  # 01 因為要用ALU 相減==0

        elif instruction.format == Format.JFORMAT:
            pass

        self.output["immediate"] = (
            dict(instruction)["immediate"] if "immediate" in dict(instruction) else None
        )

        for key in control:
            control[key] = state.pop(0)
        self.output["control"] = control
        return self.output

    def EvenNop(
        self,
        pc,
        instruction: Instruction,
        RegWrite: Union[int, None] = None,
        WriteData: Union[int, None] = None,
        WriteRegister: Union[str, None] = None,
    ):
        self.WriteBack(RegWrite, WriteData, WriteRegister)

    def WriteBack(self, RegWrite: int, WriteData: int, WriteRegister: str):
        if RegWrite != 1:
            return
        if WriteData is not None and WriteRegister is not None:
            self._ControlUnit._MemAndReg.setReg(WriteRegister, WriteData)
