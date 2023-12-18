from typing import Dict, Union
from Instructions import Instruction, Format
from stages.ControlUnit import BaseStage, ControlUnit


class IDStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def execute(
        self,
        pc,
        instruction: Instruction,
    ):
        super().execute()

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
                "ReadData1": self._ControlUnit._MemAndReg.getReg(
                    dict(instruction)["rs"]
                ),
                "ReadData2": self._ControlUnit._MemAndReg.getReg(
                    dict(instruction)["rt"]
                ),
                "rd": dict(instruction)["rd"] if "rd" in dict(instruction) else None,
                "shamt": dict(instruction)["shamt"]
                if "shamt" in dict(instruction)
                else None,
                "funct": dict(instruction)["funct"]
                if "funct" in dict(instruction)
                else None,
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
                "ReadData1": self._ControlUnit._MemAndReg.getReg(
                    dict(instruction)["rs"]
                ),
                "ReadData2": self._ControlUnit._MemAndReg.getReg(
                    dict(instruction)["rt"]
                ),
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

        # branch move to id
        if self.output["control"]["Branch"] == 1:
            compare = self.output["ReadData1"] - self.output["ReadData2"]
            AddrADD = self.output["PC"] + int(self.output["immediate"])
            if compare != 0:
                self.output["Compare_ID"] = 0
                self.output["AddrADD_ID"] = AddrADD
            else:
                self.output["Compare_ID"] = 1
                self.output["AddrADD_ID"] = AddrADD
                self.output["PC"] = AddrADD
                self._ControlUnit.pipelineRegister["IF/ID"]["nop"] = True
                self._ControlUnit.stages[0].pc = AddrADD
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   上個CYCLE
                #                                           BEQ  LW   LW   0     0
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   下個CYCLE
                #                                           ADD  BEQ  LW   LW    0
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   下個CYCLE
                #                                           SW  ADD(NOP)  BEQ   LW    LW

        if control["MemToReg"] == 1:
            if "rd" in dict(instruction).keys():  # dict(instruction)["rd"] != None:
                if (
                    dict(instruction)["rd"]
                    == self._ControlUnit.pipelineRegister["IF/ID"]["instruction"]["rs"]
                ):
                    self._ControlUnit.pipelineRegister["IF/ID"]["nop"] = True
                    self._ControlUnit.stages[0].pc = self.output["PC"] - 1
                elif (
                    dict(instruction)["rd"]
                    == self._ControlUnit.pipelineRegister["IF/ID"]["instruction"]["rt"]
                ):
                    self._ControlUnit.pipelineRegister["IF/ID"]["nop"] = True
                    self._ControlUnit.stages[0].pc = self.output["PC"] - 1
        return self.output
