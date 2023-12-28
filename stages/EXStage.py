from Instructions import Format, Instruction
from stages.ControlUnit import BaseStage, ControlUnit


class EXStage(BaseStage):
    def __init__(self, ParentUnit: ControlUnit):
        super().__init__(ParentUnit)

    def execute(
        self,
        pc: int,
        instruction: Instruction,
        immediate: int,
        control: dict,
        ReadData1: int,
        ReadData2: int,
        LastCycleMEM_WB:dict[str, dict],
    ):
        global ForwardA
        global ForwardB
        
        
        super().execute()
        alu_op = control["ALUOp"]
        inputReadData2 = ReadData2  # if MemWrite == 1 MEM STAGE 會用到
        
        #forwarding unit會用到的 #預設都是00 如果EX HAZARD =>10 MEM =>01
        ForwardA = '00'
        ForwardB = '00'
        if self._ControlUnit.pipeline==1:
            self.forwardingUnit(LastCycleMEM_WB) # forwardUNIT判斷需不需要 FORWARDING
            
            #print(str(ForwardA)+'和b'+str(ForwardB)) #FOR TEST
            if ForwardA == '00':
                ReadData1 = ReadData1
            elif ForwardA == '10':
                ReadData1 = self._ControlUnit.pipelineRegister["EX/MEM"]["ALUResult"]
            elif ForwardA == '01':
                #ReadData1 = self._ControlUnit.pipelineRegister["MEM/WB"]["ALUResult"]
                if LastCycleMEM_WB['nop']!=True:
                    if LastCycleMEM_WB['control']['MemToReg'] == 1:
                        ReadData2 = LastCycleMEM_WB["ReadData"]
                else:
                    ReadData2 = LastCycleMEM_WB["ALUResult"]
                
            if ForwardB == '00':
                ReadData2 = ReadData2
            elif ForwardB == '10':
                ReadData2 = self._ControlUnit.pipelineRegister["EX/MEM"]["ALUResult"]
            elif ForwardB == '01':
                #ReadData2 = self._ControlUnit.pipelineRegister["MEM/WB"]["ALUResult"]
                print(LastCycleMEM_WB)
                if LastCycleMEM_WB['nop']!=True:
                    if LastCycleMEM_WB['control']['MemToReg'] == 1:
                        ReadData1 = LastCycleMEM_WB["ReadData"]
                else:
                    ReadData2 = LastCycleMEM_WB["ALUResult"]
            
        
        if control["ALUSrc"] == 1:
            # lw sw , ReadData2要變成讀取immediate
            # 例如 lw 是 BaseAddress + Offset 的部分 (ReadData1 + immediate)
            # ex : lw $t0, 4($t1) 4就是immediate
            # (所以要記得在MEMStage要讀取ReadData2要除以4才會是在記憶體中的位置)
            # ps : 我們的記憶體是直接以4byte為單位 np.int32
            ReadData2 = immediate

        
        # 這裡要算出來的是ALUResult
        if alu_op == "add":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": self.ALU("add", ReadData1, ReadData2),
                "AddrResult": -1,#用不到設-1
            }
        elif alu_op == "sub" and control['RegDst'] == 1:
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": self.ALU("sub", ReadData1, ReadData2),
                "AddrResult": -1, #邏輯算要byte address 的運算 (pc*4 + immediate*4)/4
            }
        elif alu_op == "sub":
            self.output = {
                "PC": pc,
                "instruction": instruction,
                "nop": self.nop,
                "ALUResult": self.ALU("sub", ReadData1, ReadData2),
                "AddrResult": self.ALU("add", pc, int(immediate)), #邏輯算要byte address 的運算 (pc*4 + immediate*4)/4
            }
        
        #Branch的設值在mem 這裡純比較和算pc add

        if control["RegDst"] == 1:
            self.output["RegDstValue"] = instruction.dict_['rd']
        else:
            self.output["RegDstValue"] = instruction.dict_['rt']

        self.output["ReadData2"] = inputReadData2  # 這個是要傳給MEMStage的

        # 該stage 要傳給下一個stage的 control 值
        self.output["control"] = {}
        for c in ["MemToReg", "RegWrite","Branch", "MemRead", "MemWrite"]:
            self.output["control"][c] = control[c]
        return self.output

    def ALU(self, ALUop: str, data1: int, data2: int):
        if ALUop == "add":  # 00
            value = data1 + data2
        elif ALUop == "sub":  # 01
            value = data1 - data2
        return value
    
    
    def forwardingUnit(self,Last): #!!!!這邊是數學運算的DATA HAZARD (LW/SW)的要做在ID
        global ForwardA
        global ForwardB
        #如果ex hazard 就return 否則判斷mem hazard 不然就沒事
        EX_MEM_pipe=self._ControlUnit.pipelineRegister["EX/MEM"]
        MEM_WB_pipe=Last
        ID_EX_pipe=self._ControlUnit.pipelineRegister["ID/EX"]
        print(str(EX_MEM_pipe['PC'])+' mem/wb的pc '+str(MEM_WB_pipe['PC']))
        #避免拿nop的內容來比會有問題
        if ID_EX_pipe['nop']==True or ID_EX_pipe['control']['Branch'] == 1:
            print('會去溜')
            return
        
        #mem hazard    先MEM再EX這樣就算同時MEM和EX Hazard也會取到ex的
        if MEM_WB_pipe['nop'] != True:
            
            # if MEM_WB_pipe['instruction'].format != Format.RFORMAT:
            #     print('回去溜')
            #     return#要保證是前指令與前前指令都是r=format
            
            if MEM_WB_pipe['control']["RegWrite"] == 1 and MEM_WB_pipe["RegDstValue"]  != '$0':
                #print('data-hazard!!!!!!!!!!!!!!!!!!!!!!!!')
                if dict(ID_EX_pipe['instruction'])["rs"] == MEM_WB_pipe["RegDstValue"]:
                    print('MEM_R-FORMAT DATA-HAZARD--RS')
                    ForwardA='01'
                if dict(ID_EX_pipe['instruction'])["rt"] == MEM_WB_pipe["RegDstValue"]:
                    print('MEM_R-FORMAT DATA-HAZARD--RT')
                    ForwardB='01'
                    
        if EX_MEM_pipe['nop'] != True:
            
            
            
            if EX_MEM_pipe['control']["RegWrite"] == 1 and EX_MEM_pipe["RegDstValue"]  != '$0':
                if dict(ID_EX_pipe['instruction'])["rs"] == EX_MEM_pipe["RegDstValue"]:
                    print('EX_R-FORMAT DATA-HAZARD--RS')
                    ForwardA='10'
                if dict(ID_EX_pipe['instruction'])["rt"] == EX_MEM_pipe["RegDstValue"]:
                    print('EX_R-FORMAT DATA-HAZARD--RT')
                    ForwardB='10'
        else:
            pass