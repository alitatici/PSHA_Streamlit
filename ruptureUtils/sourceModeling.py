import numpy as np
import math
import pandas as pd
from shapely.geometry import LineString, Point
from geopy.distance import geodesic

class earthquakeSourcesModeling():
    def __init__(self, eqSource, mfd, magnScaling, meshSpace):
        self.eqSource = eqSource
        self.mfd = mfd
        self.magnScaling = magnScaling
        self.meshSpace = meshSpace
        self.ruptureDataframe = pd.DataFrame(columns=["Magnitude", "Starting coordinate", "Ending coordinate"])

    def meshFaultSource(self):
        faultMeshDistancesList = []
        for i, magnitudes in enumerate(self.mfd.magRange):
            if self.magnScaling.ruptureLength[i] >= self.eqSource.faultLength:
                ruptureLength = self.eqSource.faultLength
            else:
                ruptureLength = self.magnScaling.ruptureLength[i]
            number = int(ruptureLength / self.meshSpace)
            meshSpaceChanged = number * self.meshSpace
            faultMeshDistances = np.arange(0, self.eqSource.faultLength - meshSpaceChanged, self.meshSpace)
            lastUnrupturedPart = (self.eqSource.faultLength - (faultMeshDistances[-1] +
                                  self.magnScaling.ruptureLength[i]))
            faultMeshDistancesShifted = faultMeshDistances + lastUnrupturedPart / 2
            faultMeshDistancesList.append(faultMeshDistancesShifted)

        return faultMeshDistancesList

    def getRuptureCoordinate(self):

        def getNewCoordinate(lat, lon, distanceList, azimuth):
            # Convert latitude, longitude, and azimuth to radians
            lat = math.radians(lat)
            lon = math.radians(lon)
            azimuth = math.radians(azimuth)

            # Earth radius in kilometers (mean radius)
            R = 6371.0

            newLatList, newLonList = [], []
            for distance in distanceList:
                # Calculate the new latitude
                newLat = math.asin(math.sin(lat) * math.cos(distance / R) +
                                    math.cos(lat) * math.sin(distance / R) * math.cos(azimuth))

                # Calculate the new longitude
                newLon = lon + math.atan2(math.sin(azimuth) * math.sin(distance / R) * math.cos(lat),
                                           math.cos(distance / R) - math.sin(lat) * math.sin(newLat))

                # Convert the new coordinates from radians to degrees
                newLat = math.degrees(newLat)
                newLon = math.degrees(newLon)

                newLatList.append(np.round(newLat,4))
                newLonList.append(np.round(newLon,4))
                newCoordinates = [[a, b] for a, b in zip(newLatList, newLonList)]

            return newCoordinates

        faultMeshDistancesList = self.meshFaultSource()

        startingCoordinatesList = []
        endingCoordinatesList = []
        for index, distanceList in enumerate(faultMeshDistancesList):
            startingCoordinates = getNewCoordinate(self.eqSource.coordinates[0][0], self.eqSource.coordinates[0][1],
                                                   distanceList, self.eqSource.strike)
            startingCoordinatesList.append(startingCoordinates)

            endingCoordinatesListTemp = []
            for strCords in startingCoordinates:
                endingCoordinates = getNewCoordinate(strCords[0], strCords[1],
                                                     [self.magnScaling.ruptureLength[index]],
                                                     self.eqSource.strike)
                endingCoordinatesListTemp.append(endingCoordinates)

            endingCoordinatesList.append(endingCoordinatesListTemp)

        return startingCoordinatesList, endingCoordinatesList

    def ruptureProps(self):

        startingCoordinatesList, endingCoordinatesList = self.getRuptureCoordinate()

        dictMagPMF = {'magRange': self.mfd.magRange, 'pmfMFD': self.mfd.pmfMFD}

        def get_pmf_for_mag(mag):
            try:
                j = np.where(dictMagPMF['magRange'] == mag)[0]
                return dictMagPMF['pmfMFD'][j][0]
            except ValueError:
                return None

        for index, magnitude in enumerate(self.mfd.magRange):

            # Flatten ending points
            ending_points_flat = [item[0] for item in endingCoordinatesList[index]]

            # Create the DataFrame
            data = {
                "Magnitude": [magnitude] * len(startingCoordinatesList[index]),
                "P(M=m)": [get_pmf_for_mag(magnitude)] * len(startingCoordinatesList[index]),
                "P(R=r|m)": [1 / len(startingCoordinatesList[index])] * len(startingCoordinatesList[index]),
                "Starting coordinate": startingCoordinatesList[index],
                "Ending coordinate": ending_points_flat
            }

            df = pd.DataFrame(data)

            self.ruptureDataframe = pd.concat([self.ruptureDataframe, df], ignore_index=True)
            self.ruptureDataframe.index = self.ruptureDataframe.index + 1

    def calculateClosestDistance(self, siteCoordinate):
        """
        Calculate the closest distance between the given point and each line in the DataFrame.
        :param point: A tuple representing the point (longitude, latitude).
        :return: A DataFrame with the closest distances.
        """
        distances = []
        point_geom = Point(siteCoordinate)

        for _, row in self.ruptureDataframe.iterrows():
            line = LineString([row["Starting coordinate"], row["Ending coordinate"]])
            # degree
            # distance = point_geom.distance(line)
            # km
            nearest_point = line.interpolate(line.project(point_geom))
            distance = geodesic((point_geom.y, point_geom.x), (nearest_point.y, nearest_point.x)).kilometers

            distances.append(distance)

        self.ruptureDataframe["Closest Distance"] = distances

