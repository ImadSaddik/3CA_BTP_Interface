import pandas as pd
import streamlit as st
from datetime import datetime

from tabs.MeteorologicalDataParser import get_meteorological_data
from tabs.SolarPanels import PANEL_DATA
from tabs.SolarPanels import PANEL_CONSTANTS


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
        latitude = st.number_input('Latitude', value=st.session_state.get("latitude", 0.0), step=0.01)
        longitude = st.number_input('Longitude', value=st.session_state.get("longitude", 0.0), step=0.01)

    st.markdown('### Solar panel data')
    pv_manual_mode = st.checkbox('Use manual mode', value=st.session_state.get("pv_manual_mode", False))
    if pv_manual_mode:
        column1, column2 = st.columns(2)
        with column1:
            vmpp = st.number_input('Vmpp (V)', value=st.session_state.get("pv_vmpp", 0))
            vocc = st.number_input('Vocc (V)', value=st.session_state.get("pv_vocc", 0))
            isc = st.number_input('Isc (A)', value=st.session_state.get("pv_isc", 0))

        with column2:
            height = st.number_input('Height (m)', value=st.session_state.get("pv_height", 0))
            width = st.number_input('Width (m)', value=st.session_state.get("pv_width", 0))
            p_max = st.number_input('Max power (W)', value=st.session_state.get("pv_peak_power", 0))
    else:
        solar_panel_dropdown = st.selectbox(
            'Select a solar panel',
            PANEL_CONSTANTS
        )
        
        if solar_panel_dropdown is not None:
            selected_panel = PANEL_DATA[solar_panel_dropdown]
            
            p_max = selected_panel['pv_peak_power']
            width = selected_panel['pv_width']
            height = selected_panel['pv_height']
            vocc = selected_panel['pv_vocc']
            vmpp = selected_panel['pv_vmpp']
            isc = selected_panel['pv_isc']

    st.markdown('### BIM data')
    facade_type_dropdown = st.selectbox(
            'Select where to put the solar panels',
            ['Facade', 'Roof']
        )
    
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

        if errors_exist(start_date, end_date, latitude, longitude, vmpp, vocc, isc, width, height, p_max, facade_area, exploitation_ratio):
            st.session_state["is_df_loaded"] = False
            return

        with st.spinner('Generating data ...'):
            # Getting meteo data
            df = get_meteorological_data(
                start_date, end_date, latitude, longitude)
            if df is None:
                return

            # Adding PV data
            df['pv_peak_power'] = p_max
            df['pv_width'] = width
            df['pv_height'] = height
            df['pv_vmpp'] = vmpp
            df['pv_vocc'] = vocc
            df['pv_isc'] = isc

            panel_area = width * height
            usable_area = facade_area * exploitation_ratio / 100
            df['number_solar_panels'] = int(usable_area / panel_area)
            df['facade_type'] = 1 if facade_type_dropdown == 'Facade' else 2

            # Saving everything to state
            st.session_state["df"] = df
            
            st.session_state["start_date"] = start_date
            st.session_state["end_date"] = end_date
            
            st.session_state["latitude"] = latitude
            st.session_state["longitude"] = longitude
            
            st.session_state["pv_peak_power"] = p_max
            st.session_state["pv_width"] = width
            st.session_state["pv_height"] = height
            st.session_state["pv_vmpp"] = vmpp
            st.session_state["pv_vocc"] = vocc
            st.session_state["pv_isc"] = isc
            
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


def errors_exist(start_date, end_date, latitude, longitude, vmp, voc, isc, width, height, p_max, facade_area, exploitation_ratio):
    if (latitude == 0) or (longitude == 0):
        st.error('Latitude and Longitude must be different from 0')
        return True

    if start_date > end_date:
        st.error('Start date must be less than end date')
        return True

    if start_date == end_date:
        st.error('Start date must be different from end date')
        return True
    
    if (vmp <= 0) or (voc <= 0) or (isc <= 0):
        st.error('Vmpp, Vocc and Isc must be greater than 0')
        return True

    if (width <= 0) or (height <= 0) or (p_max <= 0):
        st.error('Width, Height and Max power must be greater than 0')
        return True

    if exploitation_ratio <= 0 or exploitation_ratio > 100:
        st.error('Exploitation rate must be between 0 and 100')
        return True
    
    if facade_area <= 0:
        st.error('Facade panel_area must be greater than 0')
        return True
    
    return False
