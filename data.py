import pandas as pd
import numpy as np
import os


def data_golf():
    '''
    Looping through folder where all golf data is stored and appening all
    the data together into one single dataframe
    '''
    path = 'data/golf_data'
    files = os.listdir(path)
    files_xlsx = [f for f in files if f[-4:] == 'xlsx']
    golf_data = pd.DataFrame()
    for file in files_xlsx:
        file_data = pd.read_excel(path + '/' + file)
        golf_data = golf_data.append(file_data)
    
    '''
    Dropping on course_id because missing course_id indicates a row of only final
    score, and dropping missing scores because that is no benefit to the data
    '''
    golf_data = golf_data.dropna(subset=['course_id', 'strokes'])
    golf_data = golf_data.rename(columns={"par": "score"})
    #filling missing values to 0 for columns that it works for
    golf_data[['Eagle', 'Birdie', 'Par', 'Bogey']] = golf_data[['Eagle', 'Birdie', 'Par', 'Bogey']].fillna(0)
    
    #we found that this dropped many of the match play tournaments and rounds incomplete
    incomplete_tournaments = golf_data[(golf_data['strokes'] - golf_data['score'] != golf_data['course_par'])].index
    golf_data.drop(incomplete_tournaments, inplace=True)
    
    # list of tournaments
    tournaments = golf_data['trn_id'].drop_duplicates()

    # dataframe to for scoring and birdie avg for each round of each tournament
    avg_df = pd.DataFrame()
    for tournament in tournaments:
        tourney = golf_data.loc[golf_data['trn_id'] == tournament]
        rounds = tourney['rnd_nm'].drop_duplicates()
        for x in rounds:
            tourney_rnd = tourney.loc[tourney['rnd_nm'] == x]
            scor_avg = tourney_rnd['strokes'].mean()
            bird_avg = tourney_rnd['Birdie'].mean()
            bogey_avg = tourney_rnd['Bogey'].mean()
            avg_df = avg_df.append({'trn_id': tournament, 'rnd_nm': x, 'Scoring Average': scor_avg,
                                    'Birdie Average': bird_avg, 'Bogey Average': bogey_avg}, ignore_index=True)

    golf_data = pd.merge(golf_data, avg_df, how='left', left_on=['trn_id', 'rnd_nm'], right_on=['trn_id', 'rnd_nm'])

    # filling missing values in strokes gained with calculation for strokes gained
    golf_data['Strokes Gained'] = golf_data['Strokes Gained'].fillna(golf_data['Scoring Average'] - golf_data['strokes'])
    # creating column for birdies gained
    golf_data['Birdies Gained'] = golf_data['Birdie'] - golf_data['Birdie Average']
    # creating column for bogeys lost
    golf_data['Bogeys Avoided'] = golf_data['Bogey Average'] - golf_data['Bogey']
    
    # cleaning the golfer names to better presentation for the user
    golf_data['golfer'] = golf_data['golfer'].str[:-4]
    golf_data['golfer'] = golf_data['golfer'].str.replace('-', " ")
    golf_data['golfer'] = golf_data['golfer'].str.title()

    return golf_data


weather = pd.read_excel('data/capstone_data - weather.xlsx')
# renaming the tournament_id to match the naming in golf_data
weather = weather.rename(columns={"tournament_id": "trn_id"})


'''
This function is created to format the the date to datetime, 
and then it retrieves the median value for all the weather
metrics for each day since there were multiple times given
for each date of each round
'''
def data_weather():
    weather['date'] = pd.to_datetime(weather['date']).dt.date
    tournaments = weather['trn_id'].drop_duplicates()
    tourney_list = []
    date_list = []
    temperature = []
    humidity = []
    wind_speed = []
    wind_direction = []
    precipitation = []
    dew_point = []

    for x in tournaments:
        tourney = weather.loc[weather['trn_id'] == x]
        dates = tourney['date'].drop_duplicates()
        for date in dates:
            y = tourney.loc[tourney['date'] == date]
            strip_date = date.strftime("%d %b %Y ")
            tourney_list.append(x)
            date_list.append(strip_date)
            temperature.append(y['temperature'].mean())
            humidity.append(y['humidity'].mean())
            wind_speed.append(y['wind_speed'].mean())
            wind_direction.append(y['wind_direction'].mean())
            precipitation.append(y['precipitation'].mean())
            dew_point.append(y['dew_point'].mean())

    weather_data = pd.DataFrame({'trn_id': tourney_list, 'date': date_list, 'temperature': temperature,
                                 'humidity': humidity, 'wind_speed': wind_speed, 'wind_direction': wind_direction,
                                 'precipitation': precipitation, 'dew_point': dew_point})
    weather_data['date'] = pd.to_datetime(weather_data['date'], format='%d %b %Y ')
    weather_data['tournament_yr'] = pd.DatetimeIndex(weather_data['date']).year
    # creating a column for the weekday of the each given date
    weather_data['weekday'] = weather_data['date'].dt.dayofweek
    # weather_data.drop(weather_data[weather_data['weekday'] == 0].index, inplace=True)
    weather_data.drop(weather_data[weather_data['weekday'] == 2].index, inplace=True)

    '''
    This for series of for loops and if statements accounts for matching
    weekdays and round names given some rounds start late and some end late.
    '''
    parts = []
    for tournament in tournaments:
        round_nm_up = weather_data.loc[weather_data['trn_id'] == tournament]
        if 3 not in list(round_nm_up['weekday']):
           conditions = [(weather_data['weekday'] == 4), (weather_data['weekday'] == 5),
            (weather_data['weekday'] == 6), (weather_data['weekday'] == 0)]
           values = ['Round 1', 'Round 2', 'Round 3', 'Round 4']
        else:
            # a list of our conditions for each weekday
            conditions = [(weather_data['weekday'] == 3), (weather_data['weekday'] == 4),
            (weather_data['weekday'] == 5), (weather_data['weekday'] == 6),
            (weather_data['weekday'] == 0)]
            # a list of the values that will be assigned to each condition
            values = ['Round 1', 'Round 2', 'Round 3', 'Round 4', 'Round 4']
        weather_data['rnd_nm'] = np.select(conditions, values)
        round_nm_up = weather_data.loc[weather_data['trn_id'] == tournament]
        round_nm_up['rnd_nm'].drop_duplicates()
        parts.append(round_nm_up)
    weather_data = pd.concat(parts)

    return weather_data

# reading in course dataset, only minor modifications needed to match names to other datasets
courses = pd.read_excel("data/capstone_data - courses.xlsx")
courses = courses.rename(columns={"id": "course_id", "name": "course_nm", "par": "course_par", "yards": "course_yards"})

'''
data_merge functions merges all the data together matching like columns together, 
and then makes the data column a datetime value
'''

def data_merge():
    df = pd.merge(data_golf(), data_weather(), how='left',
                  left_on=['trn_id', 'rnd_nm'], right_on=['trn_id', 'rnd_nm'])
    df = pd.merge(df, courses, how='left', left_on=['course_id', 'course_nm', 'course_par',
                                                    'slope_rating', 'course_rating', 'course_yards'],
                  right_on=['course_id', 'course_nm', 'course_par', 'slope_rating', 'course_rating', 'course_yards'])
    df['date'] = pd.to_datetime(df['date']).dt.date

    return df
