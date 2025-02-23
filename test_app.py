import pytest
from app import app, db
from config import Config
from models import Fruit, User, FruitReview,ReviewUser, FruitUser
from sqlalchemy import text  # ✅ 正确导入 text() 函数



@pytest.fixture()
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False 
    #transaction: to avoid to polute the DB but can use real DB data to do test
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    with app.app_context():
        with app.test_client() as client:
            conn = db.engine.connect()
            transaction = conn.begin()
            db.session.begin_nested()

            db.session.execute(text('DELETE FROM review_users'))
            db.session.execute(text('DELETE FROM fruit_reviews'))
            db.session.execute(text('DELETE FROM fruits_users'))
            db.session.execute(text('DELETE FROM fruits'))
            db.session.execute(text('DELETE FROM users'))  
            db.session.execute(text("ALTER SEQUENCE fruits_id_seq RESTART WITH 1"))
            db.session.execute(text("ALTER SEQUENCE fruit_reviews_id_seq RESTART WITH 1"))
            db.session.commit()

            #直接用数据里里的数据测试不会被事务回滚，要使用事务回滚必须自己提供要测试的数据
            fruit1 = Fruit(official_name="Apple", scientific_name="Malus domestica")
            fruit2 = Fruit(official_name="Mango", scientific_name="Mangifera indica")
            user = User(name="alice")
            user2 = User(name="Ella")

            db.session.add_all([fruit1, fruit2,user,user2])
            db.session.flush()

            fruit_user1 = FruitUser(fruit_id=fruit1.id, user_id = user.id)
            fruit_user2 = FruitUser(fruit_id=fruit2.id, user_id = user.id)
            db.session.add_all([fruit_user1,fruit_user2])
            db.session.commit


            review = FruitReview(
            fruit_id=fruit1.id,
            taste_score=7,
            experience_score=6,
            review="This is a test review."
            )
            db.session.add(review)
            db.session.flush()



            review_user = ReviewUser(
            review_id=review.id,
            user_id=user.id
            )
            db.session.add(review_user)

            db.session.flush()


            yield client
            db.session.rollback()
            transaction.rollback()
            conn.close()
            db.session.remove()



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
    },follow_redirects=True)
    assert response.status_code == 200



def test_add_fruit_without_redirect(client):
    response = client.post('/fruits/add', data = {
        "official_name":"test",
        "scientific_name":"test",
        "image_url":"test",
        "cultivar":"test",
        "other_links":"test",
        "special_condition":"test"
    },follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/fruits'


def test_show_fruit(client):

    fruit = Fruit.query.first()
    response = client.get(f'/fruits/{fruit.id}')
    assert response.status_code == 200


def test_update_fruit_info_without_redirect(client):
    fruit = Fruit.query.first()
    response = client.post(f'/fruits/{fruit.id}/update', data = {
            "official_name":"test",
            "scientific_name":"test",
            "image_url":"test",
            "cultivar":"test",
            "other_links":"test",
            "special_condition":"test",
            "tried_date":None
        },follow_redirects=False)
    assert response.status_code == 302
    assert response.location == f'/fruits/{fruit.id}'


def test_update_fruit_info_with_redirect(client):
    fruit = Fruit.query.first()
    response = client.post(f'/fruits/{fruit.id}/update', data = {
        "official_name":"test",
        "scientific_name":"test",
        "image_url":"test",
        "cultivar":"test",
        "other_links":"test",
        "special_condition":"test",
        "tried_date":"2024-12-12"
        },follow_redirects=True)
    assert response.status_code == 200
    assert b"Way to Get" in response.data



def test_delete_fruit(client):
    response = client.post('/fruits/2/delete')
    assert response.status_code == 302
    assert response.location == "/fruits"



def test_add_review(client):

    fruit = Fruit.query.first()
    response = client.post(f'/fruits/{fruit.id}/update', data = {
            "user_id":1,
            "taste_score":4,
            "experience_score":7,
            "review":"testtest"
        })
    assert response.status_code == 302
    


    fruit = Fruit.query.first()
    response = client.post(f'/fruits/{fruit.id}/update', data = {
            "user_id":1,
            "taste_score":11,
            "experience_score":7,
            "review":"testtest"
        })
    assert response.status_code == 302 #becuase it will return the not found html page


    fruit = Fruit.query.first()
    response = client.post(f'/fruits/{fruit.id}/update', data = {
            "user_id":888,
            "taste_score":4,
            "experience_score":7,
            "review":"testtest"
        })
    assert response.status_code == 302 #becuase it will return the not found html page




def test_update_review(client):
    review = FruitReview.query.first()

    response = client.post(f'/fruits/{review.id}/update', data = {
        "taste_score": 9,
        "experience_score": 8,
        "review": "testtetst"

    })
    assert response.status_code == 302


    



def test_delete_review(client):
    review = FruitReview.query.first()
    response = client.post(f'/fruits/{review.id}/delete')
    assert response.status_code == 302
    assert response.location == "/fruits"


def test_add_user(client):
    response = client.post('/users', data = {
        "name":"Alice"
    })
    assert response.status_code == 302

def test_show_user(client):
    response = client.get('/users')
    assert response.status_code == 200

def test_update_user(client):
    user = User.query.first()
    response = client.post(f'/users/{user.id}/update', data = {
        "name":"AAA"
    })
    assert response.status_code == 302

    response = client.post(f'/users/2048/update', data = {
    "name":"BBB"
    })
    assert response.status_code == 404 #usuer dose not exist



def test_delete_user(client):
    user = User(name="you know who")
    db.session.add(user)
    db.session.commit()
    response = client.post(f'/users/{user.id}/delete')
    print(f"{user.name} deleted")
    assert response.status_code == 302




def test_show_user_fruits_list(client):
    user = User.query.filter_by(name = "alice").first()
    response = client.get(f"/user/{user.id}/user_fruits_list")
    assert response.status_code == 200



def test_add_fruit_to_user_from_fruit_detail(client):
    user = User.query.filter_by(name = "Ella").first()
    fruit = Fruit.query.filter_by(official_name = "Mango").first()
    response = client.post(f'/add_fruit_to_user_fruit_list/{fruit.id}', data = {
        "user_id":user.id
    })
    assert response.status_code == 302
    assert fruit in user.fruits_eaten_by_user

    user = User.query.filter_by(name = "Ella").first()
    fruit = Fruit.query.filter_by(official_name = "Mango").first()
    response = client.post(f'/add_fruit_to_user_fruit_list/{fruit.id}', data = {
        "user_id":user.id
    })
    assert response.status_code == 400 #already in the list

    user = User.query.filter_by(name = "Ella").first()
    response = client.post(f'/add_fruit_to_user_fruit_list/2048', data = {
    "user_id":user.id
    })
    assert response.status_code == 404 #no such fruit


    fruit = Fruit.query.filter_by(official_name = "Mango").first()
    response = client.post(f'/add_fruit_to_user_fruit_list/{fruit.id}', data = {
        "user_id":2048
    })
    assert response.status_code == 404 #no such user




def test_remove_fruit_from_user(client):
    user = User.query.filter_by(name = "alice").first()
    fruit = Fruit.query.filter_by(official_name = "Mango").first()
    response = client.post(f'/user/{user.id}/remove_fruit/{fruit.id}')
    assert response.status_code == 302
    assert fruit not in user.fruits_eaten_by_user

    user = User.query.filter_by(name = "Ella").first()
    fruit = Fruit.query.filter_by(official_name = "Mango").first()
    response = client.post(f'/user/{user.id}/remove_fruit/{fruit.id}')
    assert response.status_code == 404 #the fruit does not in the list 

    response = client.post(f'/user/2048/remove_fruit/{fruit.id}')
    assert response.status_code == 404 #user does not exist

    response = client.post(f'/user/{user.id}/remove_fruit/2048')
    assert response.status_code == 404 #the fruit does not exist





