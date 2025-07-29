# routes/api.py
from flask import Blueprint, jsonify
from models import Race, DataPoint, Spingitore

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

@api_blueprint.route('/races')
def get_races():
    """API per ottenere tutte le corse"""
    races = Race.query.order_by(Race.date.desc()).all()
    races_list = [
        {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.get_pilota_name(),
            'spingitori': race.get_spingitori_names(),
            'notes': race.notes,
            'cartella_id': race.cartella_id
        } for race in races
    ]
    return jsonify(races_list)

@api_blueprint.route('/spingitori')
def get_spingitori():
    """API per ottenere tutti gli spingitori attivi"""
    spingitori = Spingitore.query.filter_by(attivo=True).order_by(Spingitore.nome).all()
    spingitori_list = [
        {
            'id': spingitore.id,
            'nome': spingitore.nome,
            'cognome': spingitore.cognome,
            'ruolo': spingitore.ruolo,
            'nome_completo': spingitore.nome_completo()
        } for spingitore in spingitori
    ]
    return jsonify(spingitori_list)

@api_blueprint.route('/race/<int:race_id>/data')
def get_race_data(race_id):
    """API per ottenere i dati di una specifica corsa"""
    race = Race.query.get_or_404(race_id)
    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
    
    data = {
        'race': {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.get_pilota_name(),
            'spingitori': race.get_spingitori_names(),
            'notes': race.notes
        },
        'data_points': [
            {
                'id': point.id,
                'distance': point.distance,
                'speed': point.speed,
                'acceleration': point.acceleration,
                'time': point.time
            } for point in data_points
        ]
    }
    
    return jsonify(data)
