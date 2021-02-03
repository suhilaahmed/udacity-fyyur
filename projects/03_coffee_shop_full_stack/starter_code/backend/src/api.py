import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    Public permission
    This API fetches all drinks with a short description
    Return the drinks array or the error handler
    """
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    """
          Public permission
          This API fetches all drinks with a long description
          Return the drinks array or the error handler
          """
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [d.long() for d in drinks]
        }), 200
    except:
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@requires_auth('post:drinks')
def add_drink(token):
    """
         post:drinks permission
         This API creates a new drink and returns its long description
         Return the created drink info or the error handler
         """
    if request.data:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        drink = Drink(title=title, recipe=json.dumps(recipe))
        Drink.insert(drink)

        new_drink = Drink.query.filter_by(id=drink.id).first()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    else:
        abort(422)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            abort(404)

        if title is None:
            abort(400)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        updated_drink = Drink.query.filter_by(id=drink_id).first()

        return jsonify({
            'success': True,
            'drinks': [updated_drink.long()]
        })
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except:
        abort(422)
# Error Handlers
'''
Example error handling for unprocessable entity
'''


# Error handler for Unprocessable entity
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# Error handler for resource not found error
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'
    }), 404


# Error handler for internal server error
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


# Error handler for bad request
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


# Error handler for method not allowed
@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


# Error handler for unauthorised user
@app.errorhandler(401)
def unauthorised_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorised User'
    }), 401


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


# Error handler for Auth Error
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
