from gmmFile.gmmASB14 import AkkarEtAlRjb2014
import numpy as np

class gmmCalculations():
    def __init__(self, eqSourceModeling, rake, soilConditionVs30, imts):
        self.eqSourceModeling = eqSourceModeling
        self.rake = rake
        self.soilConditionVs30 = soilConditionVs30
        self.imts = imts

    def getGMIM(self, GMM):
        if GMM == 'ASB14':
            gmm = AkkarEtAlRjb2014()
        else:
            raise Exception(GMM + " is not a valid.")

        mean, tau, phi, sig = gmm.compute(self.eqSourceModeling.ruptureDataframe['Magnitude'],
                                          self.eqSourceModeling.ruptureDataframe['Closest Distance'],
                                          self.rake, self.soilConditionVs30, self.imts)

        self.eqSourceModeling.ruptureDataframe["IM median"] = np.exp(mean)
        self.eqSourceModeling.ruptureDataframe["Between-event (tau) Residual"] = [tau] * len(mean)
        self.eqSourceModeling.ruptureDataframe["Within-event (phi) Residual"] = [phi] * len(mean)
        self.eqSourceModeling.ruptureDataframe["Total Residual"] = [sig] * len(mean)

