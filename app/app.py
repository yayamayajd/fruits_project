from flask import Flask, request, jsonify, render_template,redirect,url_for
from app.models import db, Fruit, FruitReview, FruitUser,User,Place,ReviewUser
from sqlalchemy.exc import IntegrityError
from config import Config

app = Flask(__name__, template_folder="../templates",static_folder="../static")

app.config.from_object(Config)
db.init_app(app)  #init DB for Flask



@app.route("/health")
def health_check():
    return jsonify({"status":"health"}),200  #for k8s health check probe


#index page show the introuduction
@app.route('/')
def index():
    return render_template('index.html')






#Fruit part

@app.route('/fruits',methods=["GET"])
def show_list_and_query_fruits():
    search_key = request.args.get("search_key")
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 每页显示20个水果

    if search_key:
        #check all the official name and return a list incl the results
        #.filter is condition such like WHERE in SQL
        fruits = db.session.execute(
            db.select(Fruit).filter(Fruit.official_name.ilike(f"%{search_key}%"))
        ).scalars().all() 
        print("here is the result:",fruits)

        if not fruits:
            return render_template('no_search_result.html')

        return render_template('list_fruits.html', fruits=fruits,pagination=None)                                  #前端页面
    
    

    pagination = Fruit.query.paginate(page=page, per_page=per_page, error_out=False)
    fruits = pagination.items
    return render_template(
        'list_fruits.html',
        fruits=fruits,
        pagination=pagination,
        next_url=url_for('show_list_and_query_fruits', page=pagination.next_num) if pagination.has_next else None,
        prev_url=url_for('show_list_and_query_fruits', page=pagination.prev_num) if pagination.has_prev else None
    )


@app.route('/fruits/add', methods=['POST','GET'])   #添加成功之后是否可以重新定向到首页？
def add_fruit():
    if request.method == "POST":
        data = request.form
        tried_date = data.get("tried_date")
        if not tried_date:
            tried_date = None
        fruit = Fruit(
            official_name=data["official_name"], #第一句因为名字不能为空所以是硬性校验
            scientific_name=data.get("scientific_name"), #之后的.get都是可选字段，可以为空，所以用.get
            image_url=data.get("image_url"),
            cultivar=data.get("cultivar"),
            other_links=data.get("other_links"),
            special_condition=data.get("special_condition"),
            tried_date=tried_date
        )
        db.session.add(fruit)
        db.session.commit()
        print("fruit information has beed added:",fruit.official_name)
        return redirect(url_for('show_list_and_query_fruits'))
    return render_template('add_fruit.html')
    





@app.route('/fruits/<int:id>',methods=['GET'])
def show_fruit(id):
    fruit = db.session.get(Fruit, id)
    if not fruit:
        print("no such fruit!")
        return render_template('no_search_result.html')
    users = User.query.all()
    reviews = FruitReview.query.filter_by(fruit_id=id).all()
    

    #return jsonify(fruit.to_dict())
    return render_template('fruit_detail.html', fruit=fruit,reviews=reviews,users=users)                                       #前端页面




@app.route('/fruits/<int:id>/update',methods=['GET','POST'])
def update_fruit_info(id):
    fruit = db.session.get(Fruit, id)
    if not fruit:
        return render_template('no_search_result.html')
    
    if request.method == 'POST':
        data = request.form
        if "official_name" in data:
            fruit.official_name = data["official_name"]
        if "scientific_name" in data:
            fruit.scientific_name = data["scientific_name"]
        if "image_url" in data:
            fruit.image_url = data["image_url"]
        if "tried_date" in data:
            fruit.tried_date = data["tried_date"]
        else:
            fruit.tried_date = None
        if "cultivar" in data:
            fruit.cultivar = data["cultivar"]
        if "special_condition" in data:
            fruit.special_condition = data["special_condition"]
        if "other_links" in data:
            fruit.other_links = data["other_links"]  

        db.session.commit()

        return redirect(url_for('show_fruit', id=fruit.id))
    return render_template('update_fruit.html', fruit=fruit)
    
    
    


@app.route('/fruits/<int:id>/delete',methods=['POST'])
def delete_fruit(id):
    fruit = db.session.get(Fruit, id)
    if not fruit:
        return render_template('no_search_result.html')
    
    FruitUser.query.filter_by(fruit_id=id).delete()

    for review in fruit.reviews:
        ReviewUser.query.filter_by(review_id=review.id).delete()

    db.session.delete(fruit)
    db.session.commit()
    return redirect(url_for('show_list_and_query_fruits'))

    





















#Review part


@app.route('/fruits/<int:id>/reviews', methods=['POST','GET'])
def new_review(id):
    #if not the post then show all fruit and reviews
    fruit = db.session.get(Fruit, id)
    if not fruit:
        return render_template('no_search_result.html')
    
    if request.method == 'GET':
        reviews = FruitReview.query.filter_by(fruit_id=id).all()
        users = User.query.all()
        print("Users:", users)   
        return render_template('review.html', fruit=fruit, reviews=reviews, users=users)
    
    data = request.form
    user_id = data.get("user_id")

    print(f"User ID: {user_id}")

    taste_score = int(data.get("taste_score",0))
    experience_score = int(data.get("experience_score",0))
    review = data.get("review")

    
    
    user = db.session.get(User,user_id)
    if not user:
        return render_template('no_search_result.html')
    
    if not ( 0 <= taste_score <= 10 and 0 <= experience_score <= 10):
        return jsonify({"error":"the score can be only between 0-10!"}),400
    
    
    
    new_review = FruitReview(
        fruit_id=id,
        taste_score=taste_score,
        experience_score=experience_score,
        review=review
    )

    db.session.add(new_review)
    db.session.commit()

    review_user = ReviewUser(review_id=new_review.id, user_id=user.id)
    db.session.add(review_user)
    db.session.commit()

    return redirect(url_for('show_fruit', id=id))






#modify review
@app.route('/fruits/<int:review_id>/update',methods=['GET','POST'])
def update_review(review_id):
    review = db.session.get(FruitReview, review_id)
    if not review:
        print("no such review!")
        return render_template('no_search_result.html'),404
    
    if request.method == 'GET':
        return render_template('update_review.html', review=review)

    if request.method == 'POST':    
        data = request.form
        try:
            if "experience_score" in data:

                experience_score = int(data["experience_score"])
                if not 0 <= experience_score <= 10:
                    return jsonify({"error":"the score can be only between 0-10!"}),400      
                review.experience_score = experience_score
            
            if "taste_score" in data:

                taste_score = int(data["taste_score"])
                if not 0 <= taste_score <= 10:
                    return jsonify({"error":"the score can be only between 0-10!"}),400        
                review.taste_score = taste_score

                    
            if "review" in data:
                review.review = data["review"]

            db.session.commit()
            print(f"review {review_id} has been updated!")
            return redirect(url_for('show_fruit', id=review.fruit_id)) 
    
        except ValueError:
            return jsonify({"error":"must be a INTERGER!"}),400




#delete review
@app.route('/fruits/<int:review_id>/delete_review', methods=['POST'])
def delete_review(review_id):
    review = db.session.get(FruitReview, review_id)  

    if not review:
        print("no such review!")
        return render_template('no_search_result.html')
    
    db.session.delete(review)
    db.session.commit()
    print(f"review {review_id} deleted")
    return redirect(url_for('show_fruit', id=review.fruit_id))  























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

    return redirect(url_for('index'))


#show all user
@app.route('/users', methods=['GET'])
def show_user():
    users = db.session.execute(db.select(User)).scalars().all()
    return render_template('list_users.html', users=users)



#modify user
@app.route('/users/<int:id>/update',methods=['POST'])
def update_user(id):
    user = db.session.get(User, id)  #先把对应的用户从db中找出来

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
    
    return redirect(url_for('show_user'))


#delete user
@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = db.session.get(User, id)  
    if not user:
        return render_template('no_search_result.html')
    
    FruitUser.query.filter_by(user_id=id).delete()

    ReviewUser.query.filter_by(user_id=id).delete()

    db.session.delete(user)
    db.session.commit()
    
    return redirect(url_for('show_user')) 










#user_fruits_list related


@app.route('/user/<int:id>/user_fruits_list',methods=['GET'])
def show_user_fruits_list(id):
    user = db.session.get(User, id) 
    if not user:
        return render_template('no_search_result.html'),404
    
    if not user.fruits_eaten_by_user:
        return render_template('no_search_result.html'),404
    
    fruit_list = [
        {
        "id": fruit.id,
        "official_name": fruit.official_name
        }
        for fruit in user.fruits_eaten_by_user
    ]
    return render_template('user_fruit_list.html', user=user, fruits=fruit_list)



@app.route('/add_fruit_to_user_fruit_list/<int:fruit_id>', methods=['POST'])
def add_fruit_to_user_from_fruit_detail(fruit_id):
    fruit = db.session.get(Fruit, fruit_id)
    if not fruit:
        return render_template('no_search_result.html'), 404

    user_id = request.form.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        return render_template('no_search_result.html'), 404

    if fruit in user.fruits_eaten_by_user:
        return jsonify({"error": "This fruit is already in the user's list!"}), 400

    user.fruits_eaten_by_user.append(fruit)

    db.session.commit()

    print(f"Fruit '{fruit.official_name}' added to {user.name}'s list!")
    return redirect(url_for('show_user_fruits_list', id=user.id))



@app.route('/user/<int:id>/remove_fruit/<int:fruit_id>', methods=['POST'])
def remove_fruit_from_user(id, fruit_id):
    user = db.session.get(User,id)
    fruit = db.session.get(Fruit,fruit_id)
    if not user or not fruit:
        return jsonify({"error": "This fruit is not in the user's list!"}), 404
    
    if fruit in user.fruits_eaten_by_user:
        user.fruits_eaten_by_user.remove(fruit)

        db.session.commit()

        print(f"Fruit removed from user's list!")
        return redirect(url_for('show_user_fruits_list', id=id))
    return render_template("no_search_result.html"),404






























#I keep the place and in coming part like vidoe to the next interation(V2.0). 
#Place part
@app.route('/places/add',methods=['POST','GET'])
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
@app.route('/places/<int:id>',methods=['POST'])
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
