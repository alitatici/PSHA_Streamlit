from PSHAmainChannel import mainWebGUI_def
from visualizations.mapGen import *
import numpy as np
import streamlit as st

# Streamlit App
st.title('PSHA Streamlit App')
st.write("This program performs Probabilistic Seismic Hazard Analysis (PSHA) for a specified site, "
         "utilizing a single-segment 2D fault source (line source).")
st.write("---")

tab1, tab2 = st.tabs(["Inputs", "Outputs"])

with st.form("main form", clear_on_submit=True):
    with tab1:
        st.header('Program Inputs')
        with st.container():
            st.subheader('Source Characteristics')
            col1, col2 = st.columns(2)
            with col1:
                startingCoordinate = st.text_input('Input starting point (Latitude, Longitude)', '28.0, 40.8')
            with col2:
                endingCoordinate = st.text_input('Input ending point (Latitude, Longitude)', '29.5, 40.7')
            # Seismic Depth input using columns for side by side input
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                seismicDepth_min = st.number_input('Upper Seismic Depth (km)', min_value=0, max_value=50, value=0)
            with col2:
                seismicDepth_max = st.number_input('Lower Seismic Depth (km)', min_value=0, max_value=50, value=20)
            with col3:
                dip = st.number_input('Dip', min_value=0, max_value=90, value=90)
            with col4:
                rake = st.number_input('Rake', min_value=-180, max_value=180, value=180)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                minMag = st.number_input('Minimum Magnitude', min_value=0.0, max_value=10.0, value=5.0, step=0.1)
            with col2:
                maxMag = st.number_input('Maximum Magnitude', min_value=0.0, max_value=10.0, value=8.0, step=0.1)
            with col3:
                aGR = st.number_input('aGR', value=4.00, step=0.01)
            with col4:
                bGR = st.number_input('bGR', value=1.00, step=0.01)
            # TODO: reopen when you add point/area source.
            # strike = st.text_input('Strike (comma-separated values)', '0,60,120,180,240,300')
            # strike = list(map(float, strike.split(',')))

            st.subheader('Site Characteristics')
            siteCoordinate = st.text_input('Site Coordinate (Latitude, Longitude)', '29.2, 41.0')
            soilConditionVs30 = st.number_input('Soil Condition VS30 (m/s)', value=700)

            st.subheader('Model Adjustments')
            meshSpace = st.number_input('Fault Mesh Spacing Distance (km)', value=10.0)

            st.subheader('Ground Motion Model')

            GMM = st.selectbox('Select ground motion model', ['ASB14'])
            # Create a dropdown list
            imts = st.selectbox('Select intensity measure type', ['PGA', 'PGV'])

            if imts == 'PGA':
                col1, col2, col3 = st.columns(3)
                with col1:
                    IMthresholdsStart = st.number_input('Hazard curve, PGA (g) lower limit',
                                                        min_value=0.0001, value=0.1, step=0.0001)
                with col2:
                    IMthresholdsEnd = st.number_input('Hazard curve, PGA (g) upper limit',
                                                      min_value=0.0002, value=2.0, step=0.0001)
                with col3:
                    IMthresholdsInterval = st.number_input('Number of interval', value=100, step=1)

                IMthresholds = np.logspace(np.log10(IMthresholdsStart), np.log10(IMthresholdsEnd),
                                           num=IMthresholdsInterval)
            elif imts == 'PGV':
                col1, col2, col3 = st.columns(3)
                with col1:
                    IMthresholdsStart = st.number_input('Hazard curve, PGV (cm/s) lower limit',
                                                        min_value=0.0001, value=0.1, step=0.0001)
                with col2:
                    IMthresholdsEnd = st.number_input('Hazard curve, PGV (cm/s) upper limit',
                                                      min_value=0.0002, value=100.0, step=0.0001)
                with col3:
                    IMthresholdsInterval = st.number_input('Number of interval', value=100, step=1)

                IMthresholds = np.logspace(np.log10(IMthresholdsStart), np.log10(IMthresholdsEnd),
                                           num=IMthresholdsInterval)

            # Convert the selected value to lowercase
            imts = imts.lower()

            # Convert input strings to lists
            startingLat, startingLon = map(float, startingCoordinate.split(','))
            endingLat, endingLon = map(float, endingCoordinate.split(','))
            coordinates = [[startingLat, startingLon], [endingLat, endingLon]]
            seismicDepth = [float(seismicDepth_min), float(seismicDepth_max)]
            siteCoordinate = list(map(float, siteCoordinate.split(',')))

    with tab2:
        st.header('Program Outputs')
        with st.container():
            # Calculations
            ruptureDataframe, hazardCurveFigure = mainWebGUI_def(coordinates, seismicDepth, minMag, maxMag, aGR,
                                                                 bGR, dip, rake, siteCoordinate, soilConditionVs30,
                                                                 meshSpace, imts, GMM, IMthresholds)

            st.subheader('Simulated Ruptures')
            figRuptureMap = generateRuptureMap(coordinates, siteCoordinate, ruptureDataframe)
            st.pyplot(figRuptureMap)

            st.subheader('Rupture Table')
            st.write("The following table provides simulated ruptures' magnitude, coordinates, closest distance "
                     "(km) to the site, and GMIM results.")
            st.dataframe(ruptureDataframe)

            st.pyplot(hazardCurveFigure)

st.write("---")
st.markdown("""<style>.small-font {font-size:14px;}</style>""", unsafe_allow_html=True)
st.markdown('<p class="small-font">Disclaimer: This code is written solely for educational purposes to implement and '
            'test the Streamlit library. It is not recommended to use the obtained outputs.</p>',
            unsafe_allow_html=True)
st.markdown('<p class="small-font">Disclaimer: Please inform me if you find any bugs or if you have any suggestions. '
            '</p>',
            unsafe_allow_html=True)

# Run the app with `streamlit run PSHA-StreamlitApp.py`
