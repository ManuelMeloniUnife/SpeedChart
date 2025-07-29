# SpeedChart - Documentazione Struttura

## Struttura del Progetto (Pulita e Riorganizzata)

### Cartelle Principali
```
SpeedChart/
├── config/                 # Configurazioni dell'applicazione
├── routes/                 # Routes organizzate per funzionalità
├── templates/              # Template HTML
├── static/                 # File statici (CSS, JS, immagini)
├── utils/                  # Utilities e parser
├── migrations/             # Script di migrazione database
├── data/                   # Database SQLite
└── instance/               # Dati di istanza Flask
```

### Files Principali

#### Core Application
- `app.py` - Factory pattern per l'app Flask
- `models.py` - Modelli del database SQLAlchemy
- `init_db.py` - Script per inizializzare il database
- `run_speedchart.py` - Script di avvio con browser automatico

#### Dashboard e Visualizzazione
- `dash_app.py` - Dashboard Dash per visualizzazione singola corsa
- `comparison_dash.py` - Dashboard Dash per confronto corse

#### Routes (Organizzate per Funzionalità)
- `routes/main.py` - Route principali (home, upload, visualizzazione)
- `routes/api.py` - API REST per dati JSON
- `routes/team_management.py` - Gestione del team (spingitori)
- `routes/folder_management.py` - Gestione delle cartelle

#### Configurazione
- `config/__init__.py` - Configurazioni centralizzate (dev/prod)

#### Utilities
- `utils/file_parser.py` - Parser per file del computer di bordo

#### Setup e Deployment
- `requirements.txt` - Dipendenze Python
- `setup_speedchart.bat` - Script di installazione automatica
- `avvia_speedchart.bat` - Script di avvio rapido

### Modelli Database

#### Spingitore
- Gestisce piloti e spingitori del team
- Campi: nome, cognome, ruolo, attivo

#### Race (Corsa)
- Gestisce le prove/corse
- Relazione many-to-many con Spingitore tramite RaceSpingitore
- Supporta cartelle per organizzazione

#### RaceSpingitore
- Tabella di associazione per Race-Spingitore
- Include ordine di esecuzione (pilota = 1, spingitori = 2,3,4...)

#### DataPoint
- Punti dati della corsa (distanza, velocità, accelerazione, tempo)

#### Cartella
- Sistema di organizzazione gerarchica delle corse
- Supporta cartelle nidificate

### Features Implementate

#### Gestione Corse
- Upload file computer di bordo (.txt)
- Visualizzazione interattiva con grafici
- Confronto tra due corse
- Organizzazione in cartelle

#### Gestione Team
- Aggiunta/modifica/eliminazione spingitori
- Gestione ruoli (pilota/spingitore)
- Stato attivo/inattivo

#### Dashboard
- Grafici interattivi con Plotly/Dash
- Visualizzazione diretta senza Dash
- Filtri e selezione punti

### File Rimossi nella Pulizia
- `test_toggle.html` - File di test temporaneo
- `temp_view_race_direct.html` - Template temporaneo
- `prepare_distribution.bat` - File batch vuoto
- `migration_script.py` - Script migrazione obsoleto
- `__pycache__/` - Cache Python
- `backup_packages/` - Cartella backup vuota
- `routes.py` - File routes monolitico (diviso in moduli)

### Miglioramenti Apportati

#### Organizzazione
- Separazione concerns (API, views, business logic)
- Configurazione centralizzata
- Struttura modulare

#### Codice
- Eliminazione duplicazioni
- Import puliti
- Commenti standardizzati
- Error handling migliorato

#### Manutenibilità
- Factory pattern per app Flask
- Blueprint organizzati per funzionalità
- Configurazioni ambiente (dev/prod)

### Per la Versione v1.2

Questa struttura pulita è pronta per l'implementazione di:
- ApexCharts per grafici più avanzati
- Nuove funzionalità di analisi
- Miglioramenti UI/UX
- Performance optimization

### Come Usare

1. **Setup**: `setup_speedchart.bat`
2. **Avvio**: `avvia_speedchart.bat` o `python run_speedchart.py`
3. **Init DB**: `python init_db.py` (se necessario)

La struttura è ora molto più pulita, organizzata e pronta per lo sviluppo della v1.2!
