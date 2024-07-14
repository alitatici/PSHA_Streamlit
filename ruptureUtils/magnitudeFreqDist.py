import numpy as np

class DoublyBoundedGRModel():

    def __init__(self, minMag, maxMag, aGR, bGR, mBin = 0.25):
        self.minMag = minMag
        self.maxMag = maxMag
        self.aGR = aGR
        self.bGR = bGR
        self.magRange = np.arange(self.minMag,self.maxMag + mBin, mBin)
        self.cdfMFD = None
        self.pmfMFD = None
        self.sourceRate = None

    def db_gr_mfd_model(self):
        self.cdfMFD = ((1 - 10**(-self.bGR * (self.magRange - self.minMag))) /
                        (1 - 10**(-self.bGR * (self.maxMag - self.minMag))))
        cdf_1 = np.append(self.cdfMFD[1:], 1)
        cdf_2 = self.cdfMFD[0:]
        self.pmfMFD = cdf_1 - cdf_2
        self.sourceRate = 10 ** (self.aGR - self.bGR * self.minMag)



