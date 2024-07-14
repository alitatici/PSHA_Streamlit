import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def hazardCurveCalculator(ruptureDataframe, mfd, imThresholds, imts):

    median = ruptureDataframe['IM median'].values
    totalSigma = ruptureDataframe['Total Residual'].values
    magnitudePMFs = ruptureDataframe["P(M=m)"].values
    distancePMFs = ruptureDataframe["P(R=r|m)"].values

    imThresholdList = np.round(imThresholds, 4)

    probExceedanceList = []
    for imThreshold in imThresholdList:

        probExceedanceArray = 0
        for index in range(len(median)):
            probExceedance = 1 - norm.cdf(np.log(imThreshold), np.log(median[index]), totalSigma[index])
            probExceedanceArray = probExceedanceArray + probExceedance * magnitudePMFs[index] * distancePMFs[index] * mfd.sourceRate

        probExceedanceList.append(probExceedanceArray)
    rateExceedance = np.array(probExceedanceList)

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
    ax.loglog(imThresholdList, rateExceedance, linestyle='-', color='r')
    ax.grid(which='both', linestyle='--', linewidth=0.5)
    ax.set_title('Hazard Curve')

    if imts == "pga":
        imt = "PGA (g)"
    elif imts == "pgv":
        imt = "PGV (cm/s)"

    ax.set_xlabel(imt)
    ax.set_ylabel('Annual Rate of Exceedance')

    return fig