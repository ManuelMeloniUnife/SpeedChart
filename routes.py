# routes.py
# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Race, DataPoint, Spingitore, RaceSpingitore
from utils.file_parser import parse_race_file
from datetime import datetime, date
from sqlalchemy import desc, text

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Reindirizza alla visualizzazione dati
    return redirect(url_for('main.visualizza_dati'))

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    # Ottieni piloti e spingitori separatamente
    piloti = Spingitore.query.filter_by(ruolo='Pilota').order_by(Spingitore.nome).all()
    spingitori = Spingitore.query.filter_by(ruolo='Spingitore').order_by(Spingitore.nome).all()
    
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
            pilota_id = request.form.get('pilota_id', '')  # ID del pilota (obbligatorio)
            spingitori_order = request.form.get('spingitori_order', '')  # IDs degli spingitori (opzionale)
            race_date = request.form.get('date', '')
            notes = request.form.get('notes', '')
            
            # Validazione
            if not race_name or not pilota_id:
                flash('Nome della prova e pilota sono obbligatori', 'danger')
                return redirect(request.url)
            
            # Verifica che il pilota esista e sia effettivamente un pilota
            pilota = Spingitore.query.filter_by(id=pilota_id, ruolo='Pilota').first()
            if not pilota:
                flash('Pilota non valido', 'danger')
                return redirect(request.url)
            
            # Parsa l'ordine degli spingitori (opzionale)
            spingitori_ids = []
            if spingitori_order:
                try:
                    spingitori_ids = [int(id_str) for id_str in spingitori_order.split(',') if id_str.strip()]
                    # Verifica che tutti gli ID siano di spingitori validi
                    for spingitore_id in spingitori_ids:
                        spingitore = Spingitore.query.filter_by(id=spingitore_id, ruolo='Spingitore').first()
                        if not spingitore:
                            flash(f'Spingitore con ID {spingitore_id} non valido', 'danger')
                            return redirect(request.url)
                except ValueError:
                    flash('Errore nel formato dell\'ordine spingitori', 'danger')
                    return redirect(request.url)
            
            # Parsa il file
            try:
                parsed_data = parse_race_file(file_content)
                
                # Converte la data dal form in datetime
                try:
                    race_date = datetime.strptime(race_date, '%Y-%m-%d')
                except:
                    race_date = datetime.now()
                
                # Crea una nuova corsa
                race = Race(
                    name=race_name,
                    date=race_date,
                    notes=notes,
                    wheel_circumference=parsed_data['header_info'].get('wheel_circumference', 1.52)
                )
                
                db.session.add(race)
                db.session.flush()  # Per ottenere l'ID della corsa
                
                # Aggiungi il pilota (sempre al primo posto, ordine 0)
                race_pilota = RaceSpingitore(
                    race_id=race.id,
                    spingitore_id=pilota_id,
                    ordine_esecuzione=0  # Il pilota ha sempre ordine 0
                )
                db.session.add(race_pilota)
                
                # Aggiungi gli spingitori con l'ordine specificato (se presenti)
                for ordine, spingitore_id in enumerate(spingitori_ids, 1):
                    race_spingitore = RaceSpingitore(
                        race_id=race.id,
                        spingitore_id=spingitore_id,
                        ordine_esecuzione=ordine  # Gli spingitori partono da ordine 1
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
                          spingitori=spingitori, 
                          today=today)

@main.route('/visualizza-dati')
def visualizza_dati():
    # Ottieni tutti gli spingitori - usati per filtro
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
    
    # Ottieni tutte le corse (rimuoviamo il filtro per spingitori attivi)
    races = Race.query.order_by(Race.date.desc()).all()
    
    # Converti gli spingitori in dizionari per la serializzazione JSON
    spingitori_data = []
    for spingitore in spingitori:
        spingitori_data.append({
            'id': spingitore.id,
            'nome': spingitore.nome,
            'cognome': spingitore.cognome or '',
            'nome_completo': spingitore.nome_completo()
        })
            
    return render_template('visualizza_dati.html', 
                          races=races, 
                          spingitori=spingitori, 
                          spingitori_data=spingitori_data)

@main.route('/race/<int:race_id>')
def view_race(race_id):
    race = Race.query.get_or_404(race_id)
    return render_template('dashboard.html', race=race)

@main.route('/view_race_direct/<int:race_id>')
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

@main.route('/compare')
def compare():
    """Pagina per confrontare due corse"""
    races = Race.query.order_by(Race.date.desc()).all()
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
    
    # Converti gli spingitori in dizionari per la serializzazione JSON
    spingitori_data = []
    for spingitore in spingitori:
        spingitori_data.append({
            'id': spingitore.id,
            'nome': spingitore.nome,
            'cognome': spingitore.cognome or '',
            'nome_completo': spingitore.nome_completo()
        })
    
    return render_template('compare.html', 
                          races=races, 
                          spingitori=spingitori,
                          spingitori_data=spingitori_data)

@main.route('/view_comparison/<int:race1_id>/<int:race2_id>')
def view_comparison(race1_id, race2_id):
    """Visualizza il confronto tra due corse"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    return render_template('comparison_dashboard.html', race1=race1, race2=race2)

@main.route('/view_comparison_direct/<int:race1_id>/<int:race2_id>')
def view_comparison_direct(race1_id, race2_id):
    """Visualizza il confronto tra due corse con dati precaricati (senza Dash)"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    
    # Ottieni i dati direttamente
    data_points1 = DataPoint.query.filter_by(race_id=race1_id).order_by(DataPoint.distance).all()
    data_points2 = DataPoint.query.filter_by(race_id=race2_id).order_by(DataPoint.distance).all()
    
    # Converti i dati
    race1_data = {
        'id': race1.id,
        'name': race1.name,
        'date': race1.date.strftime('%d/%m/%Y %H:%M'),
        'pilota': race1.get_pilota_name(),  # Solo il pilota
        'spingitori': race1.get_spingitori_names(),  # Solo gli spingitori
        'notes': race1.notes
    }
    
    race2_data = {
        'id': race2.id,
        'name': race2.name,
        'date': race2.date.strftime('%d/%m/%Y %H:%M'),
        'pilota': race2.get_pilota_name(),  # Solo il pilota
        'spingitori': race2.get_spingitori_names(),  # Solo gli spingitori
        'notes': race2.notes
    }
    
    points_data1 = [
        {
            'distance': float(point.distance),
            'speed': float(point.speed),
            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
            'time': float(point.time) if point.time is not None else 0.0
        } for point in data_points1
    ]
    
    points_data2 = [
        {
            'distance': float(point.distance),
            'speed': float(point.speed),
            'acceleration': float(point.acceleration) if point.acceleration is not None else 0.0,
            'time': float(point.time) if point.time is not None else 0.0
        } for point in data_points2
    ]
    
    return render_template('view_comparison_direct.html', 
                          race1=race1,             # Assicurati che 'race1' venga passato
                          race2=race2,             # Assicurati che 'race2' venga passato
                          race1_data=race1_data,
                          race2_data=race2_data,
                          points_data1=points_data1,
                          points_data2=points_data2)

@main.route('/gestione-team')
def gestione_team():
    """Pagina per la gestione degli spingitori del team"""
    piloti = Spingitore.query.filter_by(ruolo='Pilota').order_by(Spingitore.nome).all()
    spingitori = Spingitore.query.filter_by(ruolo='Spingitore').order_by(Spingitore.nome).all()
    return render_template('gestione_team.html', piloti=piloti, spingitori=spingitori)

@main.route('/aggiungi-spingitore', methods=['POST'])
def aggiungi_spingitore():
    """Aggiunge un nuovo spingitore al team"""
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    
    if not nome:
        flash('Il nome è obbligatorio', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    if ruolo not in ['Pilota', 'Spingitore']:
        flash('Ruolo non valido. Seleziona Pilota o Spingitore.', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Crea un nuovo spingitore
    spingitore = Spingitore(
        nome=nome,
        cognome=cognome,
        ruolo=ruolo
    )
    
    db.session.add(spingitore)
    db.session.commit()
    
    flash(f'{ruolo} {nome} {cognome} aggiunto con successo!', 'success')
    return redirect(url_for('main.gestione_team'))

@main.route('/modifica-spingitore', methods=['POST'])
def modifica_spingitore():
    """Modifica un spingitore esistente"""
    spingitore_id = request.form.get('id')
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    
    if not spingitore_id or not nome:
        flash('ID spingitore e nome sono obbligatori', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    if ruolo not in ['Pilota', 'Spingitore']:
        flash('Ruolo non valido. Seleziona Pilota o Spingitore.', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Trova lo spingitore
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Aggiorna i dati
    spingitore.nome = nome
    spingitore.cognome = cognome
    spingitore.ruolo = ruolo
    
    db.session.commit()
    
    flash(f'{ruolo} {nome} {cognome} aggiornato con successo!', 'success')
    return redirect(url_for('main.gestione_team'))

@main.route('/elimina-spingitore', methods=['POST'])
def elimina_spingitore():
    """Elimina un spingitore dal team e tutte le prove in cui è coinvolto"""
    spingitore_id = request.form.get('id')
    
    if not spingitore_id:
        flash('ID spingitore obbligatorio', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Trova lo spingitore per ottenere il nome
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    nome_completo = spingitore.nome_completo()
    
    try:
        # Usa SQL diretto per evitare problemi con SQLAlchemy ORM
        # Prima trova le prove associate
        result = db.session.execute(
            text("SELECT race_id FROM race_spingitore WHERE spingitore_id = :spingitore_id"),
            {"spingitore_id": spingitore_id}
        )
        race_ids = [row[0] for row in result.fetchall()]
        num_prove = len(race_ids)
        
        # Elimina prima i data_points delle prove associate
        if race_ids:
            race_ids_str = ','.join(map(str, race_ids))
            db.session.execute(
                text(f"DELETE FROM data_point WHERE race_id IN ({race_ids_str})")
            )
        
        # Elimina le associazioni race_spingitore
        db.session.execute(
            text("DELETE FROM race_spingitore WHERE spingitore_id = :spingitore_id"),
            {"spingitore_id": spingitore_id}
        )
        
        # Elimina le prove
        if race_ids:
            race_ids_str = ','.join(map(str, race_ids))
            db.session.execute(
                text(f"DELETE FROM race WHERE id IN ({race_ids_str})")
            )
        
        # Elimina lo spingitore
        db.session.execute(
            text("DELETE FROM spingitore WHERE id = :spingitore_id"),
            {"spingitore_id": spingitore_id}
        )
        
        # Commit tutto
        db.session.commit()
        
        # Messaggio di conferma
        if num_prove > 0:
            flash(f'Spingitore {nome_completo} eliminato con successo! Eliminate anche {num_prove} prove associate.', 'success')
        else:
            flash(f'Spingitore {nome_completo} eliminato con successo!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'danger')
    
    return redirect(url_for('main.gestione_team'))

@main.route('/elimina-corsa', methods=['POST'])
def elimina_corsa():
    """Elimina una corsa e tutti i dati associati"""
    race_id = request.form.get('id')
    
    if not race_id:
        flash('ID corsa obbligatorio', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Trova la corsa per ottenere il nome
    race = Race.query.get(race_id)
    if not race:
        flash('Corsa non trovata', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Memorizza il nome per il messaggio
    race_name = race.name
    
    try:
        # Usa SQL diretto per evitare problemi con SQLAlchemy ORM
        # Elimina i data_points
        db.session.execute(
            text("DELETE FROM data_point WHERE race_id = :race_id"),
            {"race_id": race_id}
        )
        
        # Elimina le associazioni race_spingitore
        db.session.execute(
            text("DELETE FROM race_spingitore WHERE race_id = :race_id"),
            {"race_id": race_id}
        )
        
        # Elimina la corsa
        db.session.execute(
            text("DELETE FROM race WHERE id = :race_id"),
            {"race_id": race_id}
        )
        
        # Commit tutto
        db.session.commit()
        
        flash(f'Prova "{race_name}" eliminata con successo.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'danger')
    
    return redirect(url_for('main.visualizza_dati'))

@main.route('/api/races')
def get_races():
    races = Race.query.order_by(Race.date.desc()).all()
    races_list = [
        {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.get_pilota_name(),  # Solo il pilota
            'spingitori': race.get_spingitori_names(),  # Solo gli spingitori
            'notes': race.notes
        } for race in races
    ]
    return jsonify(races_list)

@main.route('/api/spingitori')
def get_spingitori():
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
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

@main.route('/api/race/<int:race_id>/data')
def get_race_data(race_id):
    race = Race.query.get_or_404(race_id)
    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
    
    data = {
        'race': {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.get_pilota_name(),  # Solo il pilota
            'spingitori': race.get_spingitori_names(),  # Solo gli spingitori
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