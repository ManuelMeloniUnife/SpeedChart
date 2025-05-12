# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Race, DataPoint, Spingitore
from utils.file_parser import parse_race_file
from datetime import datetime, date
from sqlalchemy import desc

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Reindirizza alla visualizzazione dati
    return redirect(url_for('main.visualizza_dati'))

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    # Ottieni gli spingitori attivi per il form
    spingitori_attivi = Spingitore.query.filter_by(attivo=True).order_by(Spingitore.nome).all()
    
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
            spingitore_id = request.form.get('spingitore_id', '')
            race_date = request.form.get('date', '')
            notes = request.form.get('notes', '')
            
            if not race_name or not spingitore_id:
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
                
                # Crea una nuova corsa
                race = Race(
                    name=race_name,
                    date=race_date,
                    spingitore_id=spingitore_id,
                    notes=notes,
                    wheel_circumference=parsed_data['header_info'].get('wheel_circumference', 1.52)
                )
                
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
                flash(f'Prova "{race_name}" caricata con successo!', 'success')
                return redirect(url_for('main.view_race', race_id=race.id))
                
            except Exception as e:
                flash(f'Errore durante il parsing del file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('File non supportato. Carica un file .txt', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html', 
                          spingitori_attivi=spingitori_attivi, 
                          today=today)

@main.route('/visualizza-dati')
def visualizza_dati():
    races = Race.query.order_by(Race.date.desc()).all()
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
    return render_template('visualizza_dati.html', races=races, spingitori=spingitori)

@main.route('/race/<int:race_id>')
def view_race(race_id):
    race = Race.query.get_or_404(race_id)
    return render_template('dashboard.html', race=race)

@main.route('/compare')
def compare():
    """Pagina per confrontare due corse"""
    races = Race.query.order_by(Race.date.desc()).all()
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
    return render_template('compare.html', races=races, spingitori=spingitori)

@main.route('/view_comparison/<int:race1_id>/<int:race2_id>')
def view_comparison(race1_id, race2_id):
    """Visualizza il confronto tra due corse"""
    race1 = Race.query.get_or_404(race1_id)
    race2 = Race.query.get_or_404(race2_id)
    return render_template('comparison_dashboard.html', race1=race1, race2=race2)

@main.route('/gestione-team')
def gestione_team():
    """Pagina per la gestione degli spingitori del team"""
    spingitori = Spingitore.query.order_by(Spingitore.nome).all()
    return render_template('gestione_team.html', spingitori=spingitori)

@main.route('/aggiungi-spingitore', methods=['POST'])
def aggiungi_spingitore():
    """Aggiunge un nuovo spingitore al team"""
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    
    if not nome:
        flash('Il nome è obbligatorio', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Crea un nuovo spingitore
    spingitore = Spingitore(
        nome=nome,
        cognome=cognome,
        ruolo=ruolo,
        attivo=True
    )
    
    db.session.add(spingitore)
    db.session.commit()
    
    flash(f'Spingitore {nome} {cognome} aggiunto con successo!', 'success')
    return redirect(url_for('main.gestione_team'))

@main.route('/modifica-spingitore', methods=['POST'])
def modifica_spingitore():
    """Modifica un spingitore esistente"""
    spingitore_id = request.form.get('id')
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    attivo = 'attivo' in request.form
    
    if not spingitore_id or not nome:
        flash('ID spingitore e nome sono obbligatori', 'danger')
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
    spingitore.attivo = attivo
    
    db.session.commit()
    
    flash(f'Spingitore {nome} {cognome} aggiornato con successo!', 'success')
    return redirect(url_for('main.gestione_team'))

@main.route('/cambia-stato-spingitore', methods=['POST'])
def cambia_stato_spingitore():
    """Cambia lo stato di uno spingitore tra Schierato e A Riposo"""
    spingitore_id = request.form.get('id')
    nuovo_stato = request.form.get('attivo') == '1'
    
    if not spingitore_id:
        flash('ID spingitore obbligatorio', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Trova lo spingitore
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Aggiorna lo stato
    spingitore.attivo = nuovo_stato
    db.session.commit()
    
    stato_str = "Schierato" if nuovo_stato else "A Riposo"
    flash(f'Lo spingitore {spingitore.nome_completo()} è ora {stato_str}.', 'success')
    return redirect(url_for('main.gestione_team'))

@main.route('/elimina-spingitore', methods=['POST'])
def elimina_spingitore():
    """Elimina un spingitore dal team e tutte le corse associate"""
    spingitore_id = request.form.get('id')
    
    if not spingitore_id:
        flash('ID spingitore obbligatorio', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Trova lo spingitore
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('main.gestione_team'))
    
    # Trova le corse associate
    corse_associate = Race.query.filter_by(spingitore_id=spingitore_id).all()
    num_corse = len(corse_associate)
    
    # Elimina tutte le corse associate e i loro data points
    for corsa in corse_associate:
        db.session.delete(corsa)
    
    # Elimina lo spingitore
    db.session.delete(spingitore)
    db.session.commit()
    
    # Messaggio di conferma
    if num_corse > 0:
        flash(f'Spingitore {spingitore.nome_completo()} e {num_corse} prove associate eliminate con successo!', 'success')
    else:
        flash(f'Spingitore {spingitore.nome_completo()} eliminato con successo!', 'success')
    
    return redirect(url_for('main.gestione_team'))

@main.route('/elimina-corsa', methods=['POST'])
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
    
    # Elimina la corsa (i data_points saranno eliminati automaticamente grazie a cascade="all, delete-orphan")
    db.session.delete(race)
    db.session.commit()
    
    flash(f'Prova "{race_name}" eliminata con successo.', 'success')
    return redirect(url_for('main.visualizza_dati'))

@main.route('/api/races')
def get_races():
    races = Race.query.order_by(Race.date.desc()).all()
    races_list = [
        {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.spingitore.nome_completo() if race.spingitore else 'N/A',
            'notes': race.notes
        } for race in races
    ]
    return jsonify(races_list)

@main.route('/api/spingitori')
def get_spingitori():
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

@main.route('/api/race/<int:race_id>/data')
def get_race_data(race_id):
    race = Race.query.get_or_404(race_id)
    data_points = DataPoint.query.filter_by(race_id=race_id).order_by(DataPoint.distance).all()
    
    data = {
        'race': {
            'id': race.id,
            'name': race.name,
            'date': race.date.strftime('%d/%m/%Y %H:%M'),
            'pilota': race.spingitore.nome_completo() if race.spingitore else 'N/A',
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