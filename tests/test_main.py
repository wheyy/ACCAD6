from app import app

def test_redirect():
    response = app.test_client().get('/')
    assert response.status_code == 302
    
def test_connection():
    response = app.test_client().get('/upload')
    assert response.status_code == 200

def test_connection1():
    response = app.test_client().get('/edit')
    assert response.status_code == 200

def test_connection2():
    response = app.test_client().get('/calendar')
    assert response.status_code == 200
