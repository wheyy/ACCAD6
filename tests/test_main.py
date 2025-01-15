# Test for connectivity
import requests
from app import app

def test_connection():
    response = app.test_client().get('/upload')
    assert response.status_code == 200

# since we want to redirect / to /update, check if redirect is working
def test_redirect():
    response = app.test_client().get('/')
    assert response.status_code == 302

