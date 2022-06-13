import requests
import json
import streamlit as st
import pandas as pd
from datetime import date as dt
import base64
import plotly.express as px
import matplotlib.pyplot as plt

#Cache to speed up webpage when accessing data already read in 

@st.cache
def getLeagues():
    '''
    Connect to API and load info about League name and endpoint input
    '''
    leagueAbb = []
    league = []
    l = requests.get("https://api-football-standings.azharimm.site/leagues/")

    for i in range(len(l.json()['data'])):
        leagueAbb.append(l.json()['data'][i]['id'])
        league.append(l.json()['data'][i]['name'])

    d = {'abb':leagueAbb,'league':league}
    df = pd.DataFrame(data=d)
    return df

@st.cache
def dataLoad(leagues,year):
    '''
    Connect to API and load data into DataFrame
    '''
    df = getLeagues()
    #league code for endpoint
    leagueCode = df[df['league'] == leagues]['abb'].values.tolist()[0]

    #Access API
    r = requests.get("https://api-football-standings.azharimm.site/leagues/{}/standings?season={}&sort=asc".format(leagueCode,year))

    #create list of years to capture data

    r = r.json()['data']

    teams = []
    points =[]
    abb = []
    wins = []
    draws = []
    losses = []
    played = []
    pfor = []
    pagainst = []
    rank = []

    for i in range(len(r['standings'])):
        teams.append(r['standings'][i]['team']['name'])
        points.append(r['standings'][i]['stats'][6]['value'])
        abb.append(r['standings'][i]['team']['abbreviation'])
        wins.append(r['standings'][i]['stats'][0]['value'])
        draws.append(r['standings'][i]['stats'][2]['value'])
        losses.append(r['standings'][i]['stats'][1]['value'])
        played.append(r['standings'][i]['stats'][3]['value'])
        pfor.append(r['standings'][i]['stats'][4]['value'])
        pagainst.append(r['standings'][i]['stats'][5]['value'])
        rank.append(r['standings'][i]['stats'][8]['value'])

    d = {'rank':rank,'Teams':teams, 'Abbreviation':abb,'Points':points, 'Wins':wins,'Draws':draws, 'Losses':losses,'Played':played,'Scored':pfor, 'Conceded':pagainst}
    df = pd.DataFrame(data=d)

    return df, r['seasonDisplay']

#Create Sidebar - all attributes of sidebar will start with st.sidebar
st.sidebar.header('User Input Features')

#SideBar - League Selection
selectedLeague = st.sidebar.selectbox('League',getLeagues()['league'].values.tolist(),5) #default to English Premier League

#Sidebar - Year Selection
yearToday = dt.today().year
selectedYear = st.sidebar.selectbox('Year', list(reversed(range(yearToday - 10,yearToday))))

footballData = dataLoad(selectedLeague, selectedYear)[0]

#Sidebar - Team Selection
uniqueTeam = sorted(footballData.Abbreviation.unique())
selectedTeam = st.sidebar.multiselect('Team', uniqueTeam,uniqueTeam)

#Sidebar - Position Selection
selectedPos = st.sidebar.slider('Position',1,footballData.shape[0],footballData.shape[0])

#Filtering the data
filterFootballData = footballData[(footballData.Abbreviation.isin(selectedTeam)) & (footballData['rank'] <= selectedPos)]

#Page set up

st.title('Football Table Stats Explorer')

st.markdown("""
This app performs simple webscraping of Football standings in various Football leagues across the world
* **Key Python libraries:** pandas, streamlit
* **Data source:** [Football-Standings Github](https://github.com/azharimm/football-standings-api/).
""")
st.write('The below data will be showing information for the {} season'.format(dataLoad(selectedLeague, selectedYear)[1]))


st.dataframe(filterFootballData.set_index('rank'))

#Download data as CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(filterFootballData), unsafe_allow_html=True)

#Button to show graph on click

if st.button('Team ScatterPlot'):
    st.header('Team ScatterPlot')
    #df_selected_team.to_csv('output.csv',index=False)
    #df = pd.read_csv('output.csv')

    fig = px.scatter(filterFootballData, y="Scored", x="Conceded", color = 'Teams', size = 'Points')
    #fig.show()
    st.plotly_chart(fig, use_container_width=True)
    #st.pyplot(fig)