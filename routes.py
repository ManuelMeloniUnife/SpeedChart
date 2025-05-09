from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Race, DataPoint
from utils.file_parser import parse_race_file
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Mostra la pagina principale con le corse recenti
    races = Race.query.order_by(Race.date.desc()).limit(10).all()
    return render_template('index.html', races=races)

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nessun file caricato', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('Nessun file selezionato', 'danger')
            return redirect(request.url)
            
        if file and file.filename.endswith('.txt'):
            # Leggi il contenuto del file
            file_content = file.read().decode('utf-8')
            
            # Ottieni i dati dal form
            race_name = request.form.get('race_name', file.filename)
            driver = request.form.get('driver', '')
            vehicle = request.form.get('vehicle', '')
            notes = request.form.get('notes', '')
            
            # Parsa il file
            try:
                parsed_data = parse_race_file(file_content)
                
                # Crea una nuova corsa
                race = Race(
                    name=race_name,
                    driver=driver,
                    vehicle=vehicle,
                    notes=notes,
                    wheel_circumference=parsed_data['header_info'].get('wheel_circumference', 1.52)
                )
                
                # Se è stata trovata una data nel file, usala
                if 'datetime' in parsed_data['header_info']:
                    race.date = parsed_data['header_info']['datetime']
                
                db.session.add(race)
                db.session.flush()  # Per ottenere l'ID della corsa
                
                # Aggiungi i punti dati
                for point in parsed_data['data_points']:
                    data_point = DataPoint(
                        race_id=race.id,
                        distance=point['distance'],
                        speed=point['speed'],
                        acceleration=point.get('acceleration', 0),
                        time=point.get('time', 0)
                    )
                    db.session.add(data_point)
                
                db.session.commit()
                flash(f'Corsa "{race_name}" caricata con successo!', 'success')
                return redirect(url_for('main.view_race', race_id=race.id))
                
            except Exception as e:
                flash(f'Errore durante il parsing del file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('File non supportato. Carica un file .txt', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html')

@main.route('/race/<int:race_id>')
def view_race(race_id):
    race = Race.query.get_or_404(race_id)
    return render_template('dashboard.html', race=race)

@main.route('/compare')
def compare():
    """Pagina per confrontare due corse"""
    races = Race.query.order_by(Race.date.desc()).all()
    return render_template('compare.html', races=races)

@main.route('/view_comparison/<int:race1_id>/<int:race2_id>')
def view_comparison(race1_id, race2_id):
    """Visualizza il confronto tra due corse"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    return render_template('comparison_dashboard.html', race1=race1, race2=race2)

@main.route('/api/races')
def get_races():
    races = Race.query.order_by(Race.date.desc()).all()
    races_list = [
        {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'driver': race.driver,
            'vehicle': race.vehicle
        } for race in races
    ]
    return jsonify(races_list)

@main.route('/api/race/<int:race_id>/data')
def get_race_data(race_id):
    race = Race.query.get_or_404(race_id)
    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
    
    data = {
        'race': {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'driver': race.driver,
            'vehicle': race.vehicle,
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