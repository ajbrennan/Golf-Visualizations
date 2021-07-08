import pandas as pd
import numpy as np

import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly as py
import plotly.graph_objs as go

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
golfer = 'Justin Thomas'
golfer_df = df.loc[df['golfer'] == golfer]

########## Manually set the 2 conditions used in the heat map ##########
collabels = length_labels
colname = 'Course Length'
rowlabels = wind_labels
rowname = 'Wind Speed'
# temp_labels
# 'Temperature'
# wind_labels
# 'Wind Speed'
# rating_labels
# 'Course Rating'
# length_labels
# 'Course Length'
# greens_labels
# 'Greens Grass Type'

'''
Create the pandas dataframes to hold the data for the heatmaps
More heat maps can be created by following the same template, shots gained, birdies gained,
and bogeys avoided are what we feel are the most relavent to daily fantasy sports
'''
SG_map = pd.DataFrame(index=rowlabels, columns=collabels)
bird_map = pd.DataFrame(index=rowlabels, columns=collabels)
bogey_map = pd.DataFrame(index=rowlabels, columns=collabels)
# Count of how many rounds have been played for each heat map cell
rd_count = pd.DataFrame(index=rowlabels, columns=collabels)

for i in range(0,len(collabels)):
    for j in range(0,len(rowlabels)):
        x = golfer_df
        # Filter for the each heat map cell
        x = x.loc[x[colname]==collabels[i]]
        x = x.loc[x[rowname]==rowlabels[j]]
        rd_count[collabels[i]][rowlabels[j]] = len(x)
        '''
        Calculated each cell of the heat map using the mean of all observations, median
        or others could be used, additionally all heat map cells that don't have at least 
        3 rounds of data are left empty to avoid bad/great performance bias
        '''
        if len(x) >= 3:    
            SG_map[collabels[i]][rowlabels[j]] = round(x["Strokes Gained"].mean(),2)
            bird_map[collabels[i]][rowlabels[j]] = round(x["Birdies Gained"].mean(),2)
            bogey_map[collabels[i]][rowlabels[j]] = round(x["Bogeys Avoided"].mean(),2)

# Overall golfer averages
SG_average = round(golfer_df["Strokes Gained"].mean(),2)
BG_average = round(golfer_df["Birdies Gained"].mean(),2)
BA_average = round(golfer_df["Bogeys Avoided"].mean(),2)
rounds_played = len(golfer_df)

# Strokes Gained plot
map_title = 'Strokes Gained'
SG_fig = px.imshow(SG_map,
                labels=dict(x=colname, y=rowname, color=map_title),
                title=golfer+"'s "+map_title,x=collabels,y=rowlabels,
                color_continuous_scale=["red", "white", "green"],color_continuous_midpoint=SG_average
                )
SG_fig.update_xaxes(side="top")
SG_fig.update_traces(hovertemplate = colname+': %{x} <br>'+rowname+': %{y} <br>'+
                     map_title+': %{z} <br>'+golfer+"'s average: "+str(SG_average))
plot(SG_fig)

# Birdies Gained plot
map_title = 'Birdies Gained'
bird_fig = px.imshow(bird_map,
                labels=dict(x=colname, y=rowname, color=map_title),
                title=golfer+"'s "+map_title,x=collabels,y=rowlabels,
                color_continuous_scale=["red", "white", "green"],color_continuous_midpoint=BG_average
                )
bird_fig.update_xaxes(side="top")
bird_fig.update_traces(hovertemplate = colname+': %{x} <br>'+rowname+': %{y} <br>'+
                       map_title+': %{z} <br>'+golfer+"'s average: "+str(BG_average))
plot(bird_fig)

# Bogeys Avoided plot
map_title = 'Bogeys Avoided'
bogey_fig = px.imshow(bogey_map,
                labels=dict(x=colname, y=rowname, color=map_title),
                title=golfer+"'s "+map_title,x=collabels,y=rowlabels,
                color_continuous_scale=["red", "white", "green"],color_continuous_midpoint=BA_average
                )
bogey_fig.update_xaxes(side="top")
bogey_fig.update_traces(hovertemplate = colname+': %{x} <br>'+rowname+': %{y} <br>'+
                        map_title+': %{z} <br>'+golfer+"'s average: "+str(BA_average))
plot(bogey_fig)


