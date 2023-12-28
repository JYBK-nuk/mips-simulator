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
        LastCycleMEM_WB:dict[str, dict],
    ):
        global ForwardA
        global ForwardB
        
        super().execute()
        
        ForwardA = '00'
        ForwardB = '00'
        
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
        self.output["Compare_ID"] = 0
        
        # branch move to id
        #這邊要先測DATA HAZARD
        Do_Compare=True
        if self._ControlUnit.pipeline:
            Do_Compare=self.hazardDetectionUnit()
            if instruction.opcode == "beq":
                self.forwardingUnit(LastCycleMEM_WB)
            if self.output['ReadData1'] == '00':
                self.output['ReadData1'] = self.output['ReadData1']
            elif ForwardA == '10':
                self.output['ReadData1'] = self._ControlUnit.pipelineRegister["EX/MEM"]["ALUResult"]
            elif ForwardA == '01':
                #ReadData1 = self._ControlUnit.pipelineRegister["MEM/WB"]["ALUResult"]
                if LastCycleMEM_WB['control']['MemRead'] == 1:
                    self.output['ReadData1'] = LastCycleMEM_WB["ReadData"]
                else:
                    self.output['ReadData1'] = LastCycleMEM_WB["ALUResult"]
                
            if ForwardB == '00':
                self.output['ReadData2'] = self.output['ReadData2']
            elif ForwardB == '10':
                self.output['ReadData2'] = self._ControlUnit.pipelineRegister["EX/MEM"]["ALUResult"]
            elif ForwardB == '01':
                #ReadData2 = self._ControlUnit.pipelineRegister["MEM/WB"]["ALUResult"]
                if LastCycleMEM_WB['control']['MemRead'] == 1:
                    self.output['ReadData2'] = LastCycleMEM_WB["ReadData"]
                else:
                    self.output['ReadData2'] = LastCycleMEM_WB["ALUResult"]
            
        if self.output["control"]["Branch"] == 1 and Do_Compare:
            compare = self.output["ReadData1"] - self.output["ReadData2"]
            AddrADD = self.output["PC"] + int(self.output["immediate"])
            if compare != 0:
                self.output["Compare_ID"] = 0
                self.output["AddrADD_ID"] = AddrADD
            else:
                self.output["Compare_ID"] = 0
                self.output["AddrADD_ID"] = AddrADD
                self.output["PC"] = AddrADD
                #需要將下面兩條暫存 因為現在是先ID 才 IF 現在改值IF做的時後又蓋掉=NO USE
                self._ControlUnit.pipelineRegister["IF/ID"]["nop"] = True
                self._ControlUnit.stages[0].pc = AddrADD
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   上個CYCLE
                #                                           BEQ  LW   LW   0     0
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   下個CYCLE
                #                                           ADD  BEQ  LW   LW    0
                # need to NOP 一次 在PIPELINE的部分  EX STEP IF   ID   EX   MEM   WB   下個CYCLE
                #                                           SW  ADD(NOP)  BEQ   LW    LW
        #要檢查branch data hazard lw只少要在前前前 所以 ex跟mem的MemToReg都要check
        #要檢查branch data hazard alu_op只少要在前前 所以 ex的MemToReg要check
        #rs rt都要個別檢查 且 ex優先於mem的hazard
        # HOW TO SELECT 是RS 還是 RT FORWARD
        # if self._ControlUnit.StallFlag:
        #     self.output["ReadData1"]=self._ControlUnit.pipelineRegister["EX/MEM"]['ALUResult'] #ex forward的內容
        
        #self.hazardDetectionUnit()
        return self.output
    
    def hazardDetectionUnit(self):# if detect stall
        if self._ControlUnit.pipelineRegister['ID/EX']['nop']==True:
            return
        IF_ID_TEMP=self._ControlUnit.pipelineRegister['IF/ID']
        ID_EX_TEMP=self._ControlUnit.pipelineRegister['ID/EX']
        EX_MEM_TEMP=self._ControlUnit.pipelineRegister['EX/MEM']
        MEM_WB_TEMP=self._ControlUnit.pipelineRegister['MEM/WB']
        if ID_EX_TEMP['control']['MemRead'] == 1:
            if dict(ID_EX_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rs"]:
                #do stall and so that can 正常運作
                self._ControlUnit.IF_ID_Write = 1 #IF不更新
                self._ControlUnit.PC_Write_Next_Cycle = 1
                print('我lw黑色ㄌ哦')
                pass
            if dict(ID_EX_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rt"]:
                self._ControlUnit.IF_ID_Write = 1 #IF不更新
                self._ControlUnit.PC_Write_Next_Cycle = 1
                print('我lw黑色ㄌ哦')
                pass
            
        if IF_ID_TEMP['nop']!=True and EX_MEM_TEMP['nop'] != True:
            if IF_ID_TEMP['instruction'].opcode=='beq':
                print("---------------beq check data hazard------------------")
                #R-FORMAT要至少前前條 所以在前條偵測到的話就要stall 然後才能FORWARD
                if EX_MEM_TEMP['control']["RegWrite"] == 1 and EX_MEM_TEMP["RegDstValue"]  != '$0':
                    if dict(IF_ID_TEMP['instruction'])["rs"] == EX_MEM_TEMP["RegDstValue"]:
                        self._ControlUnit.IF_ID_Write = 1 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 1
                        print("Branch data hazard偵測到R-FORMAT在前一行 rs")
                        return False #return false 代表這次不比較
                    if dict(IF_ID_TEMP['instruction'])["rt"] == EX_MEM_TEMP["RegDstValue"]:
                        self._ControlUnit.IF_ID_Write = 1 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 1
                        print("Branch data hazard偵測到R-FORMAT在前一行 rt")
                        return False #return false 代表這次不比較
                #lw有兩種情況 如果是前前指令(看MEM/WB) 要停一次 如果是前指令 要停兩次()
                if MEM_WB_TEMP['control']['MemRead'] == 1:
                    #前 是要forward過來的 
                    if dict(MEM_WB_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rs"]:
                        #do stall and so that can 正常運作
                        self._ControlUnit.IF_ID_Write = 1 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 1
                        print('Branch data hazard偵測到LW在前前一行 rs')
                        pass
                    if dict(MEM_WB_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rt"]:
                        self._ControlUnit.IF_ID_Write = 1 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 1
                        print('Branch data hazard偵測到LW在前前一行 rt')
                        pass
                #停2次
                if EX_MEM_TEMP['control']['MemRead'] == 1:
                    #前 是要forward過來的 
                    if dict(EX_MEM_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rs"]:
                        #do stall and so that can 正常運作
                        self._ControlUnit.IF_ID_Write = 2 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 2
                        print('Branch data hazard偵測到LW在前一行 rs')
                        pass
                    if dict(EX_MEM_TEMP['instruction'])["rt"] == dict(IF_ID_TEMP['instruction'])["rt"]:
                        self._ControlUnit.IF_ID_Write = 2 #IF不更新
                        self._ControlUnit.PC_Write_Next_Cycle = 2
                        print('Branch data hazard偵測到LW在前一行 rt')
                        pass
            else:
                return
    #要在ID FORWARD 
    def forwardingUnit(self,Last): #因為branch data hazard要在id 解決 so i must do here
        #運作跟ex的那套一模一樣
        global ForwardA
        global ForwardB
        #如果ex hazard 就return 否則判斷mem hazard 不然就沒事
        EX_MEM_pipe=self._ControlUnit.pipelineRegister["EX/MEM"]
        MEM_WB_pipe=Last
        ID_EX_pipe=self.output
        print(str(EX_MEM_pipe['PC'])+' mem/wb的pc '+str(MEM_WB_pipe['PC']))
        #避免拿nop的內容來比會有問題
        if ID_EX_pipe['nop']==True:
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
                    print('BRANCH MEM_DATA HAZARD--RS')
                    ForwardA='01'
                if dict(ID_EX_pipe['instruction'])["rt"] == MEM_WB_pipe["RegDstValue"]:
                    print('BRANCH MEM_DATA HAZARD--RT')
                    ForwardB='01'
                    
        if EX_MEM_pipe['nop'] != True:
            
            
            
            if EX_MEM_pipe['control']["RegWrite"] == 1 and EX_MEM_pipe["RegDstValue"]  != '$0':
                if dict(ID_EX_pipe['instruction'])["rs"] == EX_MEM_pipe["RegDstValue"]:
                    print('BRANCH EX_DATA HAZARD---RS')
                    ForwardA='10'
                if dict(ID_EX_pipe['instruction'])["rt"] == EX_MEM_pipe["RegDstValue"]:
                    print('BRANCH EX_DATA HAZARD--RT')
                    ForwardB='10'
        else:
            pass
        
        
