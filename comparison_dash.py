import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import Race, DataPoint
from flask import request

def init_comparison_dashboard(server):
    """Inizializza e integra la dashboard di confronto Dash con l'app Flask"""
    
    # Creazione dell'app Dash con tema chiaro
    comparison_dash = dash.Dash(
        server=server,
        routes_pathname_prefix='/comparison/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Layout della dashboard
    comparison_dash.layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Confronto Prestazioni", className="text-center mb-3"),
                html.Div([
                    html.Div(id='races-info')
                ])
            ])
        ]),
        
        # Nuova struttura per il layout: grafico + tabelle affiancate
        dbc.Row([
            # Grafico a sinistra
            dbc.Col([
                dcc.Graph(
                    id='comparison-graph',
                    config={'displayModeBar': True, 'responsive': True},
                    style={'height': '60vh'},
                    className="border"
                )
            ], width=7),
            
            # Tabelle a destra (entrambe visibili contemporaneamente)
            dbc.Col([
                # Prima tabella
                html.Div([
                    html.H5("Dati Corsa 1", className="mb-2"),
                    html.Div(id='data-table1-container', style={'height': '29vh', 'overflow-y': 'auto'})
                ], className="mb-3 border p-2"),
                
                # Seconda tabella
                html.Div([
                    html.H5("Dati Corsa 2", className="mb-2"),
                    html.Div(id='data-table2-container', style={'height': '29vh', 'overflow-y': 'auto'})
                ], className="border p-2")
            ], width=5)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Dettagli punto - Corsa 1", className="mb-2 mt-3"),
                    html.Div(id='selected-point1-details', className="p-2 border")
                ])
            ], width=6),
            
            dbc.Col([
                html.Div([
                    html.H5("Dettagli punto - Corsa 2", className="mb-2 mt-3"),
                    html.Div(id='selected-point2-details', className="p-2 border")
                ])
            ], width=6)
        ]),
        
        # Store per i dati delle corse selezionate
        dcc.Store(id='race1-data-store'),
        dcc.Store(id='race2-data-store'),
        dcc.Store(id='selected-point1-store'),
        dcc.Store(id='selected-point2-store'),
        
        # Intervallo per caricare i dati all'avvio
        dcc.Interval(id='interval-component', interval=1000, max_intervals=1)
    ], className="container-fluid")
    
    # Callbacks per caricare i dati delle corse
    @comparison_dash.callback(
        Output('race1-data-store', 'data'),
        Input('interval-component', 'n_intervals')
    )
    def load_race1_data(n_intervals):
        # Ottieni l'ID della corsa 1 dall'URL
        try:
            race1_id = request.args.get('race1_id')
            print(f"Caricamento dati corsa 1 con ID: {race1_id}")
            
            if not race1_id:
                print("Nessun ID corsa 1 fornito nell'URL")
                return None
            
            # Carica i dati della corsa dal database
            with server.app_context():
                try:
                    race = Race.query.get(race1_id)
                    if not race:
                        print(f"Corsa 1 non trovata: {race1_id}")
                        return None
                        
                    data_points = DataPoint.query.filter_by(race_id=race1_id).order_by(DataPoint.distance).all()
                    
                    print(f"Trovati {len(data_points)} punti dati per la corsa 1")
                    
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
                    print(f"Errore nel caricamento dei dati della corsa 1: {e}")
                    return None
        except Exception as e:
            print(f"Errore generale: {e}")
            return None
    
    @comparison_dash.callback(
        Output('race2-data-store', 'data'),
        Input('interval-component', 'n_intervals')
    )
    def load_race2_data(n_intervals):
        # Ottieni l'ID della corsa 2 dall'URL
        try:
            race2_id = request.args.get('race2_id')
            print(f"Caricamento dati corsa 2 con ID: {race2_id}")
            
            if not race2_id:
                print("Nessun ID corsa 2 fornito nell'URL")
                return None
            
            # Carica i dati della corsa dal database
            with server.app_context():
                try:
                    race = Race.query.get(race2_id)
                    if not race:
                        print(f"Corsa 2 non trovata: {race2_id}")
                        return None
                        
                    data_points = DataPoint.query.filter_by(race_id=race2_id).order_by(DataPoint.distance).all()
                    
                    print(f"Trovati {len(data_points)} punti dati per la corsa 2")
                    
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
                    print(f"Errore nel caricamento dei dati della corsa 2: {e}")
                    return None
        except Exception as e:
            print(f"Errore generale: {e}")
            return None
    
    # Il resto dei callback rimane invariato
    # ...