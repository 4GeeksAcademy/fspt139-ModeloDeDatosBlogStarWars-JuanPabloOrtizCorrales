"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Location
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password are required"}), 400
    user_exist = db.session.execute(db.select(User).where(
        User.email == data.get("email"))).first()

    if user_exist:
        return jsonify({"error": "User whith this email already exist"}), 400

    new_user = User(email=data.get("email"), password=data.get("password"))

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created successfuly", "User": new_user.serialize()}), 201


@app.route('/user', methods=['GET'])
def get_all_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/user/<int:user_id>/favorite', methods=['GET'])
def get_favorites_by_user_id(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    favorites = {
        "characters": [character.serialize() for character in user.character_favorites],
        "locations": [location.serialize() for location in user.location_favorites]
    }
    return jsonify(favorites), 200


@app.route('/character', methods=['POST'])
def create_character():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    character_exist = db.session.execute(db.select(Character).where(
        Character.name == data.get("name"))).first()

    if character_exist:
        return jsonify({"error": "Character already exist"}), 400

    new_character = Character(name=data.get(
        "name"), occupation=data.get("occupation", ""))

    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": "Character created successfuly", "Character": new_character.serialize()}), 201


@app.route('/user/<int:user_id>/favorite/character/<int:character_id>', methods=['POST'])
def add_character_favorite(user_id, character_id):
    user = db.session.get(User, user_id)
    character = db.session.get(Character, character_id)

    if not user:
        return jsonify({"error": "user not found"}), 404
    if not character:
        return jsonify({"error": "character not found"}), 404
    if character in user.character_favorites:
        return jsonify({"error": "character alredy in favorites"}), 400

    user.character_favorites.append(character)
    db.session.commit()
    return jsonify({"msg": "character added in favorites", "user": user.serialize()}), 200


@app.route('/user/<int:user_id>/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_character_favorite(user_id, character_id):
    user = db.session.get(User, user_id)
    character = db.session.get(Character, character_id)

    if not user:
        return jsonify({"error": "user not found"}), 404
    if not character:
        return jsonify({"error": "character not found"}), 404
    if character not in user.character_favorites:
        return jsonify({"error": "character not in favorites"}), 400

    user.character_favorites.remove(character)
    db.session.commit()
    return jsonify({"msg": "character deleted from favorites", "user": user.serialize()}), 200



@app.route('/location', methods=['POST'])
def create_location():
    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    location_exist = db.session.execute(db.select(Location).where(
        Location.name == data.get("name"))).first()

    if location_exist:
        return jsonify({"error": "location already exist"}), 400

    new_location = Location(name=data.get(
        "name"), image=data.get("image", ""))

    db.session.add(new_location)
    db.session.commit()
    return jsonify({"msg": "location created successfuly", "Location": new_location.serialize()}), 201



@app.route('/user/<int:user_id>/favorite/location/<int:location_id>', methods=['POST'])
def add_location_favorite(user_id, location_id):
    user = db.session.get(User, user_id)
    location = db.session.get(Location, location_id)

    if not user:
        return jsonify({"error": "user not found"}), 404
    if not location:
        return jsonify({"error": "location not found"}), 404
    if location in user.location_favorites:
        return jsonify({"error": "location alredy in favorites"}), 400

    user.location_favorites.append(location)
    db.session.commit()
    return jsonify({"msg": "location added in favorites", "user": user.serialize()}), 200


@app.route('/user/<int:user_id>/favorite/location/<int:location_id>', methods=['DELETE'])
def delete_location_favorite(user_id, location_id):
    user = db.session.get(User, user_id)
    location = db.session.get(Location, location_id)

    if not user:
        return jsonify({"error": "user not found"}), 404
    if not location:
        return jsonify({"error": "location not found"}), 404
    if location not in user.location_favorites:
        return jsonify({"error": "location not favorites"}), 400

    user.location_favorites.remove(location)
    db.session.commit()
    return jsonify({"msg": "location deleted from favorites", "user": user.serialize()}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
