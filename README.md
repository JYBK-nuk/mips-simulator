# mips-simulator

## Requirement
- Python 3.10.7
```
numpy==1.24.2
colorama==0.4.6
rich==13.7.0
```

## Run
- Input : `memory.txt`
```sh
python main.py > result.txt
```

## 檔案結構
- MemAndReg.py：用於模擬記憶體和暫存器。它包含了讀取和設置暫存器值、讀取和設置記憶體值等相關的方法

- Instructions.py：指令解析的功能。它包含了指令的格式、解析指令的方法、指令字典等相關的內容

- ControlUnit.py：控制程式的執行流程。它包含了pipeline的相關邏輯，以及各個階段的初始化、執行和控制

- IFStage.py、IDStage.py、EXStage.py、MEMStage.py、WBStage.py：這些模塊分別定義了指令執行的不同階段
## Output格式
都是此STAGE執行完之後所產出的相關資訊 像是ID就是ID執行完後的資訊 而不是ID執行前  
例子  
- IF  
```py
{  
   'PC': 5,  
   'instruction': add:{'rd': '$4', 'rs': '$1', 'rt': '$4'},  
   'nop': False  
}
```
- ID (因為Control在電路圖是ID STAGE就產生)    **-1就是DON'T CARE!!**  
```py
{  
   'PC': 4,  
   'instruction': beq:{'rs': '$4', 'rt': '$1', 'immediate': '-2'},  
   'nop': False,  
   'ReadData1': 1,  
   'ReadData2': 2,  
   'immediate': '-2',  
   'control': {  
      'RegDst': -1,  
      'ALUSrc': 0,  
      'MemToReg': -1,  
      'RegWrite': 0,  
      'MemRead': 0,  
      'MemWrite': 0,  
      'Branch': 1,  
      'ALUOp': 'sub'  
   },  
   'Compare_ID': 0  
}
```
- EX MEM WB一樣  
