import pytest
from app import app


@pytest.fixture()
def client():
    app.config["Testing"] = True
    with app.test_client() as client:
        yield client



def test_index_status_get(client):
    response = client.get('/')
    assert response.status_code == 200

def test_show_list_and_query_fruits(client):
    response = client.get('/fruits')
    assert response.status_code == 200


def test_add_fruit_with_redirect(client):
    response = client.post('/fruits/add', data = {
        "official_name":"test",
        "scientific_name":"test",
        "image_url":"test",
        "cultivar":"test",
        "other_links":"test",
        "special_condition":"test"
    },follow_resirects=True)
    assert response.status_code == 200
    assert b"Fruit List" in response.data #check if include the word



def test_add_fruit_without_redirect(client):
    response = client.post('/fruits/add', data = {
        "official_name":"test",
        "scientific_name":"test",
        "image_url":"test",
        "cultivar":"test",
        "other_links":"test",
        "special_condition":"test"
    },follow_resirects=False)
    assert response.status_code == 302
    assert response.location == '/fruits'


def test_show_fruit(client):
    response = client.get('/fruits/<int:id>')
    assert response.status_code == 200



