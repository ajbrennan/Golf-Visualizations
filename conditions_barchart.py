import pandas as pd
import numpy as np

import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
from plotly.graph_objs import *
from data import data_merge

# Load and clean data
df = data_merge()

# Renaming columns so they appear cleaner on the heatmaps
df = df.rename(columns={"temperature":"Temperature", "wind_speed":"Wind Speed", "course_rating":"Course Rating", "course_yards":"Course Length", "greens_type":"Greens Grass Type"})


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

###### Could add filter for active golfers here ######

'''
Function to take weather condition and course information inputs and set the correct
condition label that is to be used in the bar chart
'''
def condition_input(condition,bins,labels):
    bins = bins[1:]
    x = False
    while x == False:
        for i in range(0,len(bins)):
            if condition <= bins[i]:
                label = labels[i]
                x = True
                break
        if x == False:
            label = 'invalid'
            x = True
    return label

'''
Input the weather and course information in the first argument of the function
Just type out the greens type, it does not need to be run since it is a string
'''
rd_temp = condition_input(85,temp_bins,temp_labels)
rd_wind = condition_input(7,wind_bins,wind_labels)
rd_rating = condition_input(75.8,rating_bins,rating_labels)
rd_length = condition_input(7221,length_bins,length_labels)
rd_greens = 'Bent Grass'

# Concatenates condition and description for better labeling appearence on the plot
con_temp = 'Temperature: ' + rd_temp
con_wind = 'Wind Speed: ' + rd_wind
con_rating = 'Course Rating: ' + rd_rating
con_length = 'Course Length: ' + rd_length
con_greens = 'Greens Grass Type: ' + rd_greens
cols = ['Golfer',con_temp,con_wind,con_rating,con_length,con_greens,'Avg Strokes Gained','Rounds Played']

'''
Data frame set up, this data frame can be used to find which golfers are the biggest 
overperformers and underperformers for each condition
'''
SG_conditions = pd.DataFrame(columns=cols)
SG_conditions['Golfer'] = golfers
SG_conditions.index = golfers
SG_conditions = SG_conditions.iloc[:,1:]

'''
Calculates difference between each player's overall average strokes gained and their
strokes gained in the given weather conditions and course characteristics
For example, if John Smith averages 1.5 strokes gained per round and 0.7 when the
temperature is above 80F, he underperforms his average by 0.8 strokes gained per round
This template can be used for other metrics by swapping out instances of 'Strokes Gained'
with the relevant metric
'''
for i in golfers:
    x = df.loc[df['golfer'] == i]
    a = x.loc[x['Temperature']==rd_temp]
    b = x.loc[x['Wind Speed']==rd_wind]
    c = x.loc[x['Course Rating']==rd_rating]
    d = x.loc[x['Course Length']==rd_length]
    e = x.loc[x['Greens Grass Type']==rd_greens]
    # Calculated each cell using the mean of all observations, median or others could be used
    if len(a) > 2:
        SG_conditions.loc[i,con_temp] = round(a["Strokes Gained"].mean() - x["Strokes Gained"].mean(),2)
    if len(b) > 2:
        SG_conditions.loc[i,con_wind] = round(b["Strokes Gained"].mean() - x["Strokes Gained"].mean(),2)
    if len(c) > 2:
        SG_conditions.loc[i,con_rating] = round(c["Strokes Gained"].mean() - x["Strokes Gained"].mean(),2)
    if len(d) > 2:
        SG_conditions.loc[i,con_length] = round(d["Strokes Gained"].mean() - x["Strokes Gained"].mean(),2)
    if len(e) > 2:
        SG_conditions.loc[i,con_greens] = round(e["Strokes Gained"].mean() - x["Strokes Gained"].mean(),2)
    SG_conditions['Avg Strokes Gained'][i] = round(x["Strokes Gained"].mean(),2)
    SG_conditions['Rounds Played'][i] = len(x)
SG_conditions = SG_conditions[SG_conditions['Rounds Played'] >= 6]

# Filtering for individual golfer stats and preprocessing to format it for the bar plot
########## Manually set golfer analyzed in the bar chart ##########
golfer = 'Bubba Watson'
player_conditions = SG_conditions.loc[SG_conditions.index==golfer]
player_conditions = player_conditions.T
player_conditions.index.name = 'Condition'
player_conditions.reset_index(inplace=True)
player_conditions.columns.values[1] = 'Strokes Gained'

# Bar plot
fig = px.bar(player_conditions[0:5],
             labels=dict(x='Condition', y='Difference in Strokes Gained from Average', color='Strokes Gained'),
             title=golfer+"'s Strokes Gained Compared to His Average",x='Condition',y='Strokes Gained')
fig.add_hline(y=0,
              annotation_text=golfer+"'s Average Strokes Gained: "+str(player_conditions['Strokes Gained'][5]), 
              annotation_position="top right")
plot(fig)




############ Alternate Version with the 0 set to 0 strokes gained############

# SG_conditions = pd.DataFrame(columns=cols)
# SG_conditions['Golfer'] = golfers
# SG_conditions.index = golfers
# SG_conditions = SG_conditions.iloc[:,1:]
# drop_list = []
# for i in golfers:
#     x = df.loc[df['golfer'] == i]
#     a = x.loc[x['Temperature']==rd_temp]
#     b = x.loc[x['Wind Speed']==rd_wind]
#     c = x.loc[x['Course Rating']==rd_rating]
#     d = x.loc[x['Course Length']==rd_length]
#     e = x.loc[x['Greens Grass Type']==rd_greens]
#     # Calculated each cell using the mean of all observations, median or others could be used
#     if len(a) > 2:
#         SG_conditions.loc[i,con_temp] = round(a["Strokes Gained"].mean(),2)
#     if len(b) > 2:
#         SG_conditions.loc[i,con_wind] = round(b["Strokes Gained"].mean(),2)
#     if len(c) > 2:
#         SG_conditions.loc[i,con_rating] = round(c["Strokes Gained"].mean(),2)
#     if len(d) > 2:
#         SG_conditions.loc[i,con_length] = round(d["Strokes Gained"].mean(),2)
#     if len(e) > 2:
#         SG_conditions.loc[i,con_greens] = round(e["Strokes Gained"].mean(),2)
#     SG_conditions['Avg Strokes Gained'][i] = round(x["Strokes Gained"].mean(),2)
#     SG_conditions['Rounds Played'][i] = len(x)
# SG_conditions = SG_conditions[SG_conditions['Rounds Played'] >= 6]

# golfer = 'Max Homa'
# player_conditions = SG_conditions.loc[SG_conditions.index==golfer]
# player_conditions = player_conditions.T
# player_conditions.index.name = 'Condition'
# player_conditions.reset_index(inplace=True)
# player_conditions.columns.values[1] = 'Strokes Gained'

# fig = px.bar(player_conditions[0:5],
#              labels=dict(x='Condition', y='Strokes Gained', color='Strokes Gained'),
#              title=golfer,x='Condition',y='Strokes Gained')
# fig.add_hline(y=player_conditions['Strokes Gained'][5],
#               annotation_text=golfer+"'s Average Strokes Gained: "+str(player_conditions['Strokes Gained'][5], 
#               annotation_position="bottom right")
# fig.add_hline(y=0, line_dash="dot",
#               annotation_text="PGA Average", 
#               annotation_position="bottom right")
# plot(fig)

