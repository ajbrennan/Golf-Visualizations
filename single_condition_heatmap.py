import pandas as pd
import numpy as np

import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff

from data import data_merge

# Load and clean data
df = data_merge()

# Renaming columns so they appear cleaner on the heatmaps
df = df.rename(columns={
    "temperature":"Temperature",
    "wind_speed":"Wind Speed",
    "course_rating":"Course Rating",
    "course_yards":"Course Length",
    "greens_type":"Greens Grass Type"})

'''
Creating the bins for each condition, the bins and labels can be changed by editing
the ranges in xxx_bins and xxx_labels
'''

# Create temperature groups
temp_bins=[0,59.9,69.9,79.9,150]
temp_labels=["<60F","60-69F","70-79F",">80F"]
df['Temperature']=pd.cut(df['Temperature'],bins=temp_bins,labels=temp_labels)

# Create wind speed groups
wind_bins=[0,4.9,9.9,100]
wind_labels=["0-4.99 mph","5-9.99 mph",">10 mph"]
df['Wind Speed']=pd.cut(df['Wind Speed'],bins=wind_bins,labels=wind_labels)

# Create course rating groups
rating_bins=[0,73.9,74.9,75.9,100]
rating_labels=["70.0-73.9","74.0-74.9","75.0-75.9","76.0-80.0"]
df['Course Rating']=pd.cut(df['Course Rating'],bins=rating_bins,labels=rating_labels)

# Create course length groups
length_bins=[0,7099,7199,7299,7399,10000]
length_labels=["6800-7099 yds","7100-7199 yds","7200-7299 yds","7300-7399 yds","7400-7700 yds"]
df['Course Length']=pd.cut(df['Course Length'],bins=length_bins,labels=length_labels)

# Rename grass types based on their main type
df.loc[df['Greens Grass Type']=='Crenshaw Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='Penn A1 Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='Penncross Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='Bent Grass (007/Tyee Blend)','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='A4 Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='L-93 Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='V-8 Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='T-1 Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='Pennlinks Bent Grass','Greens Grass Type']='Bent Grass'
df.loc[df['Greens Grass Type']=='Bent Grass (poa)','Greens Grass Type']='Bent Grass'

df.loc[df['Greens Grass Type']=='TifEagle 419 Bermuda Grass (w/ Zoysia)','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='TifEagle Bermuda Grass','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='Champion Bermuda Grass','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='Tidwarf Bermuda Grass','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='Champion Ultradwarf Bermuda Grass','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='MiniVerde Bermuda Grass','Greens Grass Type']='Bermuda Grass'
df.loc[df['Greens Grass Type']=='TifSport Bermuda Grass','Greens Grass Type']='Bermuda Grass'

df.loc[df['Greens Grass Type']=='Seashore Paspalum Grass','Greens Grass Type']='Paspalum'
df.loc[df['Greens Grass Type']=='Paspalum SeaIsle','Greens Grass Type']='Paspalum'
df.loc[df['Greens Grass Type']=='Paspalum Supreme','Greens Grass Type']='Paspalum'

# Create greens groups (excluded rye grass as there is very little data)
greens_labels=["Bent Grass","Bermuda Grass","Poa Annua","Paspalum"]


# Array of all golfers
golfers = sorted(df['golfer'].drop_duplicates())
########## Manually set golfer analyzed in the heat maps ##########
golfer = 'Brooks Koepka'
golfer_df = df.loc[df['golfer'] == golfer]

########## Manually set the condition used in the heat map ##########
rowlabels = temp_labels
rowname = 'Temperature'
# rowlabels = wind_labels
# rowname = 'Wind Speed'
# rowlabels = rating_labels
# rowname = 'Course Rating'
# rowlabels = length_labels
# rowname = 'Course Length'
# rowlabels = greens_labels
# rowname = 'Greens Grass Type'

collabels=['Strokes Gained','Birdies Gained','Bogeys Avoided','Average Driving Distance']


# Create the pandas dataframes to hold the data for the heatmaps
heatmap = pd.DataFrame(index=rowlabels, columns=collabels)
for i in collabels:
    for j in range(0,len(rowlabels)):
        x = golfer_df
        # Filter for the each heat map cell
        x = x.loc[x[rowname]==rowlabels[j]]
        # Calculated each cell using the mean of all observations, median or others could be used
        heatmap[i][rowlabels[j]] = round(x[i].mean(),2)
# Calculate metric averages and rounds played
heatmap.loc['Averages'] = [round(golfer_df["Strokes Gained"].mean(),2),
                           round(golfer_df["Birdies Gained"].mean(),2),
                           round(golfer_df["Bogeys Avoided"].mean(),2),
                           round(golfer_df["Average Driving Distance"].mean(),2)]
rounds_played = len(golfer_df)

scaled = (heatmap - heatmap.iloc[-1]) / (heatmap.max() - heatmap.min())

'''
Flip the datasets because otherwise the data will display upside down in plotly and
convert dataframes to numpy arrays so the data will work in figure factory
'''
heatmap = heatmap.iloc[::-1]
heatmap_np = heatmap.values
scaled = scaled.iloc[::-1]
scaled_np = scaled.values

# Heat map
fig = ff.create_annotated_heatmap(scaled_np,x=collabels,y=list(heatmap.index),
                                  annotation_text=heatmap_np, 
                                  colorscale=["red", "white", "green"],zmid=0,zmin=-1,zmax=1,
                                  hoverinfo='skip')
fig.update_layout(title_text=golfer+"'s Performance")
fig['layout']['xaxis']['tickfont']['size'] = 15
fig['layout']['yaxis']['tickfont']['size'] = 15
fig['layout']['font']['size'] = 20
plot(fig)

