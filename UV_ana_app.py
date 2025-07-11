import streamlit as st #for running the website
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import plotly.graph_objects as go
import os #for file names 
from sklearn.preprocessing import MinMaxScaler #for normalization 
from matplotlib.colors import to_hex #for color customization 
from collections import defaultdict #to prevent key error in find_max function

#functions
def find_max(selection, fig): 
    """Return a dictionary of the line and the x and y coordinates of the peak from a selected range on a plotly figure"""
    grouped_points = defaultdict(list) #prevent key error 

    for point in selection['points']: #group points by line
        curve_num = point['curve_number']
        grouped_points[curve_num].append(point)

    max_points = []

    for curve_num, points in grouped_points.items(): #find the max in each group
        line_name = fig.data[curve_num].name #get the trial name from the figure
        max_point = max(points, key=lambda p: p['y']) #find point with highest y-value and its coordinate x-value

        max_points.append({
            "Trial": line_name,
            "Max Wavelength (nm)": max_point['x'],
            "Max Absorbance": max_point['y'],
            "Save Peak": False #Will this display and should I make it a seperate dict of the same length instead? 
        })

    return pd.DataFrame(max_points) #return values as a dataframe

#session value checks: 
if 'wavelength_len' in st.session_state:
    del st.session_state['wavelength_len']

st.title("UV Vis Spectra Cleaner & Visualizer")

# upload csv files
input_files = st.file_uploader("Upload CSV file", type=["csv"], accept_multiple_files = True)

# user inputs for information about the data
st.write("<h3> File Controls </h3>", unsafe_allow_html = True)
skip_cols = st.number_input("Number of Baseline Trials", value = 2) + 1 #number of columns skipped
st.write("Ex: if number of baseline trials is two there is a 100% baseline and a 0% baseline" )
st.warning("Baseline Columns will not be included in normalization")
contains_units = st.checkbox("Contains Unit Row", value = True) #if the row needs to be dropped
repeats_wavelength = st.checkbox("Wavelength Column Repeats For Each Trial", value = True)

st.write(" <h3> Graph Features </h3> ", unsafe_allow_html = True)
min_wavelength = st.number_input("Minimum wavelength (nm)", value=300) #wavelength range
max_wavelength = st.number_input("Maximum wavelength (nm)", value=800)
x_step = st.number_input("X step (nm)", value = 100, min_value = 1) #x ticks
interactive = st.toggle("Interactive Plot", value = True) #toggle between matplot and plotly graphs


if input_files:
    combined_clean = []

    for input_file in input_files:
        filename = input_file.name  
        #base_name = os.path.splitext(filename)[0] #remove .csv
        #cleaned_filename = f"{base_name}_cleaned.csv" #autocreate cleaned and normilized file names
        #normalized_filename = f"{base_name}_normalized.csv"

        #read file
        df = pd.read_csv(input_file, header = None)

        #clean data
        df_clean = df.copy()

       
        df_clean = df_clean.astype(object)  # convert all columns to object dtype
        if repeats_wavelength: 
            df_clean.iloc[0] = df_clean.iloc[0].ffill() #forward fill the column names
        df_clean.dropna(subset=[df_clean.columns[-2]], inplace = True) #drop rows with NaN in the last column - removed all the descriptive rows
        df_clean.dropna(axis=1, inplace = True) # remove any columns that have null values - incomplete data
        df_clean.columns = range(df_clean.shape[1]) #reset column names after dropping columns
        if repeats_wavelength: 
            df_clean.drop(columns= df_clean.columns[(df_clean.columns != 0) & (df_clean.columns % 2 == 0)], inplace = True) #drop even numbered columns (repeats of wavelength)
        df_clean.iat[0, 0] = 'Wavelength (nm)' #set the first cell to be the wavelength column name
        df_clean.columns = df_clean.iloc[0] # set the first row as the column names
        df_clean.drop(index=[0], inplace=True) # drop first duplicate row

        #Throw an error if files have different wavelength ranges
        wavelengths = pd.to_numeric(df_clean.iloc[:, 0], errors='coerce')
        wavelengths = wavelengths.dropna() #remove nulls just in case
        file_range = (wavelengths.min(), wavelengths.max()) #wavelength range

        if 'wavelength_range' not in st.session_state: #store as session variable
            st.session_state.wavelength_range = file_range
        else:
            if file_range != st.session_state.wavelength_range:
                st.error(f"File '{filename}' has wavelength range {file_range[0]}–{file_range[1]} nm, which does not match "
                        f"the first file's range of {st.session_state.wavelength_range[0]}–{st.session_state.wavelength_range[1]} nm.")
                st.stop()
        
        combined_clean.append(pd.concat([df_clean.iloc[:, 0], df_clean.iloc[:, skip_cols:]], axis=1)) #wavelength and non_baseline columns

    #merge on wavelength column 
    df_clean_comb = df_clean.iloc[: , :skip_cols] #start with wavelengths and baseline - from last file uploaded
    for i in range(0, len(combined_clean)): #add the data from each file
        df_clean_comb = df_clean_comb.merge(combined_clean[i], on='Wavelength (nm)', how='outer')

    df_clean_comb.sort_values(by='Wavelength (nm)', inplace=True) #sort values

    if len(input_files) > 1:
        st.warning(
            f"The baseline used in the final dataset is taken from the file: **'{input_files[-1].name}'**.\n\n"
            "If different files have different baselines, this may not reflect the actual baseline conditions for all data."
        ) #baseline warning

    #normalize everything on the same scale
    df_normalized = df_clean_comb.loc[pd.to_numeric(df_clean_comb.iloc[:, 0], errors='coerce').between(min_wavelength, max_wavelength)]
    df_normalized.reset_index(drop=True, inplace=True) # reset indexes 
    if contains_units: 
        df_normalized.drop(index=[1], inplace=True) #drop unit row 
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
        if "color_map" not in st.session_state: # set up color map if it doesn't already exist in the session
            st.session_state.color_map = {}

        color_mode = st.radio("Color Customization", ["Default", "Colormap", "Custom Pick"], index = 0, horizontal = True)
        color_map = st.session_state.color_map #set to session copy

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

        
        if color_mode == "Custom Pick":
            with st.expander("Pick Colors for Each Column", expanded=True):
                for col in selected_cols: # Use pre-computed color_map value as the default
                    color = st.color_picker(
                                f"Color for {col}",
                                value=color_map.get(col, "#000000"), 
                                key=f"color_{col}"
                                )
                    color_map[col] = color  # overwrite with user-selected color

        if interactive: #plotly interactive graph 
            st.write("Drop and drop select a region of peaks")
            fig = go.Figure()
           
            for col in selected_cols: #plot each column 
                y = ys[col]
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='markers+lines',
                    line=dict(color=color_map.get(col, "#000000")), 
                    name=str(col), 
                    text=[col]*len(x), 
                    hovertemplate=
                        'Trial: %{text}<br>' +  #control information displayed on hover for each line
                        'Wavelength: %{x} nm<br>' +
                        'Absorbance: %{y}<extra></extra>',
                    marker = dict(size = 2) #small size so the markers can't be seen but they can be selected 
            ))
                
            fig.update_layout(
            xaxis_title='Wavelength (nm)',
            yaxis_title='Abs',
            xaxis=dict(tickmode='linear', dtick=x_step, range=[x.min(), x.max()]),
            template='plotly_white',
            hovermode='closest',   #control what displays upon hover of the overall graph 
            )

            if not include_legend: #legend toggle 
                fig.update_layout(showlegend = False)

            event = st.plotly_chart( #selection happens 
                            fig, 
                            use_container_width=True,
                            on_select="rerun",  # Rerun when selection changes
                            selection_mode=['points', 'box', 'lasso'],  # Enable selection tools
                            key="plotly_chart"
                            )
    
            if 'plotly_chart' in st.session_state and st.session_state.plotly_chart: # if something has been selected
                selection = st.session_state.plotly_chart.get('selection', {}) #what has been selected 

                if selection and 'points' in selection and len(selection['points']) > 0: #if points have been selected 
                    max_vals = find_max(selection, fig) 
                    
                    st.warning("Save Peaks is under construction and currently does not work") #add FIXME warning
                    st.subheader("Selection Results")
                    st.dataframe(max_vals) #a table of the trials and max values 

        else: #matplotlib static graph
            fig, ax = plt.subplots(figsize=(10, 6))
            for col in selected_cols: #plot each column on the same axis 
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
    filename = st.text_input("What would you like to name your files?", placeholder = "File Name") #set filename

    st.download_button("Download Cleaned CSV", df_clean_comb.to_csv(index=False).encode(), file_name= filename + "_cleaned") #download cleaned file 
    st.download_button("Download Normalized CSV", df_normalized.to_csv(index=False).encode(), file_name= filename + "_normalized") #download normalized file

st.markdown( #add a link to the github repo (and the github logo because I wanted to be fancy)
    """
    <hr style='margin-top: 2em;'>
    <small>
        For more information about how the data is processed, 
        see the 
        <a href="https://github.com/IlanaB11/UV-Vis-Analysis/tree/main"> 
            GitHub repository <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
            width="16" style="vertical-align: text-bottom;">
        </a>.
    </small>
    """,
    unsafe_allow_html=True
)
