# UV-Vis-Analysis
[Access Streamlit website](https://uv-vis-analysis-uuozfjbh5atnrzf6lzvzla.streamlit.app/)
or download UV_ana_app.py and run 
```powershell
  streamlit run UV_ana_app.py
```

Upload raw data from UV Spectrometer as a .csv file <br> 
Clean data to remove text descriptions and any unfinished trials <br> 
Plot absorbance vs. wavelength in static (matplotlib) or interactive (plotly) 

## User Controls
### Data Handling and Upload
Upload Precleaned File: Upload a cleaned file previously downloaded from the site (default False)
Baseline Trials: How many columns of data are excluded from normalization (default 2 for 100% and 0% baselines) <br> 
Contains Unit Rows: Drops the first row containing unit values (default True)<br> 
Wavelength Column Repeats: Drops every other column to remove duplicates (default True) <br> 

It is possible to upload mulitple files as long as they all require the same controls. 

### Graphing Options
Minnimum Wavelength: Lower bound of the x-axis (default 300 nm) <br> 
Maximum Wavelength: Upper bound of the x-axis  (default 1000nm) <br> 
X Step: Distance between ticks on the x-axis  (default 100nm)<br> 
Include Legend: Toggle legend display (default False) <br> 
Interactive: Toggle between static (matplotlib) and interactive (plotly) graph (default True for interactive graph)

> [!NOTE]
> If something with the graphs looks wrong please look at the cleaned and normalized files to make sure the data is being proccessed correctly

### Graph Visuals
Select Trials: Select which columns of data to display on graph (default all) <br>
Only Normalize Selected Columns: Only normalizes data on display on the graph (default False)

Color Customization
- Default: Use default matplotlib color 
- Colormap: Select a preexisting [Matplotlib color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) 
- Custom: Custom set colors

### Peak Selection
Use lasso tool or box tool to select a region of the graph <br> 
Selection results will contain the maximum y value and its x coordinate within the selected region for each line in the region <br> 
Selection results can be downloaded as a .csv file or search for a specific trial

### Save Peaks
Feature incomplete

### Download Files
Cleaned File
- Drop text description of data collection method and instrumentation
- Drop unfinished trials 
- Forward fill missing column headers
- Renames first column to Wavelength (nm) and drops every other column (repeating the wavelength values) 

Normalized File
- Restricted between minnimum wavelength and maximum wavelength
- Values (excluding baselines as specificed by dropped trials) are normalized 
- Remove row containing unit labels

> [!NOTE]
> All columns will be included in the normalized file but if only normalize selected columns is selected then only those columns will be normalized in the file

## Uploading Multiple Files 
Files are merged on the Wavelength column. This can create nulls so use carefully. <br> 
The baseline is taken from the file that was uploaded last. 

## About Project
I made this as a tool to help me with my UV Vis Analysis while doing research for a 6 week period over the summer. Any consistent errors my data or variation with how the UV-Vis Spectometer I used (INSERT BRAND AND MODEL) worked compared to others may affect the effectivness of this processing. It by no means works perfectly (and it is not really meant to since it is just a tool I made for myself) but please use it as you see fit. <br> <br> 

Made to process data collected from Agilent Cary 60 UV-Vis by the program Cary WinUV Scan Application version 5.1.3.1042



