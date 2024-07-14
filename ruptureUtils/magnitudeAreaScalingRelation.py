import numpy as np

class magnitudeScaling():
    def __init__(self, faultMechanism, faultLength, faultWidth, depthTopFault):
        self.faultMechanism = faultMechanism
        self.faultLength = faultLength
        self.faultWidth = faultWidth
        self.depthTopFault = depthTopFault
        self.ruptureLength = None

    def magnScalingLeonard2014(self, mfd, eqSource, aspectRatio=2):
        # Leonard 2010 coefficients are updated with Leonard 2014.
        # two_thirds_logM0 = M_w_fault + 6.0333;
        # Two thirds of log(seismic moment) from Hanks and Kanamori (1979)

        earthquake_magnitude_array = mfd.magRange
        ruptureLenghtList = []
        for earthquake_magnitude in earthquake_magnitude_array:

            if self.faultMechanism == "Normal" or self.faultMechanism == "Strike Slip":  # strike-slip and normal faulting
                z_tor = max(2.673 - 1.136 * max(earthquake_magnitude - 4.970, 0), 0) ** 2
            elif self.faultMechanism == "Reverse":  # reverse faulting
                z_tor = max(2.704 - 1.226 * max(earthquake_magnitude - 5.849, 0), 0) ** 2
            else:
                raise Exception(self.faultMechanism + " is not a valid fault_type.")

            if z_tor > self.depthTopFault:
                Z_tor_along_dip = (z_tor - self.depthTopFault) / np.sin(np.deg2rad(eqSource.dip))
            else:
                Z_tor_along_dip = 0
            avaliable_rupture_width_in_fault = self.faultWidth - Z_tor_along_dip

            # Leonard Functions - magnitude to rupture area
            if self.faultMechanism == "Strike Slip":  # Interplate SS
                a = 1.5
                b = 6.087
            else: # Interplate DS
                a = 1.5
                b = 6.098
            ruptureArea = 10 ** (((3 / 2) * (earthquake_magnitude + 6.0333) - b) / a)

            # Leonard Functions utilize meters as the unit of length.
            # Converting rupture area m2 to km2.
            ruptureArea = ruptureArea / 1e6

            # aspect ratio = length / width
            if avaliable_rupture_width_in_fault < (ruptureArea / aspectRatio):
                ruptureLength = ruptureArea / avaliable_rupture_width_in_fault
            else:
                ruptureLength = np.sqrt(ruptureArea * aspectRatio)

            if ruptureLength > self.faultLength:
                ruptureLength = self.faultLength
            
            ruptureLenghtList.append(round(ruptureLength, 3))

        self.ruptureLength = ruptureLenghtList
