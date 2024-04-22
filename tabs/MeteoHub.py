import pandas as pd
import streamlit as st
from datetime import datetime

from tabs.MeteorologicalDataParser import get_meteorological_data
from tabs.SolarPanels import PANEL_1_DATA, PANEL_2_DATA, PANEL_3_DATA
from tabs.SolarPanels import PANEL_1_CONSTANT, PANEL_2_CONSTANT, PANEL_3_CONSTANT


def show_data_form():
    st.markdown('### Meteorological data')

    column1, column2 = st.columns(2)
    with column1:
        if "start_date" not in st.session_state:
            st.session_state["start_date"] = datetime.now().strftime('%Y-%m-%d').replace('-', '')
        
        start_date_value = st.session_state.get("start_date")
        start_date_value = datetime.strptime(start_date_value, '%Y%m%d')
        start_date = st.date_input('Start date', value=start_date_value)
            
        start_date = process_date(date=start_date)

        if "end_date" not in st.session_state:
            st.session_state["end_date"] = datetime.now().strftime('%Y-%m-%d').replace('-', '')
            
        end_date_value = st.session_state.get("end_date")
        end_date_value = datetime.strptime(end_date_value, '%Y%m%d')
        end_date = st.date_input('End date', value=end_date_value)
            
        end_date = process_date(date=end_date)

    with column2:
        latitude = st.number_input('Latitude', value=st.session_state.get("latitude", 0))
        longitude = st.number_input('Longitude', value=st.session_state.get("longitude", 0))

    st.markdown('### Solar panel data')
    pv_manual_mode = st.checkbox('Use manual mode', value=st.session_state.get("pv_manual_mode", False))
    if pv_manual_mode:
        column1, column2 = st.columns(2)
        with column1:
            vmp = st.number_input('Vmp (V)', value=st.session_state.get("vmp", 0))
            imp = st.number_input('Imp (A)', value=st.session_state.get("imp", 0))
            voc = st.number_input('Voc (V)', value=st.session_state.get("voc", 0))
            isc = st.number_input('Isc (A)', value=st.session_state.get("isc", 0))

        with column2:
            p_per_m2 = st.number_input('Power per m² (W/m²)', value=st.session_state.get("p_per_m2", 0))
            panel_area = st.number_input('Panel panel_area (m²)', value=st.session_state.get("panel_area", 0))
            p_max = st.number_input('Max power (W)', value=st.session_state.get("p_max", 0))
    else:
        solar_panel_dropdown = st.selectbox(
            'Select a solar panel',
            [PANEL_1_CONSTANT, PANEL_2_CONSTANT, PANEL_3_CONSTANT]
        )
        
        selected_panel = None
        if solar_panel_dropdown == PANEL_1_CONSTANT:
            selected_panel = PANEL_1_DATA
        elif solar_panel_dropdown == PANEL_2_CONSTANT:
            selected_panel = PANEL_2_DATA
        elif solar_panel_dropdown == PANEL_3_CONSTANT:
            selected_panel = PANEL_3_DATA
            
        vmp = selected_panel['vmp']
        imp = selected_panel['imp']
        voc = selected_panel['voc']
        isc = selected_panel['isc']
        p_per_m2 = selected_panel['p_per_m2']
        panel_area = selected_panel['panel_area']
        p_max = selected_panel['p_max']

    st.markdown('### BIM data')
    column1, column2 = st.columns(2)
    with column1:
        facade_area = st.number_input('Facade panel_area (m²)', value=st.session_state.get("facade_area", 0))

    with column2:
        exploitation_ratio = st.number_input('Exploitation ratio (%), between 0 and 100', value=st.session_state.get("exploitation_ratio", 0))

    st.markdown('\n')
    if st.button('Generate data'):
        end_date_month = datetime.strptime(end_date, '%Y%m%d').month
        if end_date_month == pd.Timestamp.now().month:
            st.error('⚠️ Please don\'t select the current month as the end date.')
            return

        if errors_exist(start_date, end_date, latitude, longitude, vmp, imp, voc, isc, p_per_m2, panel_area, p_max, facade_area, exploitation_ratio):
            st.session_state["is_df_loaded"] = False
            return

        with st.spinner('Generating data ...'):
            # Getting meteo data
            df = get_meteorological_data(
                start_date, end_date, latitude, longitude)
            if df is None:
                return

            # Adding location data
            df['latitude'] = latitude
            df['longitude'] = longitude

            # Adding PV data
            df['vmp'] = vmp
            df['imp'] = imp
            df['voc'] = voc
            df['isc'] = isc
            df['p_per_m2'] = p_per_m2
            df['p_max'] = p_max
            df['panel_area'] = panel_area

            # Adding BIM data
            df['facade_area'] = facade_area
            df['exploitation_ratio'] = exploitation_ratio
            df['total_panel_area'] = facade_area * exploitation_ratio

            st.session_state["df"] = df
            
            st.session_state["start_date"] = start_date
            st.session_state["end_date"] = end_date
            
            st.session_state["latitude"] = latitude
            st.session_state["longitude"] = longitude
            
            st.session_state["vmp"] = vmp
            st.session_state["imp"] = imp
            st.session_state["voc"] = voc
            st.session_state["isc"] = isc
            st.session_state["p_per_m2"] = p_per_m2
            st.session_state["panel_area"] = panel_area
            st.session_state["p_max"] = p_max
            
            st.session_state["facade_area"] = facade_area
            st.session_state["exploitation_ratio"] = exploitation_ratio

            st.session_state["pv_manual_mode"] = pv_manual_mode
            st.session_state["is_df_loaded"] = True
            
    # persist the data in the UI
    if st.session_state.get("is_df_loaded"):
        st.dataframe(st.session_state["df"])

def process_date(date):
    date = str(date).replace('-', '')
    return date


def errors_exist(start_date, end_date, latitude, longitude, vmp, imp, voc, isc, p_per_m2, panel_area, p_max, facade_area, exploitation_ratio):
    if (latitude == 0) or (longitude == 0):
        st.error('Latitude and Longitude must be different from 0')
        return True

    if start_date > end_date:
        st.error('Start date must be less than end date')
        return True

    if start_date == end_date:
        st.error('Start date must be different from end date')
        return True
    
    if (vmp <= 0) or (imp <= 0) or (voc <= 0) or (isc <= 0):
        st.error('Vmp, Imp, Voc and Isc must be greater than 0')
        return True

    if (p_per_m2 <= 0) or (panel_area <= 0) or (p_max <= 0):
        st.error('Power per m², Panel panel_area and Max power must be greater than 0')
        return True

    if exploitation_ratio <= 0 or exploitation_ratio > 100:
        st.error('Exploitation rate must be between 0 and 100')
        return True
    
    if facade_area <= 0:
        st.error('Facade panel_area must be greater than 0')
        return True
    
    return False
