# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Para 'ALL', mostramos el total de lanzamientos exitosos POR SITIO
        # 1. Filtramos el DataFrame para obtener solo los lanzamientos exitosos (class == 1)
        successful_launches_df = spacex_df[spacex_df['class'] == 1]
        
        # 2. Creamos el gráfico circular usando 'Launch Site' como nombres de las porciones
        fig = px.pie(
            successful_launches_df,
            names='Launch Site',  # Las porciones del gráfico son los sitios de lanzamiento
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Para un sitio específico, mostramos el ratio de éxito vs. fallo
        # 1. Filtramos el DataFrame para el sitio seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # 2. Creamos el gráfico circular usando 'class' (0 o 1) como nombres de las porciones
        fig = px.pie(
            filtered_df,
            names='class',  # Las porciones son los resultados: 0 (fallo) y 1 (éxito)
            title=f'Total Success Launches for site {entered_site}'
        )
        return fig
# Get unique launch sites for the dropdown options
min_value=spacex_df['Payload Mass (kg)'].min()
max_value=spacex_df['Payload Mass (kg)'].max()
launch_sites = spacex_df['Launch Site'].unique()
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        100: '100'},
                                    value=[min_value, max_value]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Decorador de la función que define la entrada (Input) y la salida (Output)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # --- PASOS DE DEPURACIÓN ---
    print(f"Sitio seleccionado: {entered_site}")
    print(f"Rango de carga útil seleccionado: {payload_range}")

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    print(f"Tamaño del DataFrame después de filtrar por carga útil: {len(filtered_df)}")
    # --- FIN DE DEPURACIÓN ---

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlación entre Carga Útil y Resultado de la Misión para Todos los Sitios'
        )
    else:
        specific_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # --- PASO DE DEPURACIÓN ADICIONAL ---
        print(f"Tamaño del DataFrame después de filtrar por sitio '{entered_site}': {len(specific_site_df)}")
        # --- FIN DE DEPURACIÓN ---
        fig = px.scatter(
            specific_site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlación entre Carga Útil y Resultado de la Misión para el Sitio {entered_site}'
        )

    fig.update_layout(transition_duration=500)
    return fig
# Run the app
if __name__ == '__main__':
    app.run()
