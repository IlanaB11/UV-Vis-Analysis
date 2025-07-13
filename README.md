# UV-Vis-Analysis
[Access Streamlit website](https://uv-vis-analysis-uuozfjbh5atnrzf6lzvzla.streamlit.app/)
or download UV_ana_app.py and run 
```powershell
  streamlit run UV_ana_app.py
```

Upload raw data from UV Spectrometer as a .csv file <br> 
Clean data to remove text descriptions and any unfinished trials <br> 
Plot absorbance vs. wavelength in static (matplotlib) or interactive (plotly) 

## File Controls
Baseline Trials: How many columns of data are excluded from normalization (default 2 for 100% and 0% baselines) <br> 
Contains Unit Rows: Drops the first row containing unit values (default True)<br> 
Wavelength Column Repeats: Drops every other column to remove duplicates (default True) <br> 

It is possible to upload mulitple files as long as they all require the same controls and the same range of wavelengths. 

## Graph Features
Minnimum Wavelength: Lower bound of the x-axis (default 300 nm) <br> 
Maximum Wavelength: Upper bound of the x-axis  (default 800nm) <br> 
X Step: Distance between ticks on the x-axis  (default 100nm)<br> 
Interactive: Toggle between static (matplotlib) and interactive (plotly) graph (default True for interactive graph)

> [!NOTE]
> If something with the graphs looks wrong please look at the cleaned and normalized files to make sure the data is being proccessed correctly

## Graph Visuals
Select Trials: Select which columns of data to display on graph (default all) <br>
Include Legend: Toggle legend display (default False) <br> 
Color Customization
- Default: Use default matplotlib color 
- Colormap: Select a preexisting [Matplotlib color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) 
- Custom: Custom set colors 

> [!NOTE]
> Which trials are selected does not change the normalization

## Peak Selection
Use lasso tool or box tool to select a region of the graph <br> 
Selection results will contain the maximum y value and its x coordinate within the selected region for each line in the region <br> 
Selection results can be downloaded as a .csv file or search for a specific trial

>[!NOTE]
> Shoulders may visually look like peaks but they are not so they are not detected

## Save Peaks
Feature incomplete

## Download Files
### Cleaned File
- Drop text description of data collection method and instrumentation
- Drop unfinished trials 
- Forward fill missing column headers
- Renames first column to Wavelength (nm) and drops every other column (repeating the wavelength values) 

> [!WARNING]
> If the spectrometer did not come to a stop on its own then the trial may be dropped

### Normalized File
- Restricted between minnimum wavelength and maximum wavelength
- Values (excluding baselines as specificed by dropped trials) are normalized 
- Remove row containing unit labels 

> [!WARNING]
> If data does not contain unit labels (or contains them somewhere else) this may drop the first row of data

### About Project
I made this as a tool to help me with my UV Vis Analysis while doing research for a 6 week period over the summer. Any consistent errors my data or variation with how the UV-Vis Spectometer I used (INSERT BRAND AND MODEL) worked compared to others may affect the effectivness of this processing. It by no means works perfectly (and it is not really meant to since it is just a tool I made for myself) but please use it as you see fit. <br> <br> 

Made to process data collected from Agilent Cary 60 UV-Vis by the program Cary WinUV Scan Application version 5.1.3.1042



