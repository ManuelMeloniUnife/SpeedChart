# routes/main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Race, DataPoint, Spingitore, RaceSpingitore, Cartella
from utils.file_parser import parse_race_file
from datetime import datetime, date
from sqlalchemy import desc, text
from sqlalchemy.orm import joinedload

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
    """Pagina principale - reindirizza alla visualizzazione dati"""
    return redirect(url_for('main.visualizza_dati'))

@main_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    """Pagina per caricare nuove corse"""
    # Ottieni i piloti attivi per la selezione pilota
    piloti = Spingitore.query.filter_by(ruolo='Pilota', attivo=True).order_by(Spingitore.nome).all()
    
    # Ottieni gli spingitori attivi per il form delle staffette  
    spingitori_attivi = Spingitore.query.filter_by(ruolo='Spingitore', attivo=True).order_by(Spingitore.nome).all()
    
    # Ottieni le cartelle per il form
    cartelle = Cartella.query.order_by(Cartella.nome).all()
    
    # Data odierna per il campo data
    today = date.today().strftime('%Y-%m-%d')
    
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
            race_name = request.form.get('race_name', '')
            pilota_id = request.form.get('pilota_id')  # ID del pilota
            spingitori_order = request.form.get('spingitori_order', '')  # ID spingitori separati da virgola
            race_date = request.form.get('date', '')
            notes = request.form.get('notes', '')
            cartella_id = request.form.get('cartella_id')
            
            # Converte la stringa degli spingitori in lista di ID
            spingitori_ids = []
            if spingitori_order and spingitori_order.strip():
                try:
                    spingitori_ids = [int(id.strip()) for id in spingitori_order.split(',') if id.strip()]
                except ValueError:
                    spingitori_ids = []
            
            if not race_name or not pilota_id:
                flash('Nome della prova e pilota sono obbligatori', 'danger')
                return redirect(request.url)
            
            # Parsa il file
            try:
                parsed_data = parse_race_file(file_content)
                
                # Converte la data dal form in datetime
                try:
                    race_date = datetime.strptime(race_date, '%Y-%m-%d')
                except:
                    race_date = datetime.now()
                
                # Converte cartella_id
                try:
                    cartella_id = int(cartella_id) if cartella_id and cartella_id != '' else None
                except ValueError:
                    cartella_id = None
                
                # Crea una nuova corsa
                race = Race(
                    name=race_name,
                    date=race_date,
                    notes=notes,
                    wheel_circumference=parsed_data['header_info'].get('wheel_circumference', 1.52),
                    cartella_id=cartella_id
                )
                
                db.session.add(race)
                db.session.flush()  # Per ottenere l'ID della corsa
                
                # Aggiungi il pilota (ordine 1)
                race_pilota = RaceSpingitore(
                    race_id=race.id,
                    spingitore_id=pilota_id,
                    ordine_esecuzione=1
                )
                db.session.add(race_pilota)
                
                # Aggiungi gli spingitori selezionati (ordine 2, 3, 4...)
                for i, spingitore_id in enumerate(spingitori_ids, start=2):
                    race_spingitore = RaceSpingitore(
                        race_id=race.id,
                        spingitore_id=spingitore_id,
                        ordine_esecuzione=i
                    )
                    db.session.add(race_spingitore)
                
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
                flash(f'Prova "{race_name}" caricata con successo!', 'success')
                return redirect(url_for('main.view_race_direct', race_id=race.id))
                
            except Exception as e:
                flash(f'Errore durante il parsing del file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('File non supportato. Carica un file .txt', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html', 
                          piloti=piloti,
                          spingitori_attivi=spingitori_attivi,
                          cartelle=cartelle, 
                          today=today)

@main_blueprint.route('/visualizza-dati')
def visualizza_dati():
    """Pagina principale per visualizzare tutte le corse e cartelle"""
    # Carica tutte le cartelle con le loro corse
    cartelle = Cartella.query.options(joinedload(Cartella.races)).order_by(Cartella.nome).all()
    
    # Carica le corse che non sono in nessuna cartella (cartella_id is NULL)
    corse_senza_cartella = Race.query.filter(Race.cartella_id.is_(None)).options(joinedload(Race.race_spingitori_ordered)).order_by(Race.date.desc()).all()
    
    # Ottieni tutti gli spingitori per il form di filtro
    spingitori = Spingitore.query.filter_by(attivo=True).order_by(Spingitore.nome).all()
    
    # Converti spingitori in formato JSON-like per il template
    spingitori_data = []
    for spingitore in spingitori:
        spingitori_data.append({
            'id': spingitore.id,
            'nome': spingitore.nome,
            'cognome': spingitore.cognome or '',
            'nome_completo': spingitore.nome_completo()
        })
    
    # Crea la struttura corse_per_cartella che si aspetta il template
    corse_per_cartella = {}
    
    # Aggiungi TUTTE le cartelle (anche quelle vuote)
    for cartella in cartelle:
        corse_per_cartella[cartella.nome] = {
            'cartella': cartella,
            'corse': cartella.races if cartella.races else []
        }
    
    # Aggiungi le corse senza cartella come "Generale" (sempre presente)
    corse_per_cartella['Generale'] = {
        'cartella': None,
        'corse': corse_senza_cartella if corse_senza_cartella else []
    }
            
    return render_template('visualizza_dati.html', 
                          cartelle=cartelle,
                          corse_senza_cartella=corse_senza_cartella,
                          corse_per_cartella=corse_per_cartella,
                          spingitori=spingitori, 
                          spingitori_data=spingitori_data)

@main_blueprint.route('/race/<int:race_id>')
def view_race(race_id):
    """Visualizza una corsa con la dashboard Dash"""
    race = Race.query.get_or_404(race_id)
    return render_template('dashboard.html', race=race)

@main_blueprint.route('/view_race_direct/<int:race_id>')
def view_race_direct(race_id):
    """Visualizza una corsa con dati precaricati (senza Dash)"""
    race = Race.query.get_or_404(race_id)
    
    # Ottieni i dati direttamente per passarli al template
    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
    
    # Converti i dati per renderli serializzabili per JavaScript
    race_data = {
        'id': race.id,
        'name': race.name,
        'date': race.date.strftime('%d/%m/%Y %H:%M'),
        'pilota': race.get_pilota_name(),  # Solo il pilota
        'spingitori': race.get_spingitori_names(),  # Solo gli spingitori
        'notes': race.notes
    }
    
    points_data = [
        {
            'distance': float(point.distance),
            'speed': float(point.speed),
            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
            'time': float(point.time) if point.time is not None else 0.0
        } for point in data_points
    ]
    
    return render_template('view_race_direct.html', 
                          race=race,
                          race_data=race_data,
                          points_data=points_data)

@main_blueprint.route('/compare')
def compare():
    """Pagina per confrontare due corse"""
    # Ottieni tutte le corse per il form di selezione
    races = Race.query.order_by(Race.date.desc()).all()
    
    # Ottieni tutti gli spingitori per il filtro
    spingitori = Spingitore.query.filter_by(attivo=True).order_by(Spingitore.nome).all()
    
    return render_template('compare.html', races=races, spingitori=spingitori)

@main_blueprint.route('/view_comparison/<int:race1_id>/<int:race2_id>')
def view_comparison(race1_id, race2_id):
    """Visualizza il confronto tra due corse usando Dash"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    return render_template('comparison_dashboard.html', race1=race1, race2=race2)

@main_blueprint.route('/view_comparison_direct/<int:race1_id>/<int:race2_id>')
def view_comparison_direct(race1_id, race2_id):
    """Visualizza il confronto tra due corse con dati precaricati (senza Dash)"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    
    # Ottieni i dati di entrambe le corse
    data_points_1 = DataPoint.query.filter_by(race_id=race1_id).order_by(DataPoint.distance).all()
    data_points_2 = DataPoint.query.filter_by(race_id=race2_id).order_by(DataPoint.distance).all()
    
    # Converti i dati per renderli serializzabili per JavaScript
    race1_data = {
        'id': race1.id,
        'name': race1.name,
        'date': race1.date.strftime('%d/%m/%Y %H:%M'),
        'pilota': race1.get_pilota_name(),
        'spingitori': race1.get_spingitori_names(),
        'notes': race1.notes
    }
    
    race2_data = {
        'id': race2.id,
        'name': race2.name,
        'date': race2.date.strftime('%d/%m/%Y %H:%M'),
        'pilota': race2.get_pilota_name(),
        'spingitori': race2.get_spingitori_names(),
        'notes': race2.notes
    }
    
    points1_data = [
        {
            'distance': float(point.distance),
            'speed': float(point.speed),
            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
            'time': float(point.time) if point.time is not None else 0.0
        } for point in data_points_1
    ]
    
    points2_data = [
        {
            'distance': float(point.distance),
            'speed': float(point.speed),
            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
            'time': float(point.time) if point.time is not None else 0.0
        } for point in data_points_2
    ]
    
    return render_template('view_comparison_direct.html',
                          race1=race1,
                          race2=race2,
                          race1_data=race1_data,
                          race2_data=race2_data,
                          points1_data=points1_data,
                          points2_data=points2_data)

@main_blueprint.route('/elimina-corsa', methods=['POST'])
def elimina_corsa():
    """Elimina una corsa e tutti i dati associati"""
    race_id = request.form.get('id')
    
    if not race_id:
        flash('ID corsa obbligatorio', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Trova la corsa
    race = Race.query.get(race_id)
    if not race:
        flash('Corsa non trovata', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Memorizza il nome per il messaggio
    race_name = race.name
    
    try:
        # Elimina le associazioni race_spingitore
        db.session.execute(
            text("DELETE FROM race_spingitore WHERE race_id = :race_id"),
            {'race_id': race_id}
        )
        
        # Elimina la corsa (i data_points saranno eliminati automaticamente grazie a cascade="all, delete-orphan")
        db.session.delete(race)
        db.session.commit()
        
        flash(f'Prova "{race_name}" eliminata con successo.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione della prova: {str(e)}', 'danger')
    
    return redirect(url_for('main.visualizza_dati'))
