import os
import pickle

import streamlit as st

import plotly.graph_objects as go

from tabs.SolarPanels import PANEL_1_DATA, PANEL_2_DATA, PANEL_3_DATA
from tabs.SolarPanels import PANEL_1_CONSTANT, PANEL_2_CONSTANT, PANEL_3_CONSTANT


def show_production():
    cwd = os.getcwd()

    model_path = os.path.join(
        cwd, 'models/random_forest/pickle/trained_random_forest.pkl')
    x_scaler_path = os.path.join(
        cwd, 'models/random_forest/pickle/x_scaler.pkl')
    y_scaler_path = os.path.join(
        cwd, 'models/random_forest/pickle/y_scaler.pkl')
    
    with open(x_scaler_path, 'rb') as file:
        x_scaler = pickle.load(file)

    with open(y_scaler_path, 'rb') as file:
        y_scaler = pickle.load(file)

    st.title("Production")
    with st.container():
        st.subheader("Single production")
        column1, column2 = st.columns(2)

        with column1:
            model_dropdown = st.selectbox(
                'Select a model',
                ['Random Forest', 'Decision Tree', 'XGBoost'],
                key='model_dropdown_single_production'
            )

        with column2:
            solar_panel_dropdown = st.selectbox(
                'Select a solar panel',
                [PANEL_1_CONSTANT, PANEL_2_CONSTANT, PANEL_3_CONSTANT]
            )

        if st.button('Predict'):
            if 'df' not in st.session_state:
                st.error('⚠️Please generate the data first.')
                return

            if model_dropdown == 'Random Forest':
                with open(model_path, 'rb') as file:
                    model = pickle.load(file)

            df = st.session_state["df"]
            date = df['date']
            df = df.drop(columns=['date'], axis=1)

            df['building_id'] = 99
            df = df[x_scaler.feature_names_in_]
            df = replace_solar_panel_data(df, solar_panel_dropdown)

            x = x_scaler.transform(df)
            y = model.predict(x).reshape(-1, 1)
            y = y_scaler.inverse_transform(y).reshape(-1)

            plot_graph(x=date, y=y, title='Production estimation using Random Forest',
                        y_label='Production (kWh)', x_label='Date')

        # persist the graph in the UI
        if 'fig' in st.session_state:
            st.plotly_chart(st.session_state['fig'])

    with st.container():
        st.subheader("Compare production")
        column1, column2 = st.columns(2)

        with column1:
            model_dropdown = st.selectbox(
                'Select a model',
                ['Random Forest', 'Decision Tree', 'XGBoost'],
                key='model_dropdown_production_comparison'
            )

        with column2:
            pv_panel_options = st.multiselect(
                'Choose solar panels',
                [PANEL_1_CONSTANT, PANEL_2_CONSTANT, PANEL_3_CONSTANT],
            )
            
        if st.button('Predict', key='compare_production_button'):
            if 'df' not in st.session_state:
                st.error('⚠️Please generate the data first.')
                return
            
            if pv_panel_options == []:
                st.error('⚠️Please select at least one solar panel.')
                return

            if model_dropdown == 'Random Forest':
                with open(model_path, 'rb') as file:
                    model = pickle.load(file)

            df = st.session_state["df"]
            date = df['date']
            df = df.drop(columns=['date'], axis=1)

            df['building_id'] = 99
            df = df[x_scaler.feature_names_in_]
            
            y_values = []
            for pv_panel in pv_panel_options:
                df = replace_solar_panel_data(df, pv_panel)

                x = x_scaler.transform(df)
                y = model.predict(x).reshape(-1, 1)
                y = y_scaler.inverse_transform(y).reshape(-1)
                y_values.append(y)

            plot_comparison_graph(x=date, y_values=y_values, title='Production estimation using Random Forest',
                    y_label='Production (kWh)', x_label='Date')
            
        # persist the graph in the UI
        if 'comparison_fig' in st.session_state:
            st.plotly_chart(st.session_state['comparison_fig'])


def replace_solar_panel_data(df, solar_panel_dropdown):
    if solar_panel_dropdown == PANEL_1_CONSTANT:
        df['vmp'] = PANEL_1_DATA['vmp']
        df['imp'] = PANEL_1_DATA['imp']
        df['voc'] = PANEL_1_DATA['voc']
        df['isc'] = PANEL_1_DATA['isc']
        df['p_per_m2'] = PANEL_1_DATA['p_per_m2']
        df['p_max'] = PANEL_1_DATA['p_max']
        df['panel_area'] = PANEL_1_DATA['panel_area']

    elif solar_panel_dropdown == PANEL_2_CONSTANT:
        df['vmp'] = PANEL_2_DATA['vmp']
        df['imp'] = PANEL_2_DATA['imp']
        df['voc'] = PANEL_2_DATA['voc']
        df['isc'] = PANEL_2_DATA['isc']
        df['p_per_m2'] = PANEL_2_DATA['p_per_m2']
        df['p_max'] = PANEL_2_DATA['p_max']
        df['panel_area'] = PANEL_2_DATA['panel_area']

    elif solar_panel_dropdown == PANEL_3_CONSTANT:
        df['vmp'] = PANEL_3_DATA['vmp']
        df['imp'] = PANEL_3_DATA['imp']
        df['voc'] = PANEL_3_DATA['voc']
        df['isc'] = PANEL_3_DATA['isc']
        df['p_per_m2'] = PANEL_3_DATA['p_per_m2']
        df['p_max'] = PANEL_3_DATA['p_max']
        df['panel_area'] = PANEL_3_DATA['panel_area']

    return df


def plot_graph(x, y, title, y_label, x_label):
    fig = go.Figure(data=go.Scatter(x=x, y=y,
                                    hovertemplate='<b>Date</b>: %{x}<br>' +
                                    '<b>Production (kWh)</b>: %{y}<br>',
                                    name=''))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    st.session_state['fig'] = fig
    
    
def plot_comparison_graph(x, y_values, title, y_label, x_label):
    fig = go.Figure()
    for i, y in enumerate(y_values):
        fig.add_trace(go.Scatter(x=x, y=y,
                                 hovertemplate='<b>Date</b>: %{x}<br>' +
                                 f'<b>Production {i+1} (kWh)</b>: %{y}<br>',
                                 name=f'Production {i+1}'))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    st.session_state['comparison_fig'] = fig
