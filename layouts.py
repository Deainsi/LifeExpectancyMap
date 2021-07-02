import json

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import requests

url = requests.get(
    "http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001?filter=COUNTRY:*&format=json&profile=simple")
data = json.loads(url.text)
df = pd.DataFrame(columns=['Sex', 'Year', 'Region', 'Country', 'Value'])
for i in data['fact']:
    data_row = [i['dim']['SEX'], int(i['dim']['YEAR']), i['dim']['REGION'], i['dim']['COUNTRY'], float(i['Value'])]
    df.loc[-1] = data_row
    df.index += 1
df = df.sort_values(['Region', 'Country', 'Year'], ascending=(True, True, True))

df.loc[df['Country'] == 'Iran (Islamic Republic of)', ['Country']] = 'Iran'
df.loc[df['Country'] == 'Venezuela (Bolivarian Republic of)', ['Country']] = 'Venezuela'
df.loc[df['Country'] == 'Micronesia (Federated States of)', ['Country']] = 'Micronesia'

gw = json.load(open("custom.geo.json"))

ccd = {
    'Antigua and Barb.': 'Antigua and Barbuda',
    'Dominican Rep.': 'Dominican Republic',
    'St. Vin. and Gren.': 'Saint Vincent and the Grenadines',
    'United States': 'United States of America',
    'Brunei': 'Brunei Darussalam',
    'Korea': 'Republic of Korea',
    'Lao PD': "Lao People's Democratic Republic",
    'Dem. Rep. Korea': "Democratic People's Republic of Korea",
    'Syria': 'Syrian Arab Republic',
    'Vietnam': 'Viet nam',
    'Central African Rep.': 'Central African Republic',
    "CГґte d'Ivoire": "Côte d'Ivoire",
    'Dem. Rep. Congo': 'Democratic Republic of the Congo',
    'Cape Verde': 'Cabo Verde',
    'Eq. Guinea': 'Equatorial Guinea',
    'S Sudan': 'South Sudan',
    'Somaliland': 'Somalia',
    'SГЈo TomГ© and Principe': 'Sao Tome and Principe',
    'Tanzania': 'United Republic of Tanzania',
    'American Samoa': 'Samoa',
    'Solomon Is.': 'Solomon Islands',
    'Bosnia and Herz.': 'Bosnia and Herzegovina',
    'Czech Rep.': 'Czechia',
    'United Kingdom': 'United Kingdom of Great Britain and Northern Ireland',
    'Moldova': 'Republic of Moldova',
    'Macedonia': 'North Macedonia',
    'Russia': 'Russian Federation',
}

tmp = df.set_index('Country')
found = []
missing = []
countries_geo = []
for country in gw['features']:

    # Country name detection
    country_name = country['properties']['name']

    # Eventual replacement with our transition dictionnary
    country_name = ccd[country_name] if country_name in ccd.keys() else country_name
    go_on = country_name in tmp.index

    # If country is in original dataset or transition dictionnary
    if go_on:

        # Adding country to our "Matched/found" countries
        found.append(country_name)

        # Getting information from both GeoJSON file and dataFrame
        geometry = country['geometry']

        # Adding 'id' information for further match between map and data
        countries_geo.append({
            'type': 'Feature',
            'geometry': geometry,
            'id': country_name
        })

    # Else, adding the country to the missing countries
    else:
        missing.append(country_name)

geo_world_ok = {'type': 'FeatureCollection', 'features': countries_geo}

# Create the log count column
df['Life expectancy'] = df[(df['Year'] == 2019) & (df['Sex'] == 'Both sexes')].Value

# Get the maximum value to cap displayed values
max_l = df['Life expectancy'].max()
max_val = int(max_l) + 1
min_val = 50

# Prepare the range of the colorbar
values = [i for i in range(min_val, max_val)]

fig = px.choropleth_mapbox(
    df,
    geojson=geo_world_ok,
    locations='Country',
    color=df['Life expectancy'],
    color_continuous_scale='blackbody',
    hover_name='Country',
    hover_data={'Year': False, 'Sex': False, 'Year': False, 'Region': False, 'Country': False, 'Value': False},
    mapbox_style='open-street-map',
    zoom=0.7,
    center={'lat': 20, 'lon': 10},
    opacity=0.6,
    range_color=(50, df['Life expectancy'].max())
)

fig.update_layout(
    margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    coloraxis_colorbar={
        'title': 'Life expectancy',
        'tickvals': values[::10],
        'ticktext': values[::10]
    }
)

layout = html.Div([
    html.Header([
        html.Div([dcc.Dropdown(id="dropdown",
                               options=[{'label': i, 'value': i} for i in df['Country'].unique()],
                               style={'width': '100%'})
                  ], style={'width': '50%'})],

        style={'backgroundColor': 'gray',
               'display': 'flex',
               'alignItems': 'stretch',
               'justifyContent': 'center',
               'position': 'fixed',
               'zIndex': '1',
               'width': '100%'
               }),
    html.Div([
        dcc.Graph(id="LEM", figure=fig),
        dcc.Graph(id='YD',
                  figure={"layout": {
                      "yaxis": {'zeroline': False,
                                'showgrid': False,
                                'title': 'Life expectancy'},
                      "xaxis": {'zeroline': False,
                                'showgrid': False,
                                'title': 'Year'},
                      "plot_bgcolor": "#afd3de"}})],
        style={'display': 'flex',
               'flex-direction': 'row',
               'flex-wrap': 'wrap',
               'align-content': 'center',
               'justify-content': 'center',
               'align-items': 'center',
               'paddingTop': '50px'})])
