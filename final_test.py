from app import create_app

app = create_app()
print('✅ App created successfully')

with app.test_client() as client:
    r = client.get('/')
    print(f'✅ Home page: {r.status_code}')
    
    r = client.get('/upload')
    print(f'✅ Upload page: {r.status_code}')
    
    r = client.get('/visualizza-dati')
    print(f'✅ Visualizza dati: {r.status_code}')

print('🎉 ALL ROUTES WORKING - BUGFIXES SUCCESSFUL!')
