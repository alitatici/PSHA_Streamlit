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

from ruptureUtils.magnitudeFreqDist import *
from ruptureUtils.earthquakeSourceCharacteristics import *
from ruptureUtils.magnitudeAreaScalingRelation import *
from ruptureUtils.sourceModeling import *
from gmmFile.gmmMain import *
from visualizations.hazardCurve import *

def mainWebGUI_def(coordinates, seismicDepth, minMag, maxMag, aGR, bGR, dip, rake, siteCoordinate,
                   soilConditionVs30, meshSpace, imts, GMM, IMthresholds):
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
    eqSourceModeling.calculateClosestDistance(siteCoordinate)

    # GMM
    gmmCalc = gmmCalculations(eqSourceModeling, rake, soilConditionVs30, imts)
    gmmCalc.getGMIM(GMM)

    # Hazard Curve
    hazardCurveFigure = hazardCurveCalculator(eqSourceModeling.ruptureDataframe, mfd, IMthresholds, imts)

    return eqSourceModeling.ruptureDataframe, hazardCurveFigure