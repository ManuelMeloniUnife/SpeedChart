# routes/folder_management.py
from flask import Blueprint, request, redirect, url_for, flash
from models import db, Cartella, Race
from sqlalchemy.orm import joinedload

folder_blueprint = Blueprint('folder', __name__)

@folder_blueprint.route('/crea-cartella', methods=['POST'])
def crea_cartella():
    """Crea una nuova cartella"""
    nome_cartella = request.form.get('nome_cartella', '').strip()
    colore_cartella = request.form.get('colore', '#007bff')  # Colore predefinito
    cartella_padre_id = request.form.get('cartella_padre_id')
    
    if not nome_cartella:
        flash('Il nome della cartella è obbligatorio', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Controlla se il nome è riservato
    if nome_cartella.lower() == 'generale':
        flash('Il nome "Generale" è riservato. Selezionare un nome diverso.', 'warning')
        return redirect(url_for('main.visualizza_dati'))
    
    # Controlla se esiste già una cartella con lo stesso nome nella stessa cartella padre
    cartella_esistente = Cartella.query.filter_by(
        nome=nome_cartella, 
        cartella_padre_id=cartella_padre_id
    ).first()
    
    if cartella_esistente:
        flash(f'Cartella "{nome_cartella}" già esistente, selezionare un nome diverso.', 'warning')
        return redirect(url_for('main.visualizza_dati'))
    
    # Converte cartella_padre_id in intero o None
    try:
        cartella_padre_id = int(cartella_padre_id) if cartella_padre_id and cartella_padre_id != '' else None
    except ValueError:
        cartella_padre_id = None
    
    # Crea la nuova cartella
    cartella = Cartella(
        nome=nome_cartella,
        colore=colore_cartella,
        cartella_padre_id=cartella_padre_id
    )
    
    db.session.add(cartella)
    db.session.commit()
    
    flash(f'Cartella "{nome_cartella}" creata con successo!', 'success')
    return redirect(url_for('main.visualizza_dati'))

@folder_blueprint.route('/elimina-cartella', methods=['POST'])  
def elimina_cartella():
    """Elimina una cartella e sposta le corse contenute nella cartella padre o in root"""
    cartella_id = request.form.get('cartella_id')
    
    if not cartella_id:
        flash('ID cartella obbligatorio', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Trova la cartella
    cartella = Cartella.query.get(cartella_id)
    if not cartella:
        flash('Cartella non trovata', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Controlla se ci sono sottocartelle
    sottocartelle = Cartella.query.filter_by(cartella_padre_id=cartella.id).all()
    if sottocartelle:
        nomi_sottocartelle = [sc.nome for sc in sottocartelle]
        flash(f'Impossibile eliminare la cartella: contiene le sottocartelle: {", ".join(nomi_sottocartelle)}. Elimina prima le sottocartelle.', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    nome_cartella = cartella.nome
    cartella_padre_id = cartella.cartella_padre_id
    
    # Sposta tutte le corse di questa cartella nella cartella padre (o in root se non ha padre)
    corse_in_cartella = Race.query.filter_by(cartella_id=cartella.id).all()
    for corsa in corse_in_cartella:
        corsa.cartella_id = cartella_padre_id
    
    # Elimina la cartella
    db.session.delete(cartella)
    db.session.commit()
    
    num_corse = len(corse_in_cartella)
    if num_corse > 0:
        destinazione = f"cartella padre" if cartella_padre_id else "root"
        flash(f'Cartella "{nome_cartella}" eliminata. {num_corse} prove spostate in {destinazione}.', 'success')
    else:
        flash(f'Cartella "{nome_cartella}" eliminata con successo.', 'success')
    
    return redirect(url_for('main.visualizza_dati'))

@folder_blueprint.route('/sposta-corsa', methods=['POST'])
def sposta_corsa():
    """Sposta una corsa in una cartella diversa"""
    from flask import jsonify
    
    race_id = request.form.get('race_id')
    cartella_id = request.form.get('cartella_id')
    
    if not race_id:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'success': False, 'message': 'ID corsa obbligatorio'})
        flash('ID corsa obbligatorio', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Trova la corsa
    race = Race.query.get(race_id)
    if not race:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'success': False, 'message': 'Corsa non trovata'})
        flash('Corsa non trovata', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Converte cartella_id
    try:
        cartella_id = int(cartella_id) if cartella_id and cartella_id != '' and cartella_id != 'null' else None
    except ValueError:
        cartella_id = None
    
    # Verifica che la cartella esista (se specificata)
    if cartella_id:
        cartella = Cartella.query.get(cartella_id)
        if not cartella:
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                return jsonify({'success': False, 'message': 'Cartella di destinazione non trovata'})
            flash('Cartella di destinazione non trovata', 'danger')
            return redirect(url_for('main.visualizza_dati'))
        destinazione = f'cartella "{cartella.nome}"'
    else:
        destinazione = "root"
    
    # Sposta la corsa
    race.cartella_id = cartella_id
    db.session.commit()
    
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({'success': True, 'message': f'Corsa "{race.name}" spostata in {destinazione}'})
    
    flash(f'Corsa "{race.name}" spostata in {destinazione}', 'success')
    return redirect(url_for('main.visualizza_dati'))

@folder_blueprint.route('/rinomina-cartella', methods=['POST'])
def rinomina_cartella():
    """Rinomina una cartella esistente"""
    cartella_id = request.form.get('cartella_id')
    nuovo_nome = request.form.get('nuovo_nome', '').strip()
    
    if not cartella_id or not nuovo_nome:
        flash('ID cartella e nuovo nome sono obbligatori', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    # Trova la cartella
    cartella = Cartella.query.get(cartella_id)
    if not cartella:
        flash('Cartella non trovata', 'danger')
        return redirect(url_for('main.visualizza_dati'))
    
    vecchio_nome = cartella.nome
    cartella.nome = nuovo_nome
    db.session.commit()
    
    flash(f'Cartella rinominata da "{vecchio_nome}" a "{nuovo_nome}"', 'success')
    return redirect(url_for('main.visualizza_dati'))
