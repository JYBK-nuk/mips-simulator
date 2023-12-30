from abc import ABC
from rich.pretty import pprint
from Instructions import Instruction
from MemAndReg import MemAndReg
from colorama import Fore, Back, Style
from collections import defaultdict


def log(string, color=Fore.WHITE):
    print(color + string + Style.RESET_ALL)


class ControlUnit:
    _MemAndReg: 'MemAndReg'
    instructions: list[Instruction]

    cycle: int = 0
    endInstruction = False
    RegWrite = None
    writeReg = None
    writeData = None
    StallFlag=False
    ControlHazardFlag=False #control hazard must occur on ID STAGE
    StallCount=0 #stall 幾次
    PC_Write = 0 #如果1就是 STALL 不更新pc
    PC_Write_Next_Cycle = 0 #因為backward 造成的
    IF_ID_Write = 0
    
    
    
    pipelineRegister: dict[str, dict] = {
        "IF/ID": defaultdict(lambda: None),
        "ID/EX": defaultdict(lambda: None),
        "EX/MEM": defaultdict(lambda: None),
        "MEM/WB": defaultdict(lambda: None),
    }
    pipelineRegister_temp: dict[str, dict] = { #這只是拿來暫存OUTPUT 假設IF完 OUTPUT會跑到IF/ID，但想讓輸出是IF的結果，所以用這個暫存
        "IF": defaultdict(lambda: None),
        "ID": defaultdict(lambda: None),
        "EX": defaultdict(lambda: None),
        "MEM": defaultdict(lambda: None),
        "WB": defaultdict(lambda: None),
        "MEM/WB-TEMP": defaultdict(lambda: None),
        "CONTROL_HAZARD": defaultdict(lambda: None),
    }

    stages: list['BaseStage']

    def __init__(self, MemAndReg: 'MemAndReg', instructions: list[Instruction], pipeline: bool):
        self._MemAndReg = MemAndReg
        self.instructions = instructions
        self.pipeline = pipeline

        self.pipelineRegister["IF/ID"]["nop"] = True
        self.pipelineRegister["ID/EX"]["nop"] = True
        self.pipelineRegister["EX/MEM"]["nop"] = True
        self.pipelineRegister["MEM/WB"]["nop"] = True
    #not very understand
    def SaveAndGetpipelineRegister(self, stage: str, data: dict):
        #pprint(data, expand_all=True)
        temp = self.pipelineRegister[stage]
        self.pipelineRegister[stage] = data
        return temp
    def print_fun(self,data: dict):
        pprint(data, expand_all=True)
    def print_dict(self,data: str):
        pass
    #啟動整個流程
    def start(self):
        if self.pipeline:
            while True:
                if self.runpipeline() is False:
                    break
        else:
            while True:
                if self.run() is False:
                    break
                    
    def runpipeline(self):
        #self.StallFlag=False
        log(F"\n↓ Cycle {(self.cycle) +1} ↓", Back.BLUE + Fore.WHITE)

        
        #更新狀態 THIS IS FOR I-FORMAT DATAHAZARD
        self.PC_Write=self.PC_Write_Next_Cycle
        if self.PC_Write>=1:
            self.pipelineRegister["ID/EX"]['nop']=True
            self.PC_Write_Next_Cycle-=1
            self.IF_ID_Write-=1
        print("現在的PC_Write:"+str(self.PC_Write))
        print("現在的PC_Write_Next_Cycle:"+str(self.PC_Write_Next_Cycle))
        print("現在的IF_ID_Write:"+str(self.IF_ID_Write))
            
        # Stages
        #以下是WB
        #log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].RunWithNop(
            self.pipelineRegister["MEM/WB"]["nop"],
            self.pipelineRegister["MEM/WB"]["PC"],
            self.pipelineRegister["MEM/WB"]["instruction"],  # 暫時沒用到
            self.pipelineRegister["MEM/WB"]["control"],  # ["MemToReg", "RegWrite"]
            self.pipelineRegister["MEM/WB"]["ReadData"],  # MEM STAGE Read Data
            self.pipelineRegister["MEM/WB"]["ALUResult"],  # from EX STAGE ALUresult
            self.pipelineRegister["MEM/WB"]["RegDstValue"],  # from EX STAGE RegDst 選的
        )
        
        #pprint(WBOut, expand_all=True)

        self._MemAndReg.print()
        self.pipelineRegister_temp['WB']=WBOut
        ###################以下是MEM
    
        #log("\nMEMStage", Back.WHITE + Fore.BLACK)
        self.pipelineRegister_temp['MEM/WB-TEMP']=self.pipelineRegister['MEM/WB']
        MEMOut = self.SaveAndGetpipelineRegister(
            "MEM/WB",
            self.stages[3].RunWithNop(
                self.pipelineRegister["EX/MEM"]["nop"],
                self.pipelineRegister["EX/MEM"]["PC"],
                self.pipelineRegister["EX/MEM"]["instruction"],  # 暫時沒用到
                self.pipelineRegister["EX/MEM"]["control"],  # ["MemToReg", "RegWrite", "MemRead", "MemWrite"]
                self.pipelineRegister["EX/MEM"]["ReadData2"],  # 因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
                # pure passthrough
                self.pipelineRegister["EX/MEM"]["ALUResult"],
                self.pipelineRegister["EX/MEM"]["AddrResult"],  # 計算pc加offset的結果
                self.pipelineRegister["EX/MEM"]["RegDstValue"],
            ),
        )
        self.pipelineRegister_temp['MEM']=self.pipelineRegister['MEM/WB']
        ###################以下是EX
    
        EXOut = self.SaveAndGetpipelineRegister(
            "EX/MEM",
            self.stages[2].RunWithNop(
                self.pipelineRegister["ID/EX"]["nop"],
                self.pipelineRegister["ID/EX"]["PC"],
                self.pipelineRegister["ID/EX"]["instruction"],  # 暫時沒用到
                self.pipelineRegister["ID/EX"]["immediate"],
                self.pipelineRegister["ID/EX"]["control"],  # All control state
                self.pipelineRegister["ID/EX"]["ReadData1"],
                self.pipelineRegister["ID/EX"]["ReadData2"],
                MEMOut
            ),
        )
        self.pipelineRegister_temp['EX']=self.pipelineRegister['EX/MEM']
        if self.pipelineRegister["EX/MEM"]['nop']!=True:
            pass
            #pprint(dict(self.pipelineRegister["EX/MEM"]['instruction'])['rs'])
            #pprint(self.pipelineRegister["EX/MEM"]['instruction'].format)
        ###################以下是ID
        
        #這是判斷branch的data hazard(算術運算) 還沒有寫成general的 而且還沒有mem hazard的 可能可以移到IDStage
        #因為是判斷data hazard的所以是在計算發生前確認
        #這底下的Branch hazard 感覺可以移到IDStage
        
        
        
        
        IDOut = self.SaveAndGetpipelineRegister(
            "ID/EX",
            self.stages[1].RunWithNop(
                self.pipelineRegister["IF/ID"]["nop"], 
                self.pipelineRegister["IF/ID"]["PC"], 
                self.pipelineRegister["IF/ID"]["instruction"],
                MEMOut,
                EXOut
            ),    
        )
        
        
        if self.pipelineRegister["ID/EX"]["Compare_ID"] == 1:#這是control hazard
            self.ControlHazardFlag=True
        else:
            self.ControlHazardFlag=False
            
        self.pipelineRegister_temp['ID']=self.pipelineRegister['ID/EX']
        ##############################以下是IF
        
        #因為stall要防止更新pc 所以要暫存
        print('sdsadsadsadasd\n')
        print(self.stages[0].pc)
        IFOut = self.SaveAndGetpipelineRegister(
            "IF/ID", self.stages[0].RunWithNop(self.stages[0].nop)
        )
        
        if self.PC_Write_Next_Cycle:
            self.stages[0].pc=IFOut['PC']
            print('STALL 中第IF不更新')
            
        self.pipelineRegister_temp['IF']=self.pipelineRegister['IF/ID']
        # Stages END
        
        
        #print content
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        self.print_fun(self.pipelineRegister_temp['IF'])
        log("\nIDStage", Back.WHITE + Fore.BLACK)
        self.print_fun(self.pipelineRegister_temp['ID'])
        log("\nEXStage", Back.WHITE + Fore.BLACK)
        self.print_fun(self.pipelineRegister_temp['EX'])
        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        self.print_fun(self.pipelineRegister_temp['MEM'])
        log("\nWBStage", Back.WHITE + Fore.BLACK)
        self.print_fun(self.pipelineRegister_temp['WB'])
    
        log("\n↑ End Cycle", Back.BLUE + Fore.WHITE)
        # 終止條件
        
        #後狀態更新
        if self.IF_ID_Write >=1: #I-FORMAT HAZARD
            self.pipelineRegister["IF/ID"]=IFOut
        
        
        if self.ControlHazardFlag:#如果control hazard 首先是設置下次跳轉的pc 然後IF/ID nop 但記得只會浪費一個cycle
            #print(str(self.pipelineRegister["ID/EX"]))
            self.stages[0].pc=self.pipelineRegister["ID/EX"]["PC"]
            self.pipelineRegister["IF/ID"]["nop"] = True
            self.ControlHazardFlag=False
            
            
        for stage in self.pipelineRegister.values():
            if stage["nop"] is False:
                break
        else:
            return False

        self.cycle += 1

        # pprint(self.pipelineRegister, expand_all=True)

    def run(self):
        log(F"\n↓ Loop {(self.cycle//5)+1} ↓", Back.BLUE + Fore.WHITE)

        # Stages
        log("\nIFStage", Back.WHITE + Fore.BLACK)
        IFOut = self.stages[0].RunWithNop(self.stages[0].pc >= len(self.instructions))
        pprint(IFOut, expand_all=True)

        log("\nIDStage", Back.WHITE + Fore.BLACK)
        IDOut = self.stages[1].RunWithNop(
            self.stages[0].nop,
            IFOut["PC"],
            IFOut["instruction"],
            -1,
            -1,
        )
        pprint(IDOut, expand_all=True)

        log("\nEXStage", Back.WHITE + Fore.BLACK)
        EXOut = self.stages[2].RunWithNop(
            self.stages[1].nop,
            IDOut["PC"],
            IDOut["instruction"],
            IDOut["immediate"],
            IDOut["control"],
            IDOut["ReadData1"],
            IDOut["ReadData2"],
            -1,
        )
        pprint(EXOut, expand_all=True)

        log("\nMEMStage", Back.WHITE + Fore.BLACK)
        MEMOut = self.stages[3].RunWithNop(
            self.stages[2].nop,
            EXOut["PC"],
            EXOut["instruction"],  # 暫時沒用到
            EXOut["control"],  # ["MemToReg", "RegWrite", "MemRead", "MemWrite"]
            EXOut["ReadData2"],  # 因為電路圖 有抓ReadData2 aka rt拿來用 所以看要在ex補
            EXOut["ALUResult"],
            EXOut["AddrResult"],  # 計算pc加offset的結果
            EXOut["RegDstValue"],
        )
        pprint(MEMOut, expand_all=True)

        log("\nWBStage", Back.WHITE + Fore.BLACK)
        WBOut = self.stages[4].RunWithNop(
            self.stages[3].nop,
            MEMOut["PC"],
            MEMOut["instruction"],
            MEMOut["control"],
            MEMOut["ReadData"],
            MEMOut["ALUResult"],
            MEMOut["RegDstValue"],
        )
        if not self.stages[4].nop:
            self.RegWrite = WBOut["control"]["RegWrite"]
            self.writeReg = WBOut["WriteRegister"]
            self.writeData = WBOut["WriteData"]
        pprint(WBOut, expand_all=True)
        self._MemAndReg.print()

        log(F"\n↑ Cycles : {self.cycle} ↑", Back.CYAN + Fore.WHITE)

        # 終止條件
        if self.stages[0].pc >= len(self.instructions):
            return False


class BaseStage(ABC):
    _ControlUnit: 'ControlUnit'
    nop: bool = False
    output: dict = {}
    Instruction: Instruction

    def __init__(self, ControlUnit: 'ControlUnit'):
        self._ControlUnit = ControlUnit

    def RunWithNop(self, nop: bool, *args):
        #沒pipeline時 一個cycle只能跑一個stage so everytime +1
        if not self._ControlUnit.pipeline:
            self._ControlUnit.cycle += 1
        #op 繼續保留
        self.nop = nop
        self.EvenNop(*args)
        #如果是nop就 重設dict_ 然後設nop =true for stull
        if nop is True or nop is None:
            dict_ = defaultdict(lambda: None)
            dict_["nop"] = True
            # EX
            # {"nop": True, "PC": None, "instruction": None, "immediate": None, "control": None, "ReadData1": None, "ReadData2": None}
            return dict_
        return self.execute(*args)

    def EvenNop(self, *args):  # 就算是nop也要執行的
        pass

    def execute(self):  # 這個NOP = True的時候不會執行
        pass

    def showData(self):
        pprint(self.output, expand_all=True)
