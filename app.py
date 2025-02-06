from flask import Flask, request, jsonify, render_template
from models import db, Fruit
from sqlalchemy.exc import IntegrityError
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)  #init DB for Flask


#index page show the introuduction
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fruit/<int:id>',methods=['GET'])
def get_fruit(id):
    fruit = Fruit.query.get(id)
    if not fruit:
        print("no such fruit!")
        return jsonify({"error": "No such fruit found!"}), 404
    
    fruit_details = {column.name: getattr(fruit, column.name) for column in fruit.__table__.columns} #抄来的代码，动态返回object下所有字段
    return jsonify(fruit_details)




@app.route('/add_fruit', methods=["POST","GET"])
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


@app.route('/query_fruit',methods=["GET"])
def query_fruit():
    search_key = request.args.get("search_key")

    if search_key:
        #check all the official name and return a list incl the results
        #.filter is condition such like WHERE in SQL
        fruits = Fruit.query.filter(Fruit.official_name.ilike(f"%{search_key}%")).all() 
        print("here is the result:",fruits)
        return jsonify([fruit.to_dict() for fruit in fruits])
    return render_template('search_fruit.html')

@app.route('/delete_fruit',methods=['POST'])
def delete_fruit():
    fruit_id = request.form.get("fruit_id")
    fruit = Fruit.query.get(fruit_id) #利用id找出水果
    if fruit:
        db.session.delete(fruit)
        db.session.commit()
        print(f"the fruit {fruit.official_name}(ID {fruit.id}) has been deleted!")
        return jsonify({"meddege": f"fruit {fruit.official_name} deleted! "}),200
    print("no such fruit!")
    return jsonify({"error": "No such fruit found!"}), 404


@app.route('/fruit/<int:id>',methods=['PATCH'])
def update_fruit_info(id):
    fruit = Fruit.query.get(id)
    if not fruit:
        print("no such fruit!")
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
    print(f"the fruit {id} info has beed updated")
    return jsonify({"massage":f"fruit {fruit.official_name} info updated!"}),200


if __name__ == "__main__":
    app.run(debug=True)
