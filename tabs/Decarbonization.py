import streamlit as st
import plotly.graph_objects as go


def show_decarbonization():
    st.markdown('### Decarbonization')
    st.write('This tab allows you to calculate the energy that can be deduced from the energy produced by the solar panels.')
    
    if "energy_produced" not in st.session_state:
        st.warning('⚠️ Please make sure to use the production tab to predict the PV production.')
        return
    
    print(st.session_state.get("energy_produced", 7050.0))
        
    energy_produced = st.number_input('Energy produced (kWh/year)', value=float(st.session_state.get("energy_produced", 7050.0)), disabled=True)
    energy_consumption = st.number_input('Energy consumption (kWh/year)', value=float(st.session_state.get("energy_consumption", 0.0)), step=100.0, min_value=0.0)
    
    deduced_energy = st.number_input('Deduced energy (kWh/year)', energy_consumption - energy_produced, disabled=True)
    
    utile_surface = st.number_input('Utile surface (m²)', value=float(st.session_state.get("utile_surface", 0.0)))
    
    if st.button('Show scores'):
        if energy_consumption <= 0:
            st.error('⚠️ The energy consumption should be greater than 0.')
            return
        
        if utile_surface <= 0:
            st.error('⚠️ The utile surface should be greater than 0.')
            return
        
        show_energy_scores(energy_consumption, deduced_energy, utile_surface)
        show_emission_scores(energy_produced, energy_consumption, utile_surface)
        show_decarbonization_rate(energy_produced, energy_consumption, deduced_energy, utile_surface)
    
    
def show_energy_scores(energy_consumption, deduced_energy, utile_surface):
    surface_usage_ratio = 0.7
    energy_conversion_coefficient = 2.3
    
    primary_energy_no_pv = (energy_consumption * energy_conversion_coefficient) / (surface_usage_ratio * utile_surface)
    primary_energy_with_pv = (deduced_energy * energy_conversion_coefficient) / (surface_usage_ratio * utile_surface)
    
    draw_energy_score_diagram(primary_energy_no_pv, primary_energy_with_pv)
    
    
def draw_energy_score_diagram(primary_energy_no_pv, primary_energy_with_pv):
    scores = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    values = [50, 90, 150, 230, 330, 450, 590, 750, 800]
    colors = ['#00B050', '#92D050', '#FFFF00', '#FFC000', '#FF9900', '#FF0000', '#C00000', '#A6A6A6', '#000000']
    
    energy_efficiency_dict = {score: value for score, value in zip(scores, values)}
    no_pv_score, _ = get_energy_score(primary_energy_no_pv)
    with_pv_score, _ = get_energy_score(primary_energy_with_pv)
    
    fig = go.Figure()
    arrow_head = 3
    arrow_length = 30
    arrow_offset = 10
    arrow_color = 'white'
    text_offset = 20
    
    for score, value, color in zip(scores[::-1], values[::-1], colors[::-1]):
        fig.add_trace(go.Bar(
            y=[score],
            x=[value],
            marker_color=color,
            orientation='h',
            name=f'Range for {score}',
            hoverinfo='none',
            showlegend=False
        ))

    if with_pv_score == no_pv_score:
        fig.add_annotation(
            x=energy_efficiency_dict[no_pv_score] + arrow_offset,
            y=no_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=energy_efficiency_dict[no_pv_score] + arrow_offset + arrow_length + text_offset,
            xanchor='left',
            y=no_pv_score,
            text="Primary Energy with & without PV",
            showarrow=False
        )
    else:
        fig.add_annotation(
            x=energy_efficiency_dict[no_pv_score] + arrow_offset,
            y=no_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=energy_efficiency_dict[no_pv_score] + arrow_offset + arrow_length + text_offset*1.1,
            y=no_pv_score,
            xanchor='left',
            text="Primary Energy without PV",
            showarrow=False
        )
        
        fig.add_annotation(
            x=energy_efficiency_dict[with_pv_score] + arrow_offset,
            y=with_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=energy_efficiency_dict[with_pv_score] + arrow_offset + arrow_length + text_offset,
            y=with_pv_score,
            xanchor='left',
            text="Primary Energy with PV",
            showarrow=False
        )
    
    fig.update_layout(
        title='Energy Performance Scores',
        xaxis_title='Energy Score',
        yaxis_title='Energy Value (kWh/m²/year)',
        barmode='overlay'
    )
    
    st.plotly_chart(fig)
    
    
def get_energy_score(energy_value):
    if energy_value <= 50:
        return 'A', '#00B050'
    elif energy_value <= 90:
        return 'B', '#92D050'
    elif energy_value <= 150:
        return 'C', '#FFFF00'
    elif energy_value <= 230:
        return 'D', '#FFC000'
    elif energy_value <= 330:
        return 'E', '#FF9900'
    elif energy_value <= 450:
        return 'F', '#FF0000'
    elif energy_value <= 590:
        return 'G', '#C00000'
    elif energy_value <= 750:
        return 'H', '#A6A6A6'
    else:
        return 'I', '#000000'
    
    
def show_emission_scores(energy_produced, energy_consumption, utile_surface):
    european_conversion_coefficient = 0.48
    non_renewable_energy_conversion = 0.23
    
    electricity_consumption_in_primary_energy = non_renewable_energy_conversion * energy_consumption
    prevented_quantity_of_co2_emissions = european_conversion_coefficient * energy_produced

    emissions_with_pv = (electricity_consumption_in_primary_energy - prevented_quantity_of_co2_emissions) / (utile_surface * 0.7)
    emissions_no_pv = electricity_consumption_in_primary_energy / (utile_surface * 0.7)
    
    draw_emission_score_diagram(emissions_no_pv, emissions_with_pv)


def draw_emission_score_diagram(emissions_no_pv, emissions_with_pv):
    scores = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    values = [5, 10, 20, 35, 55, 80, 110, 145, 150]
    colors = ['#f7ecfc', '#e2c2ff', '#d7a9f0', '#cc96f4', '#bc6ff8', '#a850e5', '#8919e0', '#A6A6A6', '#000000']
    
    emissions_dict = {score: value for score, value in zip(scores, values)}
    no_pv_score, _ = get_emission_score(emissions_no_pv)
    with_pv_score, _ = get_emission_score(emissions_with_pv)
    
    fig = go.Figure()
    arrow_head = 3
    arrow_length = 30
    arrow_offset = 2
    arrow_color = 'white'
    text_offset = 10
    
    for score, value, color in zip(scores[::-1], values[::-1], colors[::-1]):
        fig.add_trace(go.Bar(
            y=[score],
            x=[value],
            marker_color=color,
            orientation='h',
            name=f'Range for {score}',
            hoverinfo='none',
            showlegend=False
        ))
        
    if with_pv_score == no_pv_score:
        fig.add_annotation(
            x=emissions_dict[no_pv_score] + arrow_offset,
            y=no_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=emissions_dict[no_pv_score] + arrow_offset + text_offset,
            xanchor='left',
            y=no_pv_score,
            text="Emissions with & without PV",
            showarrow=False
        )
    else:
        fig.add_annotation(
            x=emissions_dict[no_pv_score] + arrow_offset,
            y=no_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=emissions_dict[no_pv_score] + arrow_offset + text_offset,
            y=no_pv_score,
            xanchor='left',
            text="Emissions without PV",
            showarrow=False
        )
        
        fig.add_annotation(
            x=emissions_dict[with_pv_score] + arrow_offset,
            y=with_pv_score,
            ax=arrow_length,
            ay=0,
            arrowhead=arrow_head,
            arrowcolor=arrow_color
        )
        
        fig.add_annotation(
            x=emissions_dict[with_pv_score] + arrow_offset + text_offset,
            y=with_pv_score,
            xanchor='left',
            text="Emissions with PV",
            showarrow=False
        )
    
    fig.update_layout(
        title='Emission Performance Scores',
        xaxis_title='Emission Score',
        yaxis_title='Emission Value (kgeqCO2/m²/SU/year)',
        barmode='overlay'
    )
    
    st.plotly_chart(fig)


def get_emission_score(emission_value):
    if emission_value <= 5:
        return 'A', '#f7ecfc'
    elif emission_value <= 10:
        return 'B', '#e2c2ff'
    elif emission_value <= 20:
        return 'C', '#d7a9f0'
    elif emission_value <= 35:
        return 'D', '#cc96f4'
    elif emission_value <= 55:
        return 'E', '#bc6ff8'
    elif emission_value <= 80:
        return 'F', '#a850e5'
    elif emission_value <= 110:
        return 'G', '#8919e0'
    elif emission_value <= 145:
        return 'H', '#A6A6A6'
    else:
        return 'I', '#000000'
    
    
def show_decarbonization_rate(energy_produced, energy_consumption, deduced_energy, utile_surface):
    co2_emission_factor = 0.075
    china_pv_fabrication_factor = 0.043
    
    total_ges_emissions_no_pv = co2_emission_factor * energy_consumption
    total_ges_emissions_with_pv = china_pv_fabrication_factor * energy_produced + co2_emission_factor * deduced_energy
    
    decarbonization_rate = (total_ges_emissions_no_pv - total_ges_emissions_with_pv) / total_ges_emissions_no_pv
    
    st.markdown(f'<div style="background-color: #0e1117; padding: 20px; border-radius: 5px; border: 1px solid white; text-align: center;">'
                    f'<h3 style="color: white;">Decarbonization rate: {decarbonization_rate:.2%}</h3>'
                    f'</div>', unsafe_allow_html=True)
    