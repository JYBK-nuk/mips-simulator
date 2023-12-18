

import sys
import numpy as np
import string
instruction_now="add $6, $4, $5"
#####棄用 no use for now #
#下次要control signal
def parse_instruction(instruction_str):
    instruction_list= []
    commands=str(instruction_str).splitlines()
    #print(commands)
    for per_command in commands:
        opcode, operands = str(per_command).split(" ", 1)
        opcode = opcode.upper()
        operands = [operand.strip() for operand in operands.split(",")]
        #print(operands)
        if opcode == "ADD" or opcode == "SUB":
            rd, rs, rt = map(lambda x: int(x[1:]), operands)
            instruction_list.append({"opcode": opcode, "rs": rs, "rt": rt, "rd": rd}) 
        if opcode == "LW" or opcode == "SW":
            rt=int( operands[0][1:] ) #ex lw $2, 32($26)   rs:理論上是$26 constant:32 rt:2
            #print(rs)
            constant= operands[1].split("(")
            rs=int(constant[1][1:-1])
            constant= int(constant[0])
            #print(constant)
            #print(rt)
            instruction_list.append({"opcode": opcode, "rs": rs, "rt": rt,'constant':constant}) 
        
    return instruction_list
################################
reg = np.zeros(32, dtype=np.int32)
reg[0] = 0
for i in range(1, 32):
    reg[i] = 1
def IterateReg():
    for i in range(32):
        print('$'+str(i)+":"+str(reg[i]))
####################################
memoryview = np.ones(32, dtype=np.int32)
def IterateMem():
    for i in range(32):
        print('M'+str(i)+":"+str(memoryview[i]))
        
#IterateReg()
#IterateMem()


class IFStage:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0#第一條指令
    
    def fetch_instruction(self):
        print(self.instructions)
        instruction = self.instructions[self.pc]
        self.pc += 1#下一條指令 BUT 應該+=4 FOR理論
        return instruction


class IDStage:
    def __init__(self, registers):
        self.registers = registers
    
    def read_registers(self, instruction):
        rs_value = self.registers[instruction["rs"]]#到時候用map  ex rs:5=> $5
        rt_value = self.registers[instruction["rt"]]
        return rs_value, rt_value
    
    def write_register(self, instruction, alu_result):
        if "rd" in instruction:
            self.registers[instruction["rd"]] = alu_result

class EXStage:
    def __init__(self):
        pass
    
    def alu_operation(self, instruction, rs_value, rt_value):
        if instruction["opcode"] == "ADD":
            alu_result = rs_value + rt_value
        elif instruction["opcode"] == "SUB":
            alu_result = rs_value - rt_value
        elif instruction["opcode"] == "LW" or instruction["opcode"] == "SW":
            if(reg[rs_value]%4!=0 or int(instruction["constant"])%4!=0):
                print('錯誤 在mips如果沒對齊word need use ulw 指令')
            alu_result = reg[rs_value] + int(instruction["constant"]/4)
        return alu_result


class MEMStage:
    def __init__(self, memory):
        self.memory = memory
    
    def memory_operation(self, instruction, alu_result):
        if instruction["opcode"] == "ADD" or instruction["opcode"] == "SUB":
            return alu_result#回傳原本ㄉ當作沒做事
        if instruction["opcode"] == "LW":
            return memoryview[alu_result]#回傳LOAD的MEMORY位置的值
        if instruction["opcode"] == "SW":
            memoryview[alu_result] = reg[instruction["rt"]]
        


class WBStage:
    def __init__(self, registers):
        self.registers = registers
    
    def write_result(self, instruction, alu_result):
        if instruction["opcode"] == "ADD" or instruction["opcode"] == "SUB":
            self.registers[instruction["rd"]] = alu_result
        if instruction["opcode"] == "LW":
            self.registers[instruction["rt"]] = alu_result
        if instruction["opcode"] == "SW":
            print('sw Regwrite=0 memToreg dont care')
            return 

class IF_ID:
    #不知道他要傳啥MAYBE PC AND INSTRUCTION
    def __init__(self,pc,intruction_per):
        self.pc=pc
        self.intruction_per=intruction_per
    def show(self):
        print('這裡是pipe-pc:'+str(self.pc))
        print('這裡是pipe-ins:'+str(self.intruction_per))

class DataPath:
    def __init__(self, instructions, registers, memory):
        self.instructions = instructions
        self.registers = registers
        self.memory = memory
        self.pc = 0
    
    def run(self):
        if_stage=IFStage(self.instructions)
        if_divide_id=IF_ID(if_stage.pc,if_stage.instructions[if_stage.pc])
        id_stage = IDStage(self.registers)
        ex_stage = EXStage()
        mem_stage = MEMStage(self.memory)
        wb_stage = WBStage(self.registers)
        while if_stage.pc<len(self.instructions):
            instruction_signal=if_stage.fetch_instruction()#拿到現在的指令 從list[pc]拿
            print("IF階段:"+str(instruction_signal))  
            if_divide_id.pc=if_stage.pc
            if_divide_id.intruction_per=instruction_signal
            if_divide_id.show()
            #####################
            reg_signal=id_stage.read_registers(instruction_signal)#拿到rs rt
            print("ID階段:"+str(reg_signal))
            alu_signal=ex_stage.alu_operation(instruction_signal,reg_signal[0],reg_signal[1])#拿到rs rt做運算
            print("EX階段:"+str(alu_signal))
            mem_signal=mem_stage.memory_operation(instruction_signal,alu_signal)
            wb_signal=wb_stage.write_result(instruction_signal,mem_signal)

file = open("command.txt", "r")
content = file.read()
#print(content)
parsed_instruction = (parse_instruction(content))
#print(parsed_instruction) 

#kind of mainㄅ
data_path = DataPath(parsed_instruction, reg, memoryview)
data_path.run()

IterateReg()
IterateMem()
#####棄用