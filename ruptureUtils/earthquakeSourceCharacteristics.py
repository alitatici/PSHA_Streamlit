import numpy as np
import math

class earthquakeSources():

    def __init__(self, coordinates, seismicDepth, dip, rake):
        self.coordinates = coordinates
        self.dip = dip
        self.strike = None
        self.rake = rake
        self.seismicDepth = seismicDepth
        self.sourceType = None
        self.segmentLengths = None
        self.faultLength = None
        self.faultWidth = None
        self.faultingMechanism = None

    def haversineDistance(self, coord1, coord2):
        # Radius of the Earth in kilometers
        R = 6371.0

        lat1, lon1 = np.radians(coord1)
        lat2, lon2 = np.radians(coord2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distance = R * c
        return distance

    def getFaultDimensions(self):
        lengths = []
        total_length = 0

        for i in range(len(self.coordinates) - 1):
            segment_length = self.haversineDistance(self.coordinates[i], self.coordinates[i + 1])
            lengths.append(segment_length)
            total_length += segment_length

        self.segmentLengths = lengths
        self.faultLength = total_length
        self.faultWidth = (self.seismicDepth[1] - self.seismicDepth[0]) / np.sin(np.pi * self.dip / 180)

    def determineSourceType(self):
        if isinstance(self.coordinates, list) and all(
                isinstance(coord, list) and len(coord) == 2 for coord in self.coordinates):
            if len(self.coordinates) == 1:
                self.sourceType = "Point"
            else:
                self.sourceType = "Fault"
        else:
            self.sourceType = "invalid"

    def sourceCharacteristics(self):
        self.determineSourceType()
        if self.sourceType == "Fault":
            self.getFaultDimensions()
            self.strike = None
            self.getStrikeAngle()

        if self.rake < 0:
            self.rake =+ 360

        if self.rake > 225 and self.rake < 315:
            self.faultingMechanism = "Normal"
        elif self.rake > 45 and self.rake < 135:
            self.faultingMechanism = "Reverse"
        else:
            self.faultingMechanism = "Strike Slip"

    def getStrikeAngle(self):
        def calculate_azimuth(p1, p2):
            """
            Calculate the azimuth between two geographical points.
            :param p1: Tuple of the first point (longitude, latitude).
            :param p2: Tuple of the second point (longitude, latitude).
            :return: Azimuth in degrees.
            """
            lat1, lon1 = p1
            lat2, lon2 = p2

            # Convert from degrees to radians
            lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

            # Calculate the difference in longitude
            delta_lon = lon2 - lon1

            # Calculate the azimuth
            x = math.sin(delta_lon) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))

            angle = math.atan2(x, y)
            azimuth = (math.degrees(angle) + 360) % 360  # Normalize to 0-360 degrees
            return azimuth

        azimuth_angles = []
        for i in range(len(self.coordinates) - 1):
            azimuth = calculate_azimuth(self.coordinates[i], self.coordinates[i + 1])
            azimuth_angles.append(round(azimuth, 3))

        self.strike = azimuth_angles[0]



