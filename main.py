### PSHA Calculation ###

"""
This code is written for understanding probabilistic seismic hazard analysis.

    Steps for PSHA:
    1- Identify all earthquake sources capable of producing damaging
    ground motions.
    2- Characterize the distribution of earthquake magnitudes (the rates
    at which earthquakes of various magnitudes are expected to occur).
    3- Characterize the distribution of source-to-site distances associated
    with potential earthquakes.
    4- Predict the resulting distribution of ground motion intensity as a
    function of earthquake magnitude, distance, etc.
    5- Combine uncertainties in earthquake size, location and ground
    motion intensity, using a calculation known as the total probability
    theorem.
    (Baker, Jack W. (2013) Probabilistic Seismic Hazard Analysis. White Paper Version 2.0.1, 79 pp.)
"""


### PSHA Calculation ###
# This main code is for development and is intended to run in debug mode.

from ruptureUtils.magnitudeFreqDist import *
from ruptureUtils.earthquakeSourceCharacteristics import *
from ruptureUtils.magnitudeAreaScalingRelation import *
from ruptureUtils.sourceModeling import *
from gmmFile.gmmMain import *
from visualizations.hazardCurve import *

# INPUTS
#      Source characteristics
coordinates = [[28.0, 40.8], [29.5, 40.7]]
seismicDepth = [0, 20]  # latitude, longitude
minMag, maxMag, aGR, bGR = 5, 8, 4, 1
dip, strike, rake = 90, [0, 60, 120, 180, 240, 300], 180
#      Site characteristics
site_coordinate = [29.2, 41.0]  # latitude, longitude
soilConditionVs30 = 300  # m/s
#      Rupture mesh spacing distance
meshSpace = 5    # km
imts = 'pgv'
GMM = 'ASB14'
# Generate intensity measure thresholds in logarithmic scale.
# This values will be X-axis values in hazard curve.
IMthresholds = np.logspace(0.01, 2, num=100)

# PSHA Steps
# Identify all earthquake sources capable of producing damaging ground motions.
eqSource = earthquakeSources(coordinates, seismicDepth, dip, rake)
eqSource.sourceCharacteristics()

# Characterize the distribution of earthquake magnitudes.
mfd = DoublyBoundedGRModel(minMag, maxMag, aGR, bGR)
mfd.db_gr_mfd_model()

# Characterize the distribution of source-to-site distances.
# Magnitude-Area scaling relation
magnScaling = magnitudeScaling(eqSource.faultingMechanism, eqSource.faultLength, eqSource.faultWidth,
                               eqSource.seismicDepth[0])
magnScaling.magnScalingLeonard2014(mfd, eqSource)

# Meshing line (fault) source.
eqSourceModeling = earthquakeSourcesModeling(eqSource, mfd, magnScaling, meshSpace)
eqSourceModeling.ruptureProps()

# Calculates closest distance between site and ruptures.
eqSourceModeling.calculateClosestDistance(site_coordinate)

# GMM
gmmCalc = gmmCalculations(eqSourceModeling, rake, soilConditionVs30, imts)
gmmCalc.getGMIM(GMM)

# Hazard Curve
fig = hazardCurveCalculator(eqSourceModeling.ruptureDataframe, mfd, IMthresholds, imts)
fig.show()

print("Stop here.")