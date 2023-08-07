# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 10:39:53 2023

@author: get39559
"""

#--- REQUIREMENTS ---

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px



#--- PROCESS DATA AREA ---

file_path = "230704_Standorte.xlsx"
df = pd.read_excel(file_path, usecols=["Standortnummer", "Typ", "Lat", "Lon", "m?gliche CH4 in kW", "Punktzahl gesamt", "Potenzial"])
df.columns = ["Location number", "Technology", "lat", "lon", "possible methanation capacity in kW", "Evaluation Points", "Hydrogen Potential"]
df['Evaluation Points'] = df['Evaluation Points'].round(2)


#Einteilung in Gruppen nach Leistung
conditions2 = [
    df['possible methanation capacity in kW'] < 100,
    (df['possible methanation capacity in kW'] >= 100) & (df['possible methanation capacity in kW'] < 500),
    (df['possible methanation capacity in kW'] >= 500) & (df['possible methanation capacity in kW'] <= 1000),
    df['possible methanation capacity in kW'] > 1000
]
choices2 = [0, 1, 2, 3]
df['Group'] = np.select(conditions2, choices2)


#Einteilung in Gruppen nach Punktzahl
conditions3 = [
    df['Evaluation Points'] < 5.7,
    (df['Evaluation Points'] >= 5.7) & (df['Evaluation Points'] < 5.9),
    (df['Evaluation Points'] >= 5.9) & (df['Evaluation Points'] < 6),
    df['Evaluation Points'] >= 6
]
choices3 = [1, 2, 3, 4]
choices4 = ['rgb(255,0,0)','rgb(255,165,0)','rgb(255,255,0)','rgb(0,128,0)']
df['Group_Points'] = np.select(conditions3, choices3)
df['Colour'] = np.select(conditions3, choices4)


def set_size_based_on_capacity(input_df, size):
    """
    Fügt eine neue Spalte "size" im DataFrame ein, basierend auf den Werten in der Spalte "possible methanation capacity in kW".

    Parameter:
        input_df (pandas.DataFrame): Der DataFrame, dem die Spalte "size" hinzugefügt werden soll.

    Rückgabe:
        None (Die Funktion ändert den DataFrame direkt.)
    """
    #Zuordnung der size
    conditions = [
        input_df['Group'] < 2,
        input_df['Group'] == 2,
        input_df['Group'] > 2
    ]

    choices = [(size), (size*3), (size*6)]

    input_df['size'] = np.select(conditions, choices)
    
    return input_df
    
    
    
    

def load_map(input_df, size, map_style):

    #input_df['size'] = 5
    result_df = set_size_based_on_capacity(input_df, size)
    
    if not result_df.empty:
        fig = px.scatter_mapbox(
            input_df,
            lat="lat",
            lon="lon",
            #mapbox_style="stamen-terrain",
            mapbox_style=map_style,
            color="Colour",  # Farbinformation aus dem DataFrame verwenden
            color_discrete_map={
                "rgb(255,0,0)": "rgb(255,0,0)",      # Rot
                "rgb(255,165,0)": "rgb(255,165,0)",  # Orange
                "rgb(255,255,0)": "rgb(255,255,0)",  # Gelb
                "rgb(0,128,0)": "rgb(0,128,0)" },     # Grün
            size="size",
            size_max=size*6,
            zoom=5,
            height=1000,
            hover_data=hover_data,
            hover_name="Technology",
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("Sorry, no data to display. Please adjust your filters.")



### __________________________________________________________________________________________________________________________________________
### STREAMLIT

#--- SETUP WEBSITE CONFIG ---
st.set_page_config(page_title="Methanation potential Germany", page_icon=":factory:", layout="wide", initial_sidebar_state = "collapsed" )


tab1, tab2, tab3 = st.tabs(["Introduction", "Visualisation", "Documentation"])

with tab1:
    
    #--- HEADER SECTION ---
    st.markdown('<div style="background-color: white; padding: 4px;"><h2 style="color: #5B5B5B;">Biological methanation potential with German waste gases</h2></div>', unsafe_allow_html=True)
    #st.write("")


    #--- DESCRIPTION SECTION ---
    #st.subheader('Introduction')
    st.write("The [ORBIT II](https://orbit-projekt.de/) research project is concerned with the conversion of carbon dioxide and hydrogeno methane by means of biological methanation. ")
    st.latex('$$\text{CO}_2 + 4\text{H}_2 \rightarrow \text{CH}_4 + 2\text{H}_2\text{O}$$')
    st.write("""The focus is on the storage of electricity from renewable sources in the form of methane
             Different industries and technologies are considered as potential CO2 sources and their synergies with biological methanation are evaluated.
             For this purpose, different waste and sewage gases, especially from bioethanol production, biogas plants with and without upgrading, cement plants,
             wastewater treatment plants and landfills are tested. ORBIT II aims to integrate power-to-gas plants, optimize system integration and reduce costs.
             In addition, the use of biogenic waste materials as educt gases for methanation is being advanced.
             To this end, a site assessment was conducted for these technologies and industries.
             Each site received a score consisting of a technology type score and a regional score.
             The technology type score was based on waste gas composition, steadiness of waste gas availability, and other criteria.
             The regional assessment was performed at the county level through survey analysis regarding the energy transition.
             
             ➡ More about the rating you will find in the tab documentation.
             """)
        
    st.subheader('Map description')
    st.write(
        """
        The results of the evaluation are shown on a map of germany. The map shows the potential methanation capacities and their score of various industrial sites in germany.
        
        Each point represents an industry/technology location. The size of the points is based on the potential methanation capacity.  The point scale is divided into four groups, which are colored red, orange, yellow and green to indicate how suitable a location is.

        ➡ Click in the Tab 'Visualisation' to open the Map
        """)
        #st.write("Learn more about the project [ORBIT II](https://orbit-projekt.de/).")




with tab2:
    #st.markdown('<div style="background-color: #69B73D; padding: 2px;">', unsafe_allow_html=True)
    col1, col2 = st.columns([6,2])
    
    
    #--- MAP FILTER ---
    with col2:
        
        st.subheader("Data Adjustments")
        industry_type = st.selectbox(
        "Technology Type",
        np.insert(df.Technology.unique(), 0, "All",))
        CH4_min, CH4_max = st.slider(
           "Range of possible methanation capacity in Groups", 0, 3, (1, 3), step=1, help="0: <100 kW, 1: 100-500 kW,  2: 500-1000 kW, 3: > 1000 kW \n (A methanation capacity lower than 100 kW is not economical due to the number of full load hours)")
        
        
        st.subheader("Evaluation Adjustments")
        st.write("Filter the displayed locations by the score. This can be done either in groups or individually with the slider.")



        st.subheader("Map Adjustments")  
        size = st.slider(
        "Size of the dots", 0.5, 3.0, (1.0), step=0.5, help="Pick a size")
        map_style=st.selectbox("Background Mapstyle", {"carto-positron","carto-darkmatter"})
    
        
        
    #--- MAP SECTION --
    with col1:
        #st.write("Click on a colour to remove the Group")
     
        with st.container():
            #hover data sind die die angezeigt werden beim darüber fahren mit der maus
            hover_data = {'Technology': False,
                          'possible methanation capacity in kW' : True,
                          'Evaluation Points' : True  ,
                          'lat': True,
                          'lon': True,
                          'size' : False,
                          'Colour': False
                          }
            
            
            df_mima = df.query("`Group` >= @CH4_min and `Group` <= @CH4_max")
            
            if industry_type == "All":
                load_map(df_mima, size, map_style)
            
            
            else: #filtern mit der query methode
                df1 = df_mima.query("Technology == @industry_type")
                load_map(df1, size, map_style)
                
                
                
with tab3:
    #st.markdown('<div style="background-color: #69B73D; padding: 2px;">', unsafe_allow_html=True)
    st.subheader('Documentation')
    for i in range(0,10):
        st.write("Hier wird Daniels Werbung stehen.")
    st.write("Hier wird Daniel Werbung stehlen.")



st.write("")
st.write("")
st.markdown('<div style="background-color: #69B73D; padding: 2px;">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([6,1,2])
with col1:
    st.write("")
    st.text('Forschungsstelle für Energiespeicher und Energienetze (FENES)')
    st.text('OTH Regensburg')
    #st.write("[ORBIT II](https://orbit-projekt.de/)")
with col2:
    st.image("https://www.fenes.net/wp-content/uploads/2021/12/2021_12_01_Logo_ORBIT-II_quadratisch.svg")
with col3:
    st.write("")
    st.image("https://gerotor.tech/wp-content/uploads/2018/03/Fenes-Logo-300x103.png")