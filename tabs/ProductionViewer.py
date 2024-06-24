import os
import pickle

import numpy as np
import pandas as pd
import streamlit as st

import plotly.graph_objects as go

from keras.models import load_model

from tabs.SolarPanels import PANEL_DATA
from tabs.SolarPanels import PANEL_CONSTANTS


def show_production():
    cwd = os.getcwd()

    x_scaler_path = os.path.join(
        cwd, 'scaler/x_scaler.pkl')
    
    with open(x_scaler_path, 'rb') as file:
        x_scaler = pickle.load(file)

    st.title("Production")
    with st.container():
        st.subheader("Single production")
        column1, column2 = st.columns(2)

        with column1:
            model_dropdown = st.selectbox(
                'Select a model',
                ['XGBoost', 'Decision Tree', 'Gradient Boosting'],
                key='model_dropdown_single_production'
            )

        with column2:
            solar_panel_dropdown = st.selectbox(
                'Select a solar panel',
                PANEL_CONSTANTS
            )
            
        with st.expander('Prediction date frequency'):
            date_frequency = st.radio('Predictions', ['Day', 'Month'], key='predictions_radio')

        if st.button('Predict'):
            if 'df' not in st.session_state:
                st.error('⚠️Please generate the data first.')
                return

            model = get_model(cwd, model_dropdown)
                    
            df = st.session_state["df"]
            date = df['date']
            df = df.drop(columns=['date'], axis=1)

            select_features = list(x_scaler.feature_names_in_)
            df = df[select_features]
            df = replace_solar_panel_data(df, solar_panel_dropdown)

            x = x_scaler.transform(df)
            y = model.predict(x).ravel()
            y = np.clip(y, 0, None)

            total_prediction = y.sum()
            st.session_state['energy_produced'] = total_prediction
            
            prediction_df = pd.DataFrame({'date': date, 'production': y})
            
            if date_frequency == 'Month':
                st.session_state["date_frequency"] = 'Month'
                prediction_df = convert_daily_to_monthly(prediction_df)
            else:
                st.session_state["date_frequency"] = 'Day'
                
            plot_graph(x=date, y=prediction_df['production'].values, title=f'Production estimation using {model_dropdown}',
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
                ['XGBoost', 'Decision Tree', 'Gradient Boosting'],
                key='model_dropdown_production_comparison'
            )

        with column2:
            pv_panel_options = st.multiselect(
                'Choose solar panels',
                PANEL_CONSTANTS,
            )
            
        with st.expander('Prediction date frequency'):
            date_frequency = st.radio('Predictions', ['Day', 'Month'], key='predictions_radio_comparison')
            
        if st.button('Predict', key='compare_production_button'):
            if 'df' not in st.session_state:
                st.error('⚠️Please generate the data first.')
                return
            
            if pv_panel_options == []:
                st.error('⚠️Please select at least one solar panel.')
                return

            model = get_model(cwd, model_dropdown)
                    
            df = st.session_state["df"]
            date = df['date']
            df = df.drop(columns=['date'], axis=1)

            select_features = list(x_scaler.feature_names_in_)
            df = df[select_features]
            
            y_values = []
            for i, pv_panel in enumerate(pv_panel_options):
                df = replace_solar_panel_data(df, pv_panel)

                x = x_scaler.transform(df)
                y = model.predict(x).ravel()
                
                prediction_df = pd.DataFrame({'date': date, 'production': y})
                
                if date_frequency == 'Month':
                    st.session_state["date_frequency_comparison"] = 'Month'
                    prediction_df = convert_daily_to_monthly(prediction_df)
                else:
                    st.session_state["date_frequency_comparison"] = 'Day'
                    
                y = prediction_df['production'].values
                y = np.clip(y, 0, None)
                y_values.append(y)
                
            fig = plot_comparison_graph(
                x=date,
                y_values=y_values,
                hue=pv_panel_options,
                title=f'Production estimation using {model_dropdown}',
                y_label='Production (kWh)',
                x_label='Date'
            )
            st.session_state['pv_comparison_fig'] = fig
            
        # persist the graph in the UI
        if 'pv_comparison_fig' in st.session_state:
            st.plotly_chart(st.session_state['pv_comparison_fig'])
                        
    with st.container():
        st.subheader("Compare models")
        column1, column2 = st.columns(2)
        
        with column1:
            model_options = st.multiselect(
                'Choose models',
                ['XGBoost', 'Decision Tree', 'Gradient Boosting'],
            )
        
        with column2:
            solar_panel_dropdown = st.selectbox(
                'Select a solar panel',
                PANEL_CONSTANTS,
                key='solar_panel_dropdown_compare_models'
            )
            
        with st.expander('Prediction date frequency'):
            date_frequency = st.radio('Predictions', ['Day', 'Month'], key='predictions_radio_model_comparison')
            
        if st.button('Predict', key='compare_models_button'):
            if 'df' not in st.session_state:
                st.error('⚠️Please generate the data first.')
                return
            
            if model_options == []:
                st.error('⚠️Please select at least one model.')
                return
            
            df = st.session_state["df"]
            date = df['date']
            df = df.drop(columns=['date'], axis=1)

            select_features = list(x_scaler.feature_names_in_)
            df = df[select_features]
            
            y_values = []
            for model_name in model_options:
                model = get_model(cwd, model_name)
                
                df = replace_solar_panel_data(df, solar_panel_dropdown)

                x = x_scaler.transform(df)
                y = model.predict(x).ravel()
                
                prediction_df = pd.DataFrame({'date': date, 'production': y})
                
                if date_frequency == 'Month':
                    st.session_state["date_frequency_comparison"] = 'Month'
                    prediction_df = convert_daily_to_monthly(prediction_df)
                else:
                    st.session_state["date_frequency_comparison"] = 'Day'
                    
                y = prediction_df['production'].values
                y = np.clip(y, 0, None)
                y_values.append(y)
                
            fig = plot_comparison_graph(
                x=date,
                y_values=y_values,
                hue=model_options,
                title=f'Production comparison between models',
                y_label='Production (kWh)',
                x_label='Date'
            )
            st.session_state['model_comparison_fig'] = fig
            
        # persist the graph in the UI
        if 'model_comparison_fig' in st.session_state:
            st.plotly_chart(st.session_state['model_comparison_fig'])


def get_model(cwd, model_dropdown):
    if model_dropdown == 'XGBoost':
        model_path = os.path.join(cwd, 'models/XGBRegressor.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)

    elif model_dropdown == 'DNN':
        model_path = os.path.join(cwd, 'models/dnn.keras')
        model = load_model(model_path)

    elif model_dropdown == 'Decision Tree':
        model_path = os.path.join(cwd, 'models/DecisionTreeRegressor.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
            
    elif model_dropdown == 'Gradient Boosting':
        model_path = os.path.join(cwd, 'models/GradientBoostingRegressor.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
            
    elif model_dropdown == 'Random Forest':
        model_path = os.path.join(cwd, 'models/RandomForestRegressor.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
            
    return model

def convert_daily_to_monthly(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df = df.resample('ME').sum()
    df = df.reset_index()
    df['date'] = df['date'].dt.strftime('%Y-%m')
    return df


def replace_solar_panel_data(df, solar_panel_choice):
    solar_panel_data = PANEL_DATA[solar_panel_choice]
    df['pv_peak_power'] = solar_panel_data['pv_peak_power']
    df['pv_width'] = solar_panel_data['pv_width']
    df['pv_height'] = solar_panel_data['pv_height']
    df['pv_vocc'] = solar_panel_data['pv_vocc']
    df['pv_vmpp'] = solar_panel_data['pv_vmpp']
    df['pv_isc'] = solar_panel_data['pv_isc']

    return df


def plot_graph(x, y, title, y_label, x_label):
    if st.session_state['date_frequency'] == 'Day':
        fig = go.Figure(data=go.Scatter(x=x, y=y,
                                        hovertemplate='<b>Date</b>: %{x}<br>' +
                                        '<b>Production (kWh)</b>: %{y}<br>',
                                        name=''))
    elif st.session_state['date_frequency'] == 'Month':
        x.index = pd.to_datetime(x)
        x = x.resample('ME').mean()
        x = x.index.strftime('%Y-%m')
        
        fig = go.Figure(data=go.Bar(x=x, y=y,
                                    hovertemplate='<b>Month</b>: %{x}<br>' +
                                    '<b>Production (kWh)</b>: %{y}<br>',
                                    name=''))
        
        fig.update_layout(
            xaxis=dict(
                tickvals=x,
                ticktext=x,
            ),
        )
    else:
        raise ValueError("Invalid date_frequency. Expected 'Day' or 'Month'.")

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    st.session_state['fig'] = fig
    
    
def plot_comparison_graph(x, y_values, hue, title, y_label, x_label):
    fig = go.Figure()
    
    if st.session_state['date_frequency_comparison'] == 'Day':
        for i, y in enumerate(y_values):
            fig.add_trace(go.Scatter(x=x, y=y,
                                        hovertemplate='<b>Date</b>: %{x}<br>' +
                                        '<b>Production (kWh)</b>: %{y}<br>',
                                        name=hue[i]))
    elif st.session_state['date_frequency_comparison'] == 'Month':
        x.index = pd.to_datetime(x)
        x = x.resample('ME').mean()
        x = x.index.strftime('%Y-%m')
        
        for i, y in enumerate(y_values):
            fig.add_trace(go.Bar(x=x, y=y,
                                        hovertemplate='<b>Month</b>: %{x}<br>' +
                                        '<b>Production (kWh)</b>: %{y}<br>',
                                        name=hue[i]))
            
        fig.update_layout(
            xaxis=dict(
                tickvals=x,
                ticktext=x,
            ),
        )
    else:
        raise ValueError("Invalid date_frequency. Expected 'Day' or 'Month'.")

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )
        
    return fig
