import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import Race, DataPoint

def init_dashboard(server):
    """Inizializza e integra la dashboard Dash con l'app Flask"""
    
    # Creazione dell'app Dash
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=[dbc.themes.DARKLY]  # Tema scuro per Dash
    )
    
    # Layout della dashboard
    dash_app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("SpeedChart Dashboard", className="text-center mb-4"),
                html.Div([
                    dcc.Dropdown(
                        id='race-selector',
                        placeholder='Seleziona una corsa',
                        className="mb-3"
                    )
                ])
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='speed-distance-graph',
                    config={'displayModeBar': True},
                    className="mb-4"
                )
            ], width=8),
            
            dbc.Col([
                html.Div([
                    html.H4("Dati", className="mb-3"),
                    html.Div(id='data-table-container', style={'height': '500px', 'overflow-y': 'auto'})
                ])
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Dettagli punto selezionato", className="mb-3"),
                    html.Div(id='selected-point-details', className="p-3 border rounded")
                ])
            ])
        ]),
        
        # Store per i dati della corsa selezionata (invisibile all'utente)
        dcc.Store(id='race-data-store'),
        dcc.Store(id='selected-point-store')
    ], className="container-fluid py-4")
    
    # Callback per popolare il dropdown delle corse
    @dash_app.callback(
        Output('race-selector', 'options'),
        Input('race-selector', 'search_value')
    )
    def update_race_options(search_value):
        # Ottieni le corse dal database
        with server.app_context():
            races = Race.query.order_by(Race.date.desc()).all()
            options = [
                {
                    'label': f"{race.name} - {race.date.strftime('%d/%m/%Y')} - {race.driver}",
                    'value': race.id
                } for race in races
            ]
        return options
    
    # Callback per caricare i dati della corsa selezionata
    @dash_app.callback(
        Output('race-data-store', 'data'),
        Input('race-selector', 'value')
    )
    def load_race_data(race_id):
        if not race_id:
            return None
            
        # Carica i dati della corsa dal database
        with server.app_context():
            race = Race.query.get(race_id)
            data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
            
            race_info = {
                'id': race.id,
                'name': race.name,
                'date': race.date.strftime('%d/%m/%Y %H:%M'),
                'driver': race.driver,
                'vehicle': race.vehicle,
                'notes': race.notes
            }
            
            points_data = [
                {
                    'id': point.id,
                    'distance': point.distance,
                    'speed': point.speed,
                    'acceleration': point.acceleration,
                    'time': point.time
                } for point in data_points
            ]
            
        return {'race': race_info, 'data_points': points_data}
    
    # Callback per aggiornare il grafico e la tabella
    @dash_app.callback(
        [
            Output('speed-distance-graph', 'figure'),
            Output('data-table-container', 'children')
        ],
        [Input('race-data-store', 'data')]
    )
    def update_graph_and_table(data):
        if not data or not data['data_points']:
            return {}, html.Div("Nessun dato disponibile")
            
        # Crea un DataFrame dai punti dati
        df = pd.DataFrame(data['data_points'])
        
        # Crea il grafico velocità/distanza
        fig = px.line(
            df, 
            x='distance', 
            y='speed', 
            title=f"{data['race']['name']} - Velocità/Distanza",
            labels={'distance': 'Distanza (m)', 'speed': 'Velocità (km/h)'},
            markers=True
        )
        
        fig.update_layout(
            hovermode='closest',
            xaxis=dict(
                title='Distanza (m)', 
                title_font=dict(size=14, color="#E5E7EB"),
                tickfont=dict(color="#9CA3AF"),
                gridcolor='rgba(255,255,255,0.1)',
                zeroline=False
            ),
            yaxis=dict(
                title='Velocità (km/h)', 
                title_font=dict(size=14, color="#E5E7EB"),
                tickfont=dict(color="#9CA3AF"),
                gridcolor='rgba(255,255,255,0.1)',
                zeroline=False
            ),
            plot_bgcolor='#1E293B',  # Blu scuro
            paper_bgcolor='#1E293B',  # Blu scuro
            font=dict(color="#E5E7EB"),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        # Crea la tabella dei dati
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Distanza (m)"),
                    html.Th("Velocità (km/h)")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(f"{point['distance']:.2f}"),
                    html.Td(f"{point['speed']:.2f}")
                ], id=f"row-{i}", className="data-row") 
                for i, point in enumerate(data['data_points'])
            ])
        ], bordered=True, hover=True, responsive=True, id="data-table", className="table-dark")
        
        return fig, table
    
    # Callback per gestire i click sul grafico
    @dash_app.callback(
        [
            Output('selected-point-store', 'data'),
            Output('selected-point-details', 'children')
        ],
        [
            Input('speed-distance-graph', 'clickData'),
            Input('data-table-container', 'n_clicks')
        ],
        [
            dash.dependencies.State('race-data-store', 'data'),
            dash.dependencies.State('data-table-container', 'active_cell')
        ]
    )
    def handle_selection(clickData, table_clicks, race_data, active_cell):
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if not race_data or not race_data['data_points']:
            return None, "Nessun punto selezionato"
            
        selected_point = None
        
        if trigger_id == 'speed-distance-graph' and clickData:
            # Gestisci click sul grafico
            clicked_x = clickData['points'][0]['x']
            
            # Trova il punto dati più vicino alla coordinata x cliccata
            distances = [point['distance'] for point in race_data['data_points']]
            closest_idx = min(range(len(distances)), key=lambda i: abs(distances[i] - clicked_x))
            selected_point = race_data['data_points'][closest_idx]
            
        elif trigger_id == 'data-table-container' and active_cell:
            # Gestisci click sulla tabella
            row_idx = active_cell['row']
            if 0 <= row_idx < len(race_data['data_points']):
                selected_point = race_data['data_points'][row_idx]
        
        if selected_point:
            # Dettagli del punto selezionato
            details = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P(f"Distanza: {selected_point['distance']:.2f} m", className="mb-1"),
                        html.P(f"Velocità: {selected_point['speed']:.2f} km/h", className="mb-1")
                    ], width=4),
                    dbc.Col([
                        html.P(f"Accelerazione: {selected_point['acceleration']:.2f} m/s²", className="mb-1"),
                        html.P(f"Tempo: {selected_point['time']:.2f} s", className="mb-1")
                    ], width=4),
                    dbc.Col([
                        html.P(f"Accelerazione media: {calculate_avg_acceleration(race_data['data_points'], selected_point):.2f} m/s²", className="mb-1")
                    ], width=4)
                ])
            ])
            
            return selected_point, details
        
        return None, "Nessun punto selezionato"
    
    # Funzione di utilità per calcolare l'accelerazione media
    def calculate_avg_acceleration(data_points, selected_point):
        # Trova l'indice del punto selezionato
        selected_idx = next(
            (i for i, point in enumerate(data_points) 
             if point['distance'] == selected_point['distance'] and point['speed'] == selected_point['speed']), 
            0
        )
        
        # Calcola l'accelerazione media da inizio corsa fino a questo punto
        if selected_idx > 0:
            start_speed = 0  # Assume velocità iniziale zero
            end_speed = selected_point['speed'] / 3.6  # Converti in m/s
            time = selected_point['time']
            
            if time > 0:
                return (end_speed - start_speed) / time
        
        return 0.0
    
    # Aggiungi JavaScript per gestire il click sulla tabella e evidenziare la riga
    dash_app._inline_scripts.append("""
    document.addEventListener('DOMContentLoaded', function() {
        // Click su riga tabella
        document.addEventListener('click', function(e) {
            if (e.target.closest('#data-table tbody tr')) {
                // Rimuovi classe active da tutte le righe
                document.querySelectorAll('#data-table tbody tr').forEach(row => {
                    row.classList.remove('table-active');
                });
                
                // Aggiungi classe active alla riga cliccata
                e.target.closest('tr').classList.add('table-active');
                
                // Scorri alla riga nella tabella
                e.target.closest('tr').scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        });
    });
    """)
    
    return dash_app.server