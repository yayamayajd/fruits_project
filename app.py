from flask import Flask, request, jsonify, render_template,redirect,url_for
from models import db, Fruit, FruitReview, FruitUser,User,Place,ReviewUser
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

@app.route('/fruits',methods=["GET"])
def show_list_and_query_fruits():
    search_key = request.args.get("search_key")
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 每页显示20个水果

    if search_key:
        #check all the official name and return a list incl the results
        #.filter is condition such like WHERE in SQL
        fruits = Fruit.query.filter(Fruit.official_name.ilike(f"%{search_key}%")).all() 
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
    fruit = Fruit.query.get(id)
    if not fruit:
        print("no such fruit!")
        return render_template('no_search_result.html')
    users = User.query.all()
    reviews = FruitReview.query.filter_by(fruit_id=id).all()
    

    #return jsonify(fruit.to_dict())
    return render_template('fruit_detail.html', fruit=fruit,reviews=reviews,users=users)                                       #前端页面




@app.route('/fruits/<int:id>/update',methods=['GET','POST'])
def update_fruit_info(id):
    fruit = Fruit.query.get(id)
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
    fruit = Fruit.query.get(id) #利用id找出水果
    if not fruit:
        return render_template('no_search_result.html')
    
    db.session.delete(fruit)
    db.session.commit()
    return redirect(url_for('show_list_and_query_fruits'))

    





















#Review part


@app.route('/fruits/<int:id>/reviews', methods=['GET'])
def show_fruit_review(id):
    fruit = Fruit.query.get(id)
        #这个页面应该直接后接水果的详细信息展示页面，水果详细信息后面应该有一个查看评论的按钮，跳转这个界面，这个页面也是展示某个水果id的评论
    if not fruit:
        print("no such fruit!")
        return render_template('no_search_result.html')
    
    reviews = FruitReview.query.filter_by(fruit_id=id).all()
    return render_template('reviews.html', fruit=fruit, reviews=reviews)






@app.route('/fruits/<int:id>/reviews', methods=['POST'])
def add_review(id):
    #if not the post then show all fruit and reviews
    fruit = Fruit.query.get(id)
    if not fruit:
        return render_template('no_search_result.html')
    
    data = request.form
    user_id = data.get("user_id")

    print(f"User ID: {user_id}")

    taste_score = int(data.get("taste_score",0))
    experience_score = int(data.get("experience_score",0))
    review = data.get("review")

    
    
    user = User.query.get(user_id)
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
@app.route('/reviews/<int:id>/update',methods=['GET','POST'])
def update_review(id):
    review = FruitReview.query.get(id)
    if not review:
        print("no such review!")
        return jsonify({"error": "No such review found!"}), 404

    if request.method == 'POST':    
        data = request.form
        if "taste_score" in data:
            taste_score = data["taste_score"]

            if not 0 <= taste_score <= 10:
                return jsonify({"error":"the score can be only between 0-10!"}),400
        
        review.taste_score = taste_score

        if "experience_score" in data:
            experience_score = data["experience_score"]
            if not 0 <= experience_score <= 10:
                return jsonify({"error":"the score can be only between 0-10!"}),400 
       
            review.experience_score = experience_score

        if "review" in data:
            review.review = data["review"]

        db.session.commit()
        print(f"review {id} has been updated!")
        return redirect(url_for('show_fruit', id=id))  # 修正为 show_fruit



#delete review
@app.route('/review/<int:id>/delete', methods=['POST'])
def delete_review(id):
    review = FruitReview.query.get(id)
    if not review:
        print("no such review!")
        return jsonify({"error": "No such review found!"}), 404
    
    db.session.delete(review)
    db.session.commit()
    print(f"review {id} deleted")
    return redirect(url_for('show_fruit', id=id))  # 修正为 show_fruit























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
@app.route('/users',methods=['GET'])
def show_user():
    users = User.query.all()
    return render_template('list_users.html', users=users)


#modify user
@app.route('/users/<int:id>/update',methods=['POST'])
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
    
    return redirect(url_for('show_user'))


#delete user
@app.route('/users/<int:id>/delete',methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "no such user found!"}), 404

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users')) 
















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
