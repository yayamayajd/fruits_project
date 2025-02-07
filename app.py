from flask import Flask, request, jsonify, render_template
from models import db, Fruit, FruitReview, FruitUser,User,Place
from sqlalchemy.exc import IntegrityError
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)  #init DB for Flask


#index page show the introuduction
@app.route('/')
def index():
    return render_template('index.html')


#Fruit part

@app.route('/fruits', methods=["POST","GET"])
def add_fruit():
    if request.method == "POST":
        data = request.form
        print("here is the info you want to add",data)
        fruit = Fruit(
            official_name=data["official_name"], #第一句因为名字不能为空所以是硬性校验
            scientific_name=data.get("scientific_name"), #之后的.get都是可选字段，可以为空，所以用.get
            image_url=data.get("image_url"),
            cultivar=data.get("cultivar"),
            other_links=data.get("other_links"),
            special_condition=data.get("special_condition"),
            tried_date=data.get("tried_date")
        )
        db.session.add(fruit)
        db.session.commit()
        print("fruit information has beed added:",fruit.official_name)
        return jsonify({"message": "The fruit info added", "id":fruit.id, "name":fruit.official_name}),201
    
    return render_template('add_fruit.html')



@app.route('/fruit/<int:id>',methods=['GET'])
def show_fruit(id):
    fruit = Fruit.query.get(id)
    if not fruit:
        print("no such fruit!")
        return jsonify({"error": "No such fruit found!"}), 404

    return jsonify(fruit.to_dict())


@app.route('/fruits',methods=["GET"])
def query_fruit():
    search_key = request.args.get("search_key")

    if search_key:
        #check all the official name and return a list incl the results
        #.filter is condition such like WHERE in SQL
        fruits = Fruit.query.filter(Fruit.official_name.ilike(f"%{search_key}%")).all() 
        print("here is the result:",fruits)
        return jsonify([fruit.to_dict() for fruit in fruits])
    return render_template('search_fruit.html')




@app.route('/fruit/<int:id>',methods=['PATCH'])
def update_fruit_info(id):
    fruit = Fruit.query.get(id)
    if not fruit:
        return jsonify({"error": "No such fruit found!"}), 404
    
    data = request.form
    if "official_name" in data:
        fruit.official_name = data["official_name"]
    if "scientific_name" in data:
        fruit.scientific_name = data["scientific_name"]
    if "image_url" in data:
        fruit.image_url = data["image_url"]
    if "tried_date" in data:
        fruit.tried_date = data["tried_date"]
    if "cultivar" in data:
        fruit.cultivar = data["cultivar"]
    if "special_condition" in data:
        fruit.special_condition = data["special_condition"]
    if "other_links" in data:
        fruit.other_links = data["other_links"]  

    db.session.commit()
    return jsonify({"message":f"fruit {fruit.official_name} info updated!"}),200


@app.route('/fruits/<int:id>',methods=['DELETE'])
def delete_fruit(id):
    fruit = Fruit.query.get(id) #利用id找出水果
    if not fruit:
        return jsonify({"error": "No such fruit found!"}), 404
    
    db.session.delete(fruit)
    db.session.commit()
    return jsonify({"message": f"fruit {fruit.official_name} deleted! "}),200
    



#Review part
@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.form
    fruit_id = data.get("fruit_id")
    taste_score = data.get("taste_score",0)
    experience_score = data.get("experience_score",0)
    review = data.get("review")
    
    fruit = Fruit.query.get(fruit_id)
    if not fruit:
        print("no such fruit!")
        return jsonify({"error": "No such fruit found!"}), 404
    
    if not ( 0 <= taste_score <= 10 and 0 <= experience_score <= 10):
        return jsonify({"error":"the score can be only between 0-10!"}),400
    
    new_review = FruitReview(
        fruit_id=fruit_id,
        taste_score=taste_score,
        experience_score=experience_score,
        review=review
    )

    db.session.add(new_review)
    db.session.commit()

    return jsonify({"message":f"the review of {fruit.official_name} added!"}),201

@app.route('/fruit/<int:id>/reviews', methods=['GET'])
def show_fruit_review(id):
    fruit = Fruit.query.get(id)
    if not fruit:
        print("no such fruit!")
        return jsonify({"error": "No such fruit found!"}), 404
    
    reviews = FruitReview.query.filter_by(fruit_id=id).all() #模糊匹配
    return jsonify({"fruit": fruit.official_name,
                    "review":[review.to_dict() for review in reviews]}),200



#modify review
@app.route('/reviews/<int:id>',methods=['PATCH'])
def update_review(id):
    review = FruitReview.query.get(id)
    if not review:
        print("no such review!")
        return jsonify({"error": "No such review found!"}), 404
    
    data = request.form
    if "taste_score" in data:
        taste_score = data["taste_score"]

        if not 0 <= taste_score <= 10:
            return jsonify({"error":"the score can be only between 0-10!"}),400
        
        review.test_score = taste_score

    if "experience_score" in data:
       experience_score = data["experience_score"]
       if not 0 <= experience_score <= 10:
            return jsonify({"error":"the score can be only between 0-10!"}),400 
       
       review.experience_score = experience_score

    if "review" in data:
        review.review = data["review"]

    db.session.commit()
    print(f"review {id} has been updated!")
    return jsonify({"message": f"review {id} updated!"}),200


#delete review
@app.route('/review/<int:id>', methods=['DELETE'])
def delete_review(id):
    review = FruitReview.query.get(id)
    if not review:
        print("no such review!")
        return jsonify({"error": "No such review found!"}), 404
    
    db.session.delete(review)
    db.session.commit()
    print(f"review {id} deleted")
    return jsonify({"massage":f"review {id} deleted"})



#User part
#add user
@app.route('/users',methods=['POST'])
def add_user():
    data = request.form
    name = data.get("name")

    if not name:
        return jsonify({"error": "invalid input!"}), 400

    new_user = User()
    new_user.name = name

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"user {name} already exsits"}),400

    return jsonify({"message":f"User {name} added"}),201

#show all user
@app.route('/users',methods=['GET'])
def show_user():
    users = User.query.all()
    return jsonify([users.to_dict() for user in users])


#modify user
@app.route('/users/<int:id>',methods=['PATCH'])
def update_user(id):
    user = User.query.get(id) #先把对应的用户从db中找出来

    if not user:
        return jsonify({"error": "no such user found!"}), 404
    
    data = request.form #再根据前端提交的表单给用户赋值
    if "name" in data:
        user.name = data["name"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"user {user.name} already exist!"}),400
    
    return jsonify({"message":f"user {user.name} updated!"}),200

#delete user
@app.route('/users/<int:id>',methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "no such user found!"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message":f"user {user.name} deleted"}),200 

#Place part
@app.route('/places',methods=['POST'])
def add_place():
    data = request.form
    place_name = data["place_name"]
    country = data["country"]

    if not place_name or not country:
        return jsonify({"error":"place input place and country"})
    

    new_place = Place()
    new_place.place_name = place_name
    new_place.country = country

    db.session.add(new_place)

    db.session.commit()
    return jsonify({"message":f"new place {place_name} added!"})


#show place
@app.route('/places',methods=['GET'])
def show_place():
    places = Place.query.all()
    return jsonify([place.to_dict() for place in places]),200


#modify place
@app.route('/places/<int:id>',methods=['PATCH'])
def update_place(id):
    place = Place.query.get(id)

    if not place:
        return jsonify({"error": "no such place found!"}), 404
    
    data = request.form

    if "place_name" in data:
        place.place_name = data["place_name"]

    if "country" in data:
        place.country = data["country"]

    db.session.commit()
    return jsonify({"message":f"place {place.place_name} updated"}),200


#delete place
@app.route('/places/<int:id>',methods=['DELETE'])
def delete_place(id):
    place = Place.query.get(id)
    if not place:
        return jsonify({"error": "no such place found!"}), 404
    
    db.session.delete(place)
    db.session.commit()
    return jsonify({"message":f"place {place.place_name} deleted"}),200



if __name__ == "__main__":
    app.run(debug=True)
