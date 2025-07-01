import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
from sklearn.preprocessing import MinMaxScaler
from matplotlib.colors import to_hex
from scipy.signal import find_peaks


st.title("Spectra Cleaner & Visualizer")

# upload csv file
input_file = st.file_uploader("Upload CSV file", type=["csv"])

# user inputs for information about the data
st.write("<h3> File Controls </h3>", unsafe_allow_html = True)
skip_cols = st.number_input("Number of Baseline Trials", value = 2) + 1
st.write("Ex: if number of baseline trials is two there is a 100% baseline and a 0% baseline" )
st.warning("Baseline rows will not be included in normalization")
contains_units = st.checkbox("Contains Unit Row", value = True)

st.write(" <h3> Graph Features </h3> ", unsafe_allow_html = True)
min_wavelength = st.number_input("Minimum wavelength (nm)", value=300)
max_wavelength = st.number_input("Maximum wavelength (nm)", value=800)
x_step = st.number_input("X step (nm)", value = 100, min_value = 1)
interactive = st.toggle("Interactive Plot", value = False) #toggle between matplot and plotly graphs


if input_file:

    filename = input_file.name  
    base_name = os.path.splitext(filename)[0] #remove .csv
    cleaned_filename = f"{base_name}_cleaned.csv" #autocreate cleaned and normilized file names
    normalized_filename = f"{base_name}_normalized.csv"

    #read file
    df = pd.read_csv(input_file, header = None)

    #clean data
    df_clean = df.copy()

    df_clean = df_clean.astype(object)  # convert all columns to object dtype
    df_clean.iloc[0] = df_clean.iloc[0].ffill()
    df_clean.dropna(subset=[df_clean.columns[-2]], inplace = True) #drop rows with NaN in the last column - removed all the descriptive rows
    df_clean.dropna(axis=1, inplace = True) # remove any columns that have null values - incomplete data
    df_clean.columns = range(df_clean.shape[1]) #reset column names after dropping columns
    df_clean.drop(columns= df_clean.columns[(df_clean.columns != 0) & (df_clean.columns % 2 == 0)], inplace = True) #drop even numbered columns (repeats of wavelength)
    df_clean.iat[0, 0] = 'Wavelength (nm)' #set the first cell to be the wavelength column name
    df_clean.columns = df_clean.iloc[0] # set the first row as the column names
    df_clean.drop(index=[0], inplace=True) # drop first duplicate row
   

    df_normalized = df_clean.loc[pd.to_numeric(df_clean.iloc[:, 0], errors='coerce').between(min_wavelength, max_wavelength)]
    df_normalized.reset_index(drop=True, inplace=True) # reset indexes 
    df_normalized.drop(index=[1], inplace=True) 
    scaler = MinMaxScaler()
    df_normalized.iloc[:, skip_cols:] = scaler.fit_transform(df_normalized.iloc[:, skip_cols:])

    #set x and y
    x = pd.to_numeric(df_normalized.iloc[:, 0])
    ys = df_normalized.iloc[:, skip_cols:]

    st.write(" <h3> Graph Visuals </h3> ", unsafe_allow_html = True)

    #select trials to be displayed
    selected_cols = [] 
    with st.expander("Select Trials", expanded = False):
        for col in ys.columns:
            if st.checkbox(col, value=True):  
                selected_cols.append(col)
                
    include_legend = st.checkbox("Include Legend in Plot", value = False) #legend toggle

    if selected_cols:

        #customize colors
        color_mode = st.radio("Color Customization", ["Default", "Colormap", "Custom Pick"], index = 0, horizontal = True)
        color_map = {}

        if color_mode == "Default": #default colors - matplot default 
            default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']  
            for i, col in enumerate(selected_cols):
                color_map[col] = default_colors[i % len(default_colors)]
     
        if color_mode == "Colormap": #use a colormap from matplot
            st.page_link("https://matplotlib.org/stable/users/explain/colors/colormaps.html", label = "View Matplotlib Colormaps", use_container_width = True) #link to colormap options
            cmap_name = st.selectbox("Choose a colormap:", plt.colormaps(), index = 0)
            cmap = plt.get_cmap(cmap_name)
            n = len(selected_cols)
            for i, col in enumerate(selected_cols):
                rgba = cmap(i / max(n - 1, 1))  # Normalize for color spacing
                color_map[col] = to_hex(rgba) #convert to a hex code - for plotly to use

        
        elif color_mode == "Custom Pick": #pick colors individually
            with st.expander("Pick Colors for Each Column", expanded=True):
                for col in selected_cols:
                    color = st.color_picker(f"Color for {col}", value="#000000", key=f"color_{col}",)
                    color_map[col] = color

        if interactive: #plotly interactive graph 
            fig = go.Figure()
           
            for col in ys.columns:
                y = ys[col]
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line=dict(color=color_map.get(col, "#000000")), 
                    name=str(col), 
                    hovertemplate=
                        'Trial: %{text}<br>' +  #control information displayed on hover
                        'Wavelength: %{x} nm<br>' +
                        'Absorbance: %{y}<extra></extra>',
                    text=[col]*len(x)
            ))
                
            fig.update_layout(
            xaxis_title='Wavelength (nm)',
            yaxis_title='Abs',
            xaxis=dict(tickmode='linear', dtick=x_step, range=[x.min(), x.max()]),
            template='plotly_white',
            hovermode='closest' #control what displays upon hover 
            )

            if not include_legend: #legend toggle 
                fig.update_layout(showlegend = False)

            st.plotly_chart(fig, use_container_width=True)

        else: #matplotlib static graph
            fig, ax = plt.subplots(figsize=(10, 6))
            for col in selected_cols:
                ax.plot(x, ys[col], label=str(col), color=color_map.get(col, "#000000"))
            ax.set_xlim(min_wavelength, max_wavelength)
            ax.set_xticks(np.arange(int(min_wavelength), int(max_wavelength)+1, x_step))
            ax.set_xlabel("Wavelength (nm)")
            ax.set_ylabel("Abs")
            if include_legend: #legend toggle
                ax.legend(loc='upper right', fontsize='small')
                
            st.pyplot(fig)
    else:
        st.warning("Please select at least one column to plot.")

    #downloads
    st.write(" <h3> Files </h3> ", unsafe_allow_html = True)
    st.write("If something with the graphs looks wrong please look at the cleaned and normalized files to make sure the data is being proccessed correctly")
    st.download_button("Download Cleaned CSV", df_clean.to_csv(index=False).encode(), file_name=cleaned_filename)
    st.download_button("Download Normalized CSV", df_normalized.to_csv(index=False).encode(), file_name=normalized_filename)
