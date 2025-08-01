import streamlit as st #for running the website
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import plotly.graph_objects as go
import io #for inline graphing
import base64 #for inline graphing
import matplotlib.font_manager as fm #fonts
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
            "Save Peak": False, 
            #"Color": color_map.get(line_name, "#000000") #add line color - not currently supported by streamlit unless I want to generate a bunch of images
        })

    return pd.DataFrame(max_points) #return values as a dataframe

def create_peak_plot_base64(x, y, peak_x, peak_y, color="#000000"): #create an image of the graphs to display on selection
    fig, ax = plt.subplots(figsize=(2, 1))
    ax.plot(x, y, color=color, linewidth=1) #plot the line
    ax.scatter(peak_x, peak_y, color="black", zorder=5, s=10) #add point for the peak
    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO() #save as image
    plt.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode()}" #return image directions

#session value checks: 
#if 'wavelength_len' in st.session_state:
    #del st.session_state['wavelength_len']

if "saved_peaks" not in st.session_state: #if results have not already been saved
    st.session_state.saved_peaks = pd.DataFrame(columns=["Trial", "Max Wavelength (nm)", "Max Absorbance", "Peak"]) #create a dataframe to save them to

st.title("UV Vis Spectra Cleaner & Visualizer")

# upload csv files
input_files = st.file_uploader("Upload CSV file", type=["csv"], accept_multiple_files = True)

# user inputs for information about the data
st.divider()
with st.expander("Data Handling & Upload Options", expanded=True):
    use_raw_files = st.checkbox("Upload pre-cleaned file (Skip Cleaning Step)", value=False)
    #st.write("<h3> File Controls </h3>", unsafe_allow_html = True)
    skip_cols = st.number_input("Number of Baseline Trials", value = 2) + 1#number of columns skipped
    st.write("Ex: if number of baseline trials is two there is a 100% baseline and a 0% baseline" )
    st.warning("Baseline Columns will not be included in normalization")
    contains_units = st.checkbox("Contains Unit Row", value = True) #if the row needs to be dropped
    repeats_wavelength = st.checkbox("Wavelength Column Repeats For Each Trial", value = True)

st.divider()
with st.expander("Graphing Options", expanded=True):
    #st.write(" <h3> Graph Features </h3> ", unsafe_allow_html = True)
    min_wavelength = st.number_input("Minimum wavelength (nm)", value=300) #wavelength range
    max_wavelength = st.number_input("Maximum wavelength (nm)", value=1000) + 1
    x_step = st.number_input("X step (nm)", value = 100, min_value = 1) #x ticks
    line_weight = st.slider("Lineweight", value = 0.75, min_value = 0.25, max_value = 5.0, step = 0.25) #line thickness
    available_fonts = sorted(set(f.name for f in fm.fontManager.ttflist)) #load fonts into a list
    selected_font = st.selectbox("Choose plot font (Non interactive only)", available_fonts, index=available_fonts.index("DejaVu Sans") if "DejaVu Sans" in available_fonts else 0) #allow font selection
    include_legend = st.checkbox("Include Legend in Plot", value = False) #legend toggle
    interactive = st.toggle("Interactive Plot", value = True) #toggle between matplot and plotly graphs
st.divider() 

if input_files:
    combined_clean = []

    for input_file in input_files:
        filename = input_file.name  
        #base_name = os.path.splitext(filename)[0] #remove .csv
        #cleaned_filename = f"{base_name}_cleaned.csv" #autocreate cleaned and normilized file names
        #normalized_filename = f"{base_name}_normalized.csv"

        df = pd.read_csv(input_file, header = None) #read file
        df_clean = df.copy()
        df_clean = df_clean.astype(object)  # convert all columns to object dtype

        if not use_raw_files:

            #clean data
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
        combined_clean.append(pd.concat([df_clean.iloc[:, 0], df_clean.iloc[:, skip_cols:]], axis=1)) #wavelength and non_baseline columns

    #merge on wavelength column
    df_clean_comb = df_clean.iloc[: , :skip_cols] #start with wavelengths and baseline - from last file uploaded
    for i in range(0, len(combined_clean)): #add the data from each file
        df_clean_comb = df_clean_comb.merge(combined_clean[i], on='Wavelength (nm)', how='outer')

    df_clean_comb["Wavelength (nm)"] = pd.to_numeric(df_clean_comb["Wavelength (nm)"], errors='coerce') #make sure all wavelengths are numeric
    df_clean_comb.sort_values(by='Wavelength (nm)', ascending=True, inplace=True) #sort values

    if len(input_files) > 1:
        st.warning(
            f"The baseline used in the final dataset is taken from the file: **'{input_files[-1].name}'**.\n\n"
            "If different files have different baselines, this may not reflect the actual baseline conditions for all data."
        ) #baseline warning
    
    #select specific columns
    selected_cols = [] 
    with st.expander("Select Trials", expanded = False):
        for col in df_clean_comb.columns[skip_cols:]:
            if st.checkbox(col, value=True):  
                selected_cols.append(col)
    
    #add option to only normalize selected columns
    normalize_select = st.checkbox("Only normalize selected columns", value = False)
    scaler = MinMaxScaler()

    #normalize 
    df_normalized = df_clean_comb.loc[pd.to_numeric(df_clean_comb.iloc[:, 0], errors='coerce').between(min_wavelength, max_wavelength, inclusive="both")] #make sure everything is a number
    df_normalized.reset_index(drop=True, inplace=True) # reset indexes 
    if contains_units: 
        df_normalized.drop(index=[1], inplace=True) #drop unit row 
    if normalize_select: #only normalize selected column
         normalize_cols = [col for col in selected_cols if col in df_normalized.columns and df_normalized.columns.get_loc(col) >= skip_cols]
         df_normalized.loc[:, normalize_cols] = scaler.fit_transform(
            df_normalized[normalize_cols].values.flatten().reshape(-1, 1)
            ).reshape(df_normalized[normalize_cols].shape)
    else: #normalize everything
        df_normalized.iloc[:, skip_cols:] = scaler.fit_transform(
                df_normalized.iloc[:, skip_cols:].values.flatten().reshape(-1, 1) #flatten dataframe to scale on the same level
                ).reshape(df_normalized.iloc[:, skip_cols:].shape) #reshape it back to the dataframe

    #set x and y
    x = pd.to_numeric(df_normalized.iloc[:, 0])
    ys = df_normalized.iloc[:, skip_cols:]

    st.divider()            
   
    plot_cols = [col for col in selected_cols if col in ys.columns] #transfer selected columns to new dict for plotting

    if plot_cols:
        #customize colors
        if "color_map" not in st.session_state: # set up color map if it doesn't already exist in the session
            st.session_state.color_map = {}

        color_mode = st.radio("Color Customization", ["Default", "Colormap", "Custom Pick"], index = 0, horizontal = True)
        color_map = st.session_state.color_map #set to session copy

        if color_mode == "Default": #default colors - matplot default 
            default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            for i, col in enumerate(plot_cols):
                color_map[col] = default_colors[i % len(default_colors)]
     
        if color_mode == "Colormap": #use a colormap from matplot
            st.page_link("https://matplotlib.org/stable/users/explain/colors/colormaps.html", label = "View Matplotlib Colormaps", use_container_width = True) #link to colormap options
            cmap_name = st.selectbox("Choose a colormap:", plt.colormaps(), index = 0)
            cmap = plt.get_cmap(cmap_name)
            n = len(plot_cols)
            for i, col in enumerate(plot_cols):
                rgba = cmap(i / max(n - 1, 1))  # Normalize for color spacing
                color_map[col] = to_hex(rgba) #convert to a hex code - for plotly to use

        
        if color_mode == "Custom Pick":
            with st.expander("Pick Colors for Each Column", expanded=True):
                for col in plot_cols: # Use pre-computed color_map value as the default
                    color = st.color_picker(
                                f"Color for {col}",
                                value=color_map.get(col, "#000000"), 
                                key=f"color_{col}"
                                )
                    color_map[col] = color  # overwrite with user-selected color

        st.divider()

        if interactive: #plotly interactive graph 
            st.write("Drop and drop select a region of peaks")
            fig = go.Figure()
           
            for col in plot_cols: #plot each column 
                y = ys[col]
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='markers+lines',
                    line=dict(color=color_map.get(col, "#000000"), width = 0.75), 
                    name=str(col),
                    text=[col]*len(x), 
                    hovertemplate=
                        'Trial: %{text}<br>' +  #control information displayed on hover for each line
                        'Wavelength: %{x} nm<br>' +
                        'Absorbance: %{y}<extra></extra>',
                    marker = dict(size = 0, opacity = 0),  # hide markers but they can still be selected 
                    connectgaps=True,  # connect over NaNs caused by merge
            ))
                
            fig.update_layout(
            xaxis_title='Wavelength (nm)',
            yaxis_title='Abs',
            yaxis = dict(range = [0,1.05]),
            xaxis=dict(tickmode='linear', dtick=x_step, range=[x.min(), x.max() + 1]),
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

                    #add a graph of each line with the peak marked
                    plots = []
                    for _, row in max_vals.iterrows():
                        if row["Trial"] in ys.columns: #create a plot for each line
                            y_data = ys[row["Trial"]]
                            plot_md = create_peak_plot_base64( #use function to make an image
                                x, y_data,
                                row["Max Wavelength (nm)"],
                                row["Max Absorbance"],
                                color=color_map.get(row["Trial"], "#000000") #using line color
                            )
                            plots.append(plot_md) #append to list
                        else:
                            plots.append("")
                    
                    max_vals["Peak"] = plots #add to dataframe

                    #peak selection 
                    edited_peaks = st.data_editor(max_vals, num_rows="fixed", key="peak_editor", 
                                                  column_config={
                                                                "Trial": st.column_config.TextColumn(disabled=True), #can't change trial number (random index)
                                                                "Max Wavelength (nm)": st.column_config.NumberColumn(disabled=True), #can't change value
                                                                "Max Absorbance": st.column_config.NumberColumn(disabled=True), #can't change value
                                                                "Save Peak": st.column_config.CheckboxColumn(disabled=False), #allow checkbox toggling
                                                                "Peak": st.column_config.ImageColumn()
                                                                }) 
                    for _, row in edited_peaks.iterrows():
                        if row["Save Peak"]: #add peaks where button has been pushed
                            if not ((st.session_state.saved_peaks["Trial"] == row["Trial"]) & (st.session_state.saved_peaks["Max Wavelength (nm)"] == row["Max Wavelength (nm)"])).any(): #remove repeats
                                st.session_state.saved_peaks = pd.concat([st.session_state.saved_peaks, pd.DataFrame([row.drop("Save Peak")])], ignore_index=True) # add to saved dataframe without button row

                st.divider()
                st.subheader("Saved Peaks")
                st.dataframe(st.session_state.saved_peaks,  column_config = {"Peak": st.column_config.ImageColumn()})

                if st.button("Clear Saved Peaks: FIXME"): #clear button: FIXME
                    st.session_state.saved_peaks = pd.DataFrame(columns=["Trial", "Max Wavelength (nm)", "Max Absorbance", "Peak"]) #reset the dataframe
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            for col in plot_cols: #plot each column on the same axis 
                y = ys[col].astype(float).interpolate(method='linear', limit_direction='both') #interpolate to ignore NaN values from merge
                ax.plot(x, y, label=str(col), color=color_map.get(col, "#000000"), lw=0.75 )
            ax.set_xlim(min_wavelength, max_wavelength)
            ax.set_ylim(0,1)
            ax.set_xticks(np.arange(int(min_wavelength), int(max_wavelength)+1, x_step))
            ax.set_xlabel("Wavelength (nm)", fontname = selected_font)
            ax.set_ylabel("Abs", fontname = selected_font)
            ax.spines['top']. set_visible(False)
            ax.spines['right']. set_visible(False)
            if include_legend: #legend toggle
                ax.legend(loc='upper right', fontsize='small')
                
            st.pyplot(fig)
    else:
        st.warning("Please select at least one column to plot.")

    #downloads
    st.divider()
    st.write(" <h3> Files </h3> ", unsafe_allow_html = True)
    st.write("If something with the graphs looks wrong please look at the cleaned and normalized files to make sure the data is being proccessed correctly")
    filename = st.text_input("What would you like to name your files?", value = "File Name") #set filename

    st.download_button("Download Cleaned CSV", df_clean_comb.to_csv(index=False).encode(), file_name= filename + ".csv") #download cleaned file 
    st.download_button("Download Normalized CSV", df_normalized.to_csv(index=False).encode(), file_name= filename + ".csv") #download normalized file

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
    <br>
    <sub> This site was made with help from ChatGPT and Claude.ai </sub>
    """,
    unsafe_allow_html=True
)
