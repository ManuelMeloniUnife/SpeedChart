import dash
from dash import dcc, html, Input, Output, callback_context, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import Race, DataPoint
from flask import request

def init_dashboard(server):
    """Inizializza e integra la dashboard Dash con l'app Flask"""
    
    # Creazione dell'app Dash con tema BOOTSTRAP
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Layout della dashboard - SENZA DROPDOWN di selezione
    dash_app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("Dashboard Velocità", className="text-center mb-3")
            ])
        ]),
        
        dbc.Row([
            # Grafico a sinistra
            dbc.Col([
                dcc.Graph(
                    id='speed-distance-graph',
                    config={'displayModeBar': True, 'responsive': True},
                    style={'height': '60vh'},
                    className="border"
                )
            ], width=7),
            
            # Tabella dati a destra
            dbc.Col([
                html.Div([
                    html.H4("Dati", className="mb-2"),
                    html.Div(id='data-table-container', 
                             style={'height': '60vh', 'overflow-y': 'auto'})
                ], className="border p-3")
            ], width=5)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Dettagli punto selezionato", className="mb-2 mt-3"),
                    html.Div(id='selected-point-details', className="p-3 border")
                ])
            ])
        ]),
        
        # Store per i dati della corsa selezionata
        dcc.Store(id='race-data-store'),
        dcc.Store(id='selected-point-store'),
        
        # Aggiungiamo un componente interval che esegue il callback una volta sola all'avvio
        dcc.Interval(id='interval-component', interval=1000, max_intervals=1)
    ], className="container-fluid")
    
    # Callback per caricare i dati all'avvio della dashboard
    @dash_app.callback(
        Output('race-data-store', 'data'),
        Input('interval-component', 'n_intervals')
    )
    def load_race_data(n_intervals):
        # Ottieni l'ID della corsa dall'URL
        try:
            race_id = request.args.get('race_id')
            print(f"Caricamento dati corsa con ID: {race_id}")
            
            if not race_id:
                print("Nessun ID corsa fornito nell'URL")
                return None
            
            # Carica i dati della corsa dal database
            with server.app_context():
                try:
                    race = Race.query.get(race_id)
                    if not race:
                        print(f"Corsa non trovata: {race_id}")
                        return None
                        
                    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
                    
                    print(f"Trovati {len(data_points)} punti dati")
                    
                    race_info = {
                        'id': race.id,
                        'name': race.name,
                        'date': race.date.strftime('%d/%m/%Y %H:%M'),
                        'driver': race.spingitore.nome_completo() if race.spingitore else 'N/A',
                        'vehicle': getattr(race, 'vehicle', ''),
                        'notes': race.notes or ''
                    }
                    
                    points_data = [
                        {
                            'id': point.id,
                            'distance': float(point.distance),
                            'speed': float(point.speed),
                            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
                            'time': float(point.time) if point.time is not None else 0.0
                        } for point in data_points
                    ]
                    
                    return {'race': race_info, 'data_points': points_data}
                except Exception as e:
                    print(f"Errore nel caricamento dei dati della corsa: {e}")
                    return None
        except Exception as e:
            print(f"Errore generale: {e}")
            return None
    
    # Il resto dei callback rimane invariato
    # ...