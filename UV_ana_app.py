import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import MinMaxScaler


st.title("Spectra Cleaner & Visualizer")

# upload csv file
input_file = st.file_uploader("Upload CSV file", type=["csv"])

# user inputs for information about the data
base_100 = st.checkbox("Includes 100% baseline column", value = True)
base_0 = st.checkbox("Includes 0% baseline column", value = True)


min_wavelength = st.number_input("Minimum wavelength (nm)", value=300)
max_wavelength = st.number_input("Maximum wavelength (nm)", value=800)
x_step = st.number_input("X-axis step size (nm)", value = 100, min_value = 1)

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
    df_clean.drop(index = [0, 1], inplace = True) # drop the two rows

    #normalize data - exlucde baseline
    skip_cols = 1  # first column = wavelength
    if base_100:
        skip_cols += 1
    if base_0:
        skip_cols += 1

    df_normalized = df_clean.loc[pd.to_numeric(df_clean.iloc[:, 0], errors='coerce').between(min_wavelength, max_wavelength)]
    scaler = MinMaxScaler()
    df_normalized.iloc[:, skip_cols:] = scaler.fit_transform(df_normalized.iloc[:, skip_cols:])

    #plot data
    x = pd.to_numeric(df_normalized.iloc[:, 0])
    ys = df_normalized.iloc[:, skip_cols:]


    #user graph customization
    selected_cols = [] #let user select columns to plot
    with st.expander("Select Trials", expanded = False):
        for col in ys.columns:
            if st.checkbox(col, value=True):  
                selected_cols.append(col)
                
    include_legend = st.checkbox("Include Legend in Plot", value = False)

    if selected_cols:

        #customize colors
        color_mode = st.radio("Color Customization", ["Default", "Colormap", "Custom Pick"], index = 0, horizontal = True)
        color_map = {}

        if color_mode == "Default":
            default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color'] #default colors 
            for i, col in enumerate(selected_cols):
                color_map[col] = default_colors[i % len(default_colors)]
     
        if color_mode == "Colormap": #use a colormap
            st.page_link("https://matplotlib.org/stable/users/explain/colors/colormaps.html)", label = "View Matplotlib Colormaps", use_container_width = True) #link to colormap options
            cmap_name = st.selectbox("Choose a colormap:", plt.colormaps(), index = 0)
            cmap = plt.get_cmap(cmap_name)
            n = len(selected_cols)
            for i, col in enumerate(selected_cols):
                color_map[col] = cmap(i / max(n - 1, 1))  # Normalize for color spacing

        
        elif color_mode == "Custom Pick": #pick colors individually
            with st.expander("Pick Colors for Each Column", expanded=True):
                for col in selected_cols:
                    color = st.color_picker(f"Color for {col}", value="#000000", key=f"color_{col}",)
                    color_map[col] = color

        fig, ax = plt.subplots(figsize=(10, 6))
        for col in selected_cols:
            ax.plot(x, ys[col], label=str(col), color=color_map.get(col, "#000000"))
        ax.set_xlim(min_wavelength, max_wavelength)
        ax.set_xticks(np.arange(int(min_wavelength), int(max_wavelength)+1, x_step))
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Abs")
        if include_legend: 
            ax.legend(loc='upper right', fontsize='small')
        
        st.pyplot(fig)
    else:
        st.warning("Please select at least one column to plot.")

    # --- Step 4: Downloads ---
    st.download_button("Download Cleaned CSV", df_clean.to_csv(index=False).encode(), file_name=cleaned_filename)
    st.download_button("Download Normalized CSV", df_normalized.to_csv(index=False).encode(), file_name=normalized_filename)
