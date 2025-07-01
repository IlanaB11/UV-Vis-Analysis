# UV-Vis-Analysis
[Access Streamlit website here](https://uv-vis-analysis-uuozfjbh5atnrzf6lzvzla.streamlit.app/)
or download UV_ana_app.py and run 
```powershell
  streamlit run UV_ana_app.py
```

Upload raw data from UV Spectrometer as a .csv file <br> 
Clean data to remove text descriptions and any unfinished trials <br> 
Plot absorbance vs. wavelength in static (matplotlib) or interactive (plotly) 

## File Controls
Dropped Trials: How many columns of data are excluded from normalization <br> 

## Graph Features
Minnimum Wavelength: Lower bound of the x-axis <br> 
Maximum Wavelength: Upper bound of the x-axis <br> 
X Step: Distance between ticks on the x-axis <br> 
Interactive: Toggle between static (matplotlib) and interactive (plotly) graph

> [!NOTE]
> If something with the graphs looks wrong please look at the cleaned and normalized files to make sure the data is being proccessed correctly

## Graph Visuals
Select Trials: Select which columns of data to display on graph
Include Legend: Toggle legend display
Color Customization
<ul> Default: Use default matplotlib color</ul>
<ul> Colormap: Select a preexisting [matplotlib color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html)</ul>
<ul>Custom: Custome set colors </ul>

> [!NOTE]
> Which trials are selected does not change the normalization


## Download Files
### Cleaned File
<ul> Drop text description of data collection method and instrumentation </ul>
<ul> Drop unfinished trials </ul>
<ul> Forward fill missing column headers</ul>
<ul> Renames first column to Wavelength (nm) and drops every other column (repeating the wavelength values) </ul>

> [!WARNING]
> If the spectrometer did not come to a stop on its own then the trial may be dropped

### Normalized File
<ul> Restricted between minnimum wavelength and maximum wavelength</ul>
<ul> Values (excluding baselines as specificed by dropped trials) are normalized </ul>
<ul> Remove row containing unit labels </ul>

> [!WARNING]
> If data does not contain unit labels (or contains them somewhere else) this may drop the first row of data




