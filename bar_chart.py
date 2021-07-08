import pandas as pd
import numpy as np
from bokeh.io import show, output_file
from bokeh.plotting import curdoc, figure, show
from bokeh.layouts import column, row
from bokeh.models import Select, ColumnDataSource, Span, Label
from bokeh.models.formatters import String, List
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_predict
from math import sqrt

from data import data_merge

# function to create columndatasource from dataframe
def get_dataset(src, name, metric):
    df = src[src.golfer == name].copy()
    df['metric'] = df[metric]
    df.reset_index(drop=True, inplace=True)
    
    return ColumnDataSource(data=df)

'''
K fold cross validation using KNN to build a model that with 
correlation filtering finds where the RMSE is at it's lowest.
Providing the features associated with the lowest RMSE that users
can choose from that are the best predictors for player performance
'''
def features(df):
    df = df
    var_list = df.var()[df.var()>2].drop('rnd_id').index.tolist()
    working_df = df[var_list]
    working_df = working_df.drop(columns='strokes').dropna(axis='columns')
    X = working_df.drop(columns='score')
    y = working_df['score']
    cv = KFold(n_splits=10, shuffle=False)
    classifier_pipeline = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=10))
    y_pred = cross_val_predict(classifier_pipeline, X, y, cv=cv)
    
    corr_filter = pd.DataFrame()

    values = [0.2, 0.4, 0.6, 0.7, 0.8]
    for value in values:
        features = abs(working_df.corr()["score"][abs(working_df.corr()["score"])>value].drop('score')).index.tolist()
        X = working_df.drop(columns='score')
        X=X[features]
    
        y_pred = cross_val_predict(classifier_pipeline, X, y, cv=cv)
        rmse = str(round(sqrt(mean_squared_error(y,y_pred)),2))
        r_squared = str(round(r2_score(y,y_pred),2))
        corr_filter = corr_filter.append({"Features": features, "RMSE": rmse, "R Squared": r_squared},
                                     ignore_index = True)
    
    selected_features = corr_filter[corr_filter['RMSE']==corr_filter['RMSE'].min()]
    selected_features = list(selected_features['Features'])
    
    return selected_features[0]


def make_plot(source):
    TOOLTIPS = [
            ("Tournament", "@trn_nm"),
            ("Course", "@course_nm"),
            ("Round", "@rnd_nm"),
            ("Score", "@score")
            ]
    p = figure(plot_height = 800, plot_width=1600, tooltips=TOOLTIPS)

    p.vbar(x='index', top='metric', width=.5, fill_color = 'lightgreen', source=source)
 
    zero = Span(location=0, line_color='black', line_dash='solid', line_width=0.5)

    p.add_layout(pga_avg)
    p.add_layout(player_avg)
    p.add_layout(zero)
    p.add_layout(pga_label)
    p.add_layout(player_label)
    p.xaxis.visible = False
    p.yaxis.axis_label = metric + ' per Round'
    p.axis.axis_label_text_font_style = 'bold'
    p.title.text = player + " 2019 " + metric + ' per Round'
    p.title.text_font_size = '20pt'
    return p


def update_plot(attrname, old, new):
    player = player_select.value
    metric = metric_select.value
    player_df = df[df.golfer == player_select.value].copy()
    pga_avg.location = df[metric_select.value].mean()
    player_avg.location = player_df[metric_select.value].mean()
    pga_label.y = df[metric_select.value].mean()
    player_label.y = player_df[metric_select.value].mean()
    p.yaxis.axis_label = metric + " per Round"
    p.title.text = player + " 2019 " + metric + " per Round"
    src = get_dataset(df, dict_golfers[player], metric_select.value)
    source.data.update(src.data)


def Convert(lst):
    res_dct = {lst[i]: lst[i] for i in range(0, len(lst), 1)}
    return res_dct


df = data_merge()
df = df.loc[df['tournament_yr'] == 2019]
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df = df.sort_values(by='date')

golfers = sorted(df['golfer'].drop_duplicates())
lst = golfers
dict_golfers = Convert(lst)

player = 'Brooks Koepka'
metric = 'Strokes Gained'
pga_avg = Span(location=df[metric].mean(), line_color='red', line_dash='dashed', line_width=2)
pga_label = Label(x=0, y=(df[metric].mean()), text="PGA Average", level='overlay', text_font_style='bold')
player_df = df[df.golfer == player].copy()
player_avg = Span(location=player_df[metric].mean(), line_color='blue', line_dash='dashed', line_width=1)
player_label = Label(x=0, y=(player_df[metric].mean()), text="This Player's Average", level='overlay', text_font_style='bold')

player_select = Select(value=player, title='Player', options=sorted(dict_golfers.keys()))
metric_select = Select(value=metric, title='Performance Measure', options=sorted(features(df)))

source = get_dataset(df, dict_golfers[player], metric)
p = make_plot(source)

player_select.on_change('value', update_plot)
metric_select.on_change('value', update_plot)

controls = column(player_select, metric_select)

curdoc().add_root(row(p, controls))
curdoc().title = 'Capstone Bar Chart'
