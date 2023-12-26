Reg:
array([0, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
│      1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
Mem:
array([1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
│      1, 1, 1, 1, 1, 1, 1, 1, 1, 1])



array([0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
│      1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
Mem:
array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
│      1, 1, 1, 1, 1, 1, 1, 1, 1, 1])


# if dict(self.pipelineRegister["IF/ID"]['instruction'])=='Branch':
        #     if self.pipelineRegister["EX/MEM"]["RegWrite"] == 1 and self.pipelineRegister["EX/MEM"]["RegDstValue"]  != '$0':
        #         if dict(self.pipelineRegister["IF/ID"]['instruction'])["rs"] == self.pipelineRegister["EX/MEM"]["RegDstValue"]:
        #             self.pipelineRegister["IF/ID"]['nop']=True
        #             log(self.pipelineRegister["EX/MEM"]["RegDstValue"])
        
