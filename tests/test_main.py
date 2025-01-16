from app import app

def test_redirect():
    response = app.test_client().get('/')
    assert response.status_code == 302
