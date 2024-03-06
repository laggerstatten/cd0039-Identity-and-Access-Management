import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)

setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type, Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )

    return response


"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
"""
db_drop_and_create_all()

# ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route('/drinks', methods=['GET'], endpoint='get_drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify(
            {
                "message": "OK",
                "success": True,
                "drinks": [drink.short() for drink in drinks]
            }
        ), 200

    except AuthError as ex:
        abort(ex.status_code, ex.error)


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the "get:drinks-detail" permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route('/drinks-detail', methods=['GET'], endpoint='drinks_detail')
@requires_auth("get:drinks-detail")
def retrieve_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify(
            {
                "message": "OK",
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }
        ), 200

    except AuthError as ex:
        abort(ex.status_code, ex.error)


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the "post:drinks" permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route('/drinks', methods=['POST'], endpoint='post_drink')
@requires_auth("post:drinks")
def create_drink(payload):
    body = request.get_json()
    new_title = body.get("title")
    recipe_data = body.get("recipe")
    new_recipe = json.dumps(recipe_data)

    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify(
            {
                "message": "OK",
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }
        ), 200

    except AuthError as ex:
        abort(ex.status_code, ex.error)


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the "patch:drinks" permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route('/drinks/<id>', methods=['PATCH'], endpoint='patch_drink')
@requires_auth("patch:drinks")
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
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify(
            {
                "message": "OK",
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }
        ), 200

    except AuthError as ex:
        abort(ex.status_code, ex.error)


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the "delete:drinks" permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:drink_id>", methods=["DELETE"], endpoint='delete_drink')
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is not None:
            drink.delete()
            drinks = Drink.query.order_by(Drink.id).all()
        else:
            abort(404)
        return jsonify(
            {
                "message": "OK",
                "success": True,
                "drinks": [drink.long() for drink in drinks]
            }
        )

    except AuthError as ex:
        abort(ex.status_code, ex.error)


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


"""
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""

"""
@TODO implement error handler for 404
    error handler should conform to general task above
"""


@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": 404,
            "message": "resource not found"
        }
    ), 404


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def autherror_handler(ex):
    return jsonify(
        {
            "success": False,
            "error": ex.status_code,
            "message": ex.error["description"]
        }
    ), ex.status_code
