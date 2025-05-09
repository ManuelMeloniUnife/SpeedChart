// static/js/script.js
// Script personalizzato per SpeedChart

// Funzione per migliorare l'interazione tabella-grafico
document.addEventListener('DOMContentLoaded', function() {
    // Gestisci click sulla tabella (implementato in dash_app.py)
    
    // Scroll smooth per la navigazione
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Animazione per alert di notifica
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);  // Auto-chiudi dopo 5 secondi
    });
});