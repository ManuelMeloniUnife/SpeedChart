@echo off
echo ===================================
echo    Installazione di SpeedChart
echo ===================================
echo.

REM Verifica se Python è installato
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python non è installato. Avvio dell'installer di Python...
    start "" "python_installer\python-3.9.13-amd64.exe" /quiet PrependPath=1
    echo Attendi che l'installazione di Python sia completata...
    echo Quando l'installazione è terminata, chiudi questa finestra e riavvia lo script.
    pause
    exit
)

echo Python è installato. Creazione dell'ambiente virtuale...

REM Crea un file di log per l'installazione
echo Log di installazione SpeedChart > install_log.txt
echo Data: %date% %time% >> install_log.txt
echo. >> install_log.txt

echo Creazione ambiente virtuale... >> install_log.txt
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRORE: Creazione ambiente virtuale fallita >> install_log.txt
    echo Errore nella creazione dell'ambiente virtuale.
    pause
    exit /b 1
)

echo Installazione delle dipendenze... >> install_log.txt
call venv\Scripts\activate.bat

REM Prima prova a installare dal PyPI
echo Tentativo di installazione da PyPI... >> install_log.txt
pip install -r requirements.txt >> install_log.txt 2>&1
set PIP_RESULT=%errorlevel%

REM Se fallisce, prova a installare dai pacchetti locali
if %PIP_RESULT% neq 0 (
    echo Installazione online fallita, tentativo di utilizzare pacchetti locali... >> install_log.txt
    
    if exist "backup_packages" (
        echo Installazione dai pacchetti di backup... >> install_log.txt
        pip install --no-index --find-links=backup_packages -r requirements.txt >> install_log.txt 2>&1
        set PIP_RESULT=%errorlevel%
    ) else (
        echo Cartella backup_packages non trovata >> install_log.txt
    )
)

if %PIP_RESULT% neq 0 (
    echo ERRORE: Installazione dipendenze fallita >> install_log.txt
    echo Errore nell'installazione delle dipendenze. Controlla install_log.txt per maggiori dettagli.
    pause
    exit /b 1
)

echo.
echo ===================================
echo Installazione completata con successo!
echo.
echo Per avviare SpeedChart, esegui:
echo  - avvia_speedchart.bat
echo ===================================
echo.

echo Creazione di un collegamento sul desktop...
echo Set oWS = WScript.CreateObject("WScript.Shell") > createShortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\SpeedChart.lnk" >> createShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> createShortcut.vbs
echo oLink.TargetPath = "%~dp0avvia_speedchart.bat" >> createShortcut.vbs
echo oLink.WorkingDirectory = "%~dp0" >> createShortcut.vbs
echo oLink.Description = "SpeedChart" >> createShortcut.vbs
echo oLink.IconLocation = "%~dp0static\img\favicon.ico" >> createShortcut.vbs
echo oLink.Save >> createShortcut.vbs
cscript //nologo createShortcut.vbs
del createShortcut.vbs

echo Installazione completata! >> install_log.txt

echo.
echo Vuoi avviare SpeedChart adesso?
choice /c SN /m "Premi S per Sì, N per No"
if %errorlevel% equ 1 (
    echo Avvio SpeedChart...
    call avvia_speedchart.bat
) else (
    echo Puoi avviare SpeedChart in qualsiasi momento facendo doppio clic sul collegamento sul desktop.
)

pause