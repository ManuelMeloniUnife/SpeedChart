# routes/team_management.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Spingitore
from sqlalchemy import text

team_blueprint = Blueprint('team', __name__)

@team_blueprint.route('/gestione-team')
def gestione_team():
    """Pagina per la gestione degli spingitori del team"""
    # Separa piloti e spingitori
    piloti = Spingitore.query.filter_by(ruolo='Pilota').order_by(Spingitore.nome).all()
    spingitori = Spingitore.query.filter_by(ruolo='Spingitore').order_by(Spingitore.nome).all()
    
    return render_template('gestione_team.html', 
                          piloti=piloti, 
                          spingitori=spingitori)

@team_blueprint.route('/aggiungi-spingitore', methods=['POST'])
def aggiungi_spingitore():
    """Aggiunge un nuovo spingitore al team"""
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    
    if not nome:
        flash('Il nome è obbligatorio', 'danger')
        return redirect(url_for('team.gestione_team'))
    
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
    return redirect(url_for('team.gestione_team'))

@team_blueprint.route('/modifica-spingitore', methods=['POST'])
def modifica_spingitore():
    """Modifica un spingitore esistente"""
    spingitore_id = request.form.get('id')
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    ruolo = request.form.get('ruolo', '').strip()
    attivo = 'attivo' in request.form
    
    if not spingitore_id or not nome:
        flash('ID spingitore e nome sono obbligatori', 'danger')
        return redirect(url_for('team.gestione_team'))
    
    # Trova lo spingitore
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('team.gestione_team'))
    
    # Aggiorna i dati
    spingitore.nome = nome
    spingitore.cognome = cognome
    spingitore.ruolo = ruolo
    spingitore.attivo = attivo
    
    db.session.commit()
    
    flash(f'Spingitore {nome} {cognome} aggiornato con successo!', 'success')
    return redirect(url_for('team.gestione_team'))

@team_blueprint.route('/elimina-spingitore', methods=['POST'])
def elimina_spingitore():
    """Elimina un spingitore dal team e tutte le corse associate"""
    spingitore_id = request.form.get('id')
    
    if not spingitore_id:
        flash('ID spingitore obbligatorio', 'danger')
        return redirect(url_for('team.gestione_team'))
    
    # Trova lo spingitore
    spingitore = Spingitore.query.get(spingitore_id)
    if not spingitore:
        flash('Spingitore non trovato', 'danger')
        return redirect(url_for('team.gestione_team'))
    
    # Conta le corse associate
    result = db.session.execute(
        text("SELECT race_id FROM race_spingitore WHERE spingitore_id = :spingitore_id"),
        {'spingitore_id': spingitore_id}
    )
    corse_associate = result.fetchall()
    num_corse = len(corse_associate)
    
    # Memorizza il nome per il messaggio
    nome_spingitore = spingitore.nome_completo()
    
    try:
        # Elimina le associazioni race_spingitore
        db.session.execute(
            text("DELETE FROM race_spingitore WHERE spingitore_id = :spingitore_id"),
            {'spingitore_id': spingitore_id}
        )
        
        # Elimina lo spingitore
        db.session.delete(spingitore)
        db.session.commit()
        
        # Messaggio di conferma
        if num_corse > 0:
            flash(f'Spingitore {nome_spingitore} eliminato con successo! Rimosso da {num_corse} prove.', 'success')
        else:
            flash(f'Spingitore {nome_spingitore} eliminato con successo!', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione del spingitore: {str(e)}', 'danger')
    
    return redirect(url_for('team.gestione_team'))
