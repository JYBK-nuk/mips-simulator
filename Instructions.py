from enum import Enum


class Format(Enum):
    IFORMAT = 0
    RFORMAT = 1
    JFORMAT = 2

    @staticmethod
    def getField(format: int):
        FormatField = [
            ["rs", "rt", "immediate"],
            ["rs", "rt", "rd", "shamt", "funct"],
            ["address"],
        ]
        return FormatField[format]


def parse_sw_lw(args: list[str]):
    # ["$2","32($26)"] -> {"rt": $2, "immediate": 32, "rs": $26}
    rt = args[0]
    constant = args[1].split("(")
    rs = constant[1][:-1]
    immediate = int(constant[0])
    return {"rt": rt, "immediate": immediate, "rs": rs}


FormatTable = {
    # 放置順序與指令args順序不同
    "add": [Format.RFORMAT, [1, 2, 0]],  # 2 = rd, 0 = rs, 1 = rt
    "sub": [Format.RFORMAT, [1, 2, 0]],  # 2 = rd, 0 = rs, 1 = rt
    "sw": [Format.IFORMAT, parse_sw_lw],
    "lw": [Format.IFORMAT, parse_sw_lw],
}


class Instruction:
    opcode: str
    format: Format
    dict_: dict[str, str]
    

    def __init__(self, opcode: str, args: list[str] or dict[str, str]):
        self.opcode = opcode
        self.format: Format = FormatTable[opcode][0]

        # args check
        if isinstance(args, (list, dict)):
            self.args = args
        else:
            raise TypeError("args must be list or dict")

        fields = Format.getField(self.format.value)
        used_fields = FormatTable[opcode][1]
        # 兩種情況: 1. 順序問題 2. lw sw 需要解析()
        if isinstance(used_fields, list):
            self.dict_ = {fields[i]: args[used_fields[i]] for i in range(len(used_fields))}
        elif callable(used_fields):
            self.dict_ = used_fields(args)

    def __iter__(self):
        yield from self.dict_.items()

    def __repr__(self) -> str:
        # print can print all args
        return self.opcode + ":" + str(self.dict_)
