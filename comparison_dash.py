import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import Race, DataPoint

def init_comparison_dashboard(server):
    """Inizializza e integra la dashboard di confronto Dash con l'app Flask"""
    
    # Creazione dell'app Dash
    comparison_dash = dash.Dash(
        server=server,
        routes_pathname_prefix='/comparison/',
        external_stylesheets=[dbc.themes.DARKLY]  # Tema scuro per Dash
    )
    
    # Layout della dashboard
    comparison_dash.layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Confronto Prestazioni", className="text-center mb-4"),
                html.Div([
                    html.Div(id='races-info')
                ])
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='comparison-graph',
                    config={'displayModeBar': True},
                    className="mb-4"
                )
            ], width=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Dati Corsa 1", className="mb-3"),
                    html.Div(id='data-table1-container', style={'height': '400px', 'overflow-y': 'auto'})
                ])
            ], width=6),
            
            dbc.Col([
                html.Div([
                    html.H4("Dati Corsa 2", className="mb-3"),
                    html.Div(id='data-table2-container', style={'height': '400px', 'overflow-y': 'auto'})
                ])
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Dettagli punto selezionato - Corsa 1", className="mb-3"),
                    html.Div(id='selected-point1-details', className="p-3 border rounded")
                ])
            ], width=6),
            
            dbc.Col([
                html.Div([
                    html.H4("Dettagli punto selezionato - Corsa 2", className="mb-3"),
                    html.Div(id='selected-point2-details', className="p-3 border rounded")
                ])
            ], width=6)
        ]),
        
        # Store per i dati delle corse selezionate (invisibile all'utente)
        dcc.Store(id='race1-data-store'),
        dcc.Store(id='race2-data-store'),
        dcc.Store(id='selected-point1-store'),
        dcc.Store(id='selected-point2-store')
    ], className="container-fluid py-4 dark-theme")
    
    # Callback per caricare i dati della prima corsa selezionata
    @comparison_dash.callback(
        Output('race1-data-store', 'data'),
        Input('_dash-global-callback-arguments', 'value'),  # Callback all'avvio
        dash.dependencies.State('race1-data-store', 'id')  # dummy state per compatibilità
    )
    def load_race1_data(_1, _2):
        # Ottieni l'ID della corsa 1 dalle query params
        race1_id = None
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return None
            
        try:
            # Ottieni l'ID della corsa dalla URL
            from dash import no_update
            from flask import request
            if request:
                race1_id = request.args.get('race1_id')
        except:
            return None
            
        if not race1_id:
            return None
            
        # Carica i dati della corsa dal database
        with server.app_context():
            race = Race.query.get(race1_id)
            if not race:
                return None
                
            data_points = DataPoint.query.filter_by(race_id=race1_id).order_by(DataPoint.distance).all()
            
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
    
    # Callback per caricare i dati della seconda corsa selezionata
    @comparison_dash.callback(
        Output('race2-data-store', 'data'),
        Input('_dash-global-callback-arguments', 'value'),  # Callback all'avvio
        dash.dependencies.State('race2-data-store', 'id')  # dummy state per compatibilità
    )
    def load_race2_data(_1, _2):
        # Ottieni l'ID della corsa 2 dalle query params
        race2_id = None
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return None
            
        try:
            # Ottieni l'ID della corsa dalla URL
            from dash import no_update
            from flask import request
            if request:
                race2_id = request.args.get('race2_id')
        except:
            return None
            
        if not race2_id:
            return None
            
        # Carica i dati della corsa dal database
        with server.app_context():
            race = Race.query.get(race2_id)
            if not race:
                return None
                
            data_points = DataPoint.query.filter_by(race_id=race2_id).order_by(DataPoint.distance).all()
            
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
    
    # Callback per mostrare le informazioni sulle corse
    @comparison_dash.callback(
        Output('races-info', 'children'),
        [Input('race1-data-store', 'data'),
         Input('race2-data-store', 'data')]
    )
    def update_races_info(race1_data, race2_data):
        if not race1_data or not race2_data:
            return html.Div("Caricamento dati in corso...")
            
        race1_info = race1_data['race']
        race2_info = race2_data['race']
        
        return html.Div([
            html.Div([
                html.Span(f"Confronto tra ", className="text-muted"),
                html.Span(f"{race1_info['name']}", style={"color": "#3B82F6"}),
                html.Span(" e ", className="text-muted"),
                html.Span(f"{race2_info['name']}", style={"color": "#10B981"})
            ], className="h5 mb-3 text-center")
        ])
    
    # Callback per aggiornare il grafico di confronto
    @comparison_dash.callback(
        Output('comparison-graph', 'figure'),
        [Input('race1-data-store', 'data'),
         Input('race2-data-store', 'data')]
    )
    def update_comparison_graph(race1_data, race2_data):
        if not race1_data or not race2_data:
            return {}
            
        # Crea DataFrames dai punti dati
        df1 = pd.DataFrame(race1_data['data_points'])
        df2 = pd.DataFrame(race2_data['data_points'])
        
        # Crea il grafico con due serie
        fig = go.Figure()
        
        # Aggiungi la prima serie (corsa 1)
        fig.add_trace(go.Scatter(
            x=df1['distance'],
            y=df1['speed'],
            mode='lines+markers',
            name=race1_data['race']['name'],
            line=dict(color='#3B82F6', width=2),  # Blu acceso
            marker=dict(size=6, color='#3B82F6'),
            hovertemplate='<b>Distanza:</b> %{x:.2f} m<br><b>Velocità:</b> %{y:.2f} km/h<extra></extra>'
        ))
        
        # Aggiungi la seconda serie (corsa 2)
        fig.add_trace(go.Scatter(
            x=df2['distance'],
            y=df2['speed'],
            mode='lines+markers',
            name=race2_data['race']['name'],
            line=dict(color='#10B981', width=2),  # Verde acqua
            marker=dict(size=6, color='#10B981'),
            hovertemplate='<b>Distanza:</b> %{x:.2f} m<br><b>Velocità:</b> %{y:.2f} km/h<extra></extra>'
        ))
        
        # Personalizza il layout
        fig.update_layout(
            title="Confronto Velocità/Distanza",
            title_font=dict(size=18, color="#E5E7EB"),
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
            legend=dict(
                bgcolor='rgba(0,0,0,0.2)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                font=dict(color="#E5E7EB")
            ),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        return fig
    
    # Callback per aggiornare le tabelle dei dati
    @comparison_dash.callback(
        [Output('data-table1-container', 'children'),
         Output('data-table2-container', 'children')],
        [Input('race1-data-store', 'data'),
         Input('race2-data-store', 'data')]
    )
    def update_data_tables(race1_data, race2_data):
        if not race1_data or not race2_data:
            return html.Div("Caricamento dati in corso..."), html.Div("Caricamento dati in corso...")
            
        # Crea la tabella per la corsa 1
        table1 = dbc.Table([
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
                ], id=f"row1-{i}", className="data-row1") 
                for i, point in enumerate(race1_data['data_points'])
            ])
        ], bordered=True, hover=True, responsive=True, id="data-table1", className="table-dark")
        
        # Crea la tabella per la corsa 2
        table2 = dbc.Table([
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
                ], id=f"row2-{i}", className="data-row2") 
                for i, point in enumerate(race2_data['data_points'])
            ])
        ], bordered=True, hover=True, responsive=True, id="data-table2", className="table-dark")
        
        return table1, table2
    
    # Callback per gestire i click sul grafico e aggiornare i dettagli dei punti
    @comparison_dash.callback(
        [Output('selected-point1-store', 'data'),
         Output('selected-point2-store', 'data'),
         Output('selected-point1-details', 'children'),
         Output('selected-point2-details', 'children')],
        [Input('comparison-graph', 'clickData')],
        [dash.dependencies.State('race1-data-store', 'data'),
         dash.dependencies.State('race2-data-store', 'data')]
    )
    def handle_graph_click(clickData, race1_data, race2_data):
        if not race1_data or not race2_data or not clickData:
            # Valori di default
            return None, None, "Clicca sul grafico per selezionare un punto", "Clicca sul grafico per selezionare un punto"
        
        # Ottieni il punto cliccato e la curva selezionata
        curve_index = clickData['points'][0]['curveNumber']
        clicked_x = clickData['points'][0]['x']
        
        selected_point1 = None
        selected_point2 = None
        
        # Trova il punto più vicino nella curva selezionata e nell'altra curva
        if curve_index == 0:  # Curva della corsa 1
            # Trova il punto più vicino per la corsa 1
            distances1 = [point['distance'] for point in race1_data['data_points']]
            closest_idx1 = min(range(len(distances1)), key=lambda i: abs(distances1[i] - clicked_x))
            selected_point1 = race1_data['data_points'][closest_idx1]
            
            # Trova il punto corrispondente per la corsa 2 (posizione più vicina)
            distances2 = [point['distance'] for point in race2_data['data_points']]
            if distances2:
                closest_idx2 = min(range(len(distances2)), key=lambda i: abs(distances2[i] - clicked_x))
                selected_point2 = race2_data['data_points'][closest_idx2]
        else:  # Curva della corsa 2
            # Trova il punto più vicino per la corsa 2
            distances2 = [point['distance'] for point in race2_data['data_points']]
            closest_idx2 = min(range(len(distances2)), key=lambda i: abs(distances2[i] - clicked_x))
            selected_point2 = race2_data['data_points'][closest_idx2]
            
            # Trova il punto corrispondente per la corsa 1 (posizione più vicina)
            distances1 = [point['distance'] for point in race1_data['data_points']]
            if distances1:
                closest_idx1 = min(range(len(distances1)), key=lambda i: abs(distances1[i] - clicked_x))
                selected_point1 = race1_data['data_points'][closest_idx1]
        
        # Crea i dettagli per il punto della corsa 1
        if selected_point1:
            details1 = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P(f"Distanza: {selected_point1['distance']:.2f} m", className="mb-1"),
                        html.P(f"Velocità: {selected_point1['speed']:.2f} km/h", className="mb-1")
                    ], width=6),
                    dbc.Col([
                        html.P(f"Accelerazione: {selected_point1['acceleration']:.2f} m/s²", className="mb-1"),
                        html.P(f"Tempo: {selected_point1['time']:.2f} s", className="mb-1"),
                        html.P(f"Accelerazione media: {calculate_avg_acceleration(race1_data['data_points'], selected_point1):.2f} m/s²", className="mb-1")
                    ], width=6)
                ])
            ], style={"border-left": "4px solid #3B82F6"})  # Bordo blu per corsa 1
        else:
            details1 = "Nessun dato disponibile"
        
        # Crea i dettagli per il punto della corsa 2
        if selected_point2:
            details2 = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P(f"Distanza: {selected_point2['distance']:.2f} m", className="mb-1"),
                        html.P(f"Velocità: {selected_point2['speed']:.2f} km/h", className="mb-1")
                    ], width=6),
                    dbc.Col([
                        html.P(f"Accelerazione: {selected_point2['acceleration']:.2f} m/s²", className="mb-1"),
                        html.P(f"Tempo: {selected_point2['time']:.2f} s", className="mb-1"),
                        html.P(f"Accelerazione media: {calculate_avg_acceleration(race2_data['data_points'], selected_point2):.2f} m/s²", className="mb-1")
                    ], width=6)
                ])
            ], style={"border-left": "4px solid #10B981"})  # Bordo verde per corsa 2
        else:
            details2 = "Nessun dato disponibile"
        
        return selected_point1, selected_point2, details1, details2
    
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
    
    # Aggiungi JavaScript per gestire i click sulle tabelle e evidenziare le righe
    comparison_dash._inline_scripts.append("""
    document.addEventListener('DOMContentLoaded', function() {
        // Click su riga tabella 1
        document.addEventListener('click', function(e) {
            if (e.target.closest('#data-table1 tbody tr')) {
                // Rimuovi classe active da tutte le righe
                document.querySelectorAll('#data-table1 tbody tr').forEach(row => {
                    row.classList.remove('table-primary');
                });
                
                // Aggiungi classe active alla riga cliccata
                e.target.closest('tr').classList.add('table-primary');
                
                // Scorri alla riga nella tabella
                e.target.closest('tr').scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        });
        
        // Click su riga tabella 2
        document.addEventListener('click', function(e) {
            if (e.target.closest('#data-table2 tbody tr')) {
                // Rimuovi classe active da tutte le righe
                document.querySelectorAll('#data-table2 tbody tr').forEach(row => {
                    row.classList.remove('table-success');
                });
                
                // Aggiungi classe active alla riga cliccata
                e.target.closest('tr').classList.add('table-success');
                
                // Scorri alla riga nella tabella
                e.target.closest('tr').scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        });
    });
    """)
    
    return comparison_dash.server