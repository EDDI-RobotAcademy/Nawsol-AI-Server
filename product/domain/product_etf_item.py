from datetime import datetime

class ProductEtfItem:
    def __init__(self, fltRt: float, nav: float, mkp: int, hipr: int, lopr: int,
                 trqu: int, trPrc: int, mrktTotAmt: int, nPptTotAmt: int, stLstgCnt: int,
                 bssIdxIdxNm: str, bssIdxClpr: float, basDt: datetime, clpr: int, vs: int):
        self.fltRt = fltRt
        self.nav = nav
        self.mkp = mkp
        self.hipr = hipr
        self.lopr = lopr
        self.trqu = trqu
        self.trPrc = trPrc
        self.mrktTotAmt = mrktTotAmt
        self.nPptTotAmt = nPptTotAmt
        self.stLstgCnt = stLstgCnt
        self.bssIdxIdxNm = bssIdxIdxNm
        self.bssIdxClpr = bssIdxClpr
        self.basDt = basDt
        self.clpr = clpr
        self.vs = vs