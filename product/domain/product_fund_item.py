from datetime import datetime

class ProductFundItem:
    def __init__(self, basDt:datetime, srtnCd: str, fndNm:str, ctg:str, setpDt:datetime, fndTp:str, prdClsfCd:str, asoStdCd:str ):
        self.baseDt = basDt
        self.srtnCd = srtnCd
        self.fndNm = fndNm
        self.ctg = ctg
        self.setpDt = setpDt
        self.fndTp = fndTp
        self.prdClsfCd = prdClsfCd
        self.asoStdCd = asoStdCd