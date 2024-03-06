import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
app.app_context().push()
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route("/drinks")
def retrieve_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        list_of_drinks = []
        for drink in drinks:
            list_of_drinks.append(drink.short())

        return jsonify(
            {
                "success": True,
                "drinks": list_of_drinks,
            }
        )
    except AuthError as e:
        abort(e.status_code)
    except:
        abort(422)


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        list_of_drinks = []
        for drink in drinks:
            list_of_drinks.append(drink.long())

        return jsonify(
            {
                "success": True,
                "drinks": list_of_drinks,
            }
        )
    except AuthError as e:
        abort(e.status_code)
    except:
        abort(422)


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    new_title = body.get("title")
    recipe_data = body.get("recipe")
    new_recipe = json.dumps(recipe_data)

    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        drinks = Drink.query.order_by(Drink.id).all()
        list_of_drinks = []
        for drink in drinks:
            list_of_drinks.append(drink.long())

        return jsonify(
            {
                "success": True,
                "drinks": list_of_drinks,
            }
        )

    except AuthError as e:
        abort(e.status_code)
    except:
        abort(422)


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    body = request.get_json()
    new_title = body.get("title")
    recipe_data = body.get("recipe")

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if new_title is not None:
            if new_title != drink.title:
                drink.title = new_title

        if recipe_data is not None:
            new_recipe = json.dumps(recipe_data)
            if new_recipe != drink.recipe:
                drink.recipe = new_recipe

        drink.update()
        updated_drink = Drink.query.get(drink_id)
        list_of_drink = []
        list_of_drink.append(updated_drink.long())

        return jsonify(
            {
                "success": True,
                "drinks": list_of_drink,
            }
        )

    except AuthError as e:
        abort(e.status_code)


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify(
            {
                "success": True,
                "delete": drink.id,
            }
        )
    except AuthError as e:
        abort(e.status_code, e.error)


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": 404,
            "message": "resource not found"
        }
    ), 404


@app.errorhandler(AuthError)
def autherror_handler(ex):
    return jsonify(
        {
            "success": False,
            "error": ex.status_code,
            "message": ex.error["description"]
        }
    ), ex.status_code
