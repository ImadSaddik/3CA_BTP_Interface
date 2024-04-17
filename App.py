import pandas as pd

import streamlit as st
from streamlit_option_menu import option_menu

from tabs.MeteoHub import show_data_form
from tabs.ProductionViewer import show_production


TAB_1 = "Data hub"
TAB_2 = "Production"

def main():
    st.title("BIPV Interactive interface")

    with st.container():
        selected_tab = option_menu(
            menu_title=None,
            options=[TAB_1, TAB_2, "Decarbonization"],
            icons=['house', 'diagram-3','gear', 'clipboard-check'],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"display": "flex", "flex-wrap": "wrap", "padding": "0", "margin": "0", "list-style-type": "none", "max-width": "100%"},
                "nav-item": {"flex": "1 1 auto", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"},
                "nav-link": {"width": "100%", "padding": "8px 0"},
            }
        )

        handle_selected_tab(selected_tab)
        
        
def handle_selected_tab(selected_tab):
    if selected_tab == TAB_1:
        show_data_form()
            
    elif selected_tab == TAB_2:
        show_production()
            
    elif selected_tab == 'Reports':
        pass
    
            
if __name__ == "__main__":
    main()
        