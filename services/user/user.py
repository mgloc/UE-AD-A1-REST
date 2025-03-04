import json
import os
import time
from pathlib import Path

import requests
# .env imports
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request

# Getting env variables
dotenv_path = Path('../../.env')
load_dotenv(dotenv_path=dotenv_path)
IMDB_API_KEY = os.getenv('IMDB_KEY')

# Flask app
app = Flask(__name__)

# Variables
PORT = os.getenv('USER_PORT')
HOST = '0.0.0.0'

MOVIE_PORT = os.getenv('MOVIE_PORT')
BOOKING_PORT = os.getenv('BOOKING_PORT')

MOVIE_URL = f"http://movie:{MOVIE_PORT}"
BOOKING_URL = f"http://booking:{BOOKING_PORT}"
BASE_URL = f"http://{HOST}:{PORT}"

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# Gets all the users datas from the JSON
@app.route("/users", methods=['GET'])
def get_users():
    return make_response(jsonify(users), 200)


# Gets user datas from its ID
@app.route("/users/<userid>", methods=['GET'])
def get_user_by_id(userid):
    for user in users:
        if userid == user["id"]:
            return make_response(jsonify(user), 200)
    return make_response(jsonify({'error': 'id not found'}))


# Create a user from a given ID
@app.route("/users/<userid>", methods=['POST'])
def create_user(userid):
    req = request.get_json()

    for user in users:
        if str(user["id"]) == str(userid):
            return make_response(jsonify({"error": "user ID already exists"}), 409)

    res = {
        'id': req["id"],
        'name': req["name"],
        'last_active': int(time.time()),
    }

    users.append(res)
    res = make_response(jsonify({"message": "user added"}), 200)
    return res


# Get user bookings from the user ID
@app.route("/booking/<userid>")
def get_users_booking(userid):
    print(f'{BOOKING_URL}/bookings/{userid}')
    try:
        res = requests.get(f'{BOOKING_URL}/bookings/{userid}')
    except:
        return make_response(jsonify({'error': 'error fetching booking microservice'}), 400)
    if not (res.ok): return make_response(jsonify({'error': 'error user don\'t have bookings'}), 400)
    response = json.loads(res.text)

    return make_response(jsonify(response["dates"]), 200)


# Get the movies booked from the user ID
@app.route("/allmoviesbooked/<userid>")
def get_all_movies_booked(userid):
    try:
        res = requests.get(f'{BASE_URL}/booking/{userid}')
    except:
        return make_response(jsonify({'error': 'error fetching user microservice'}))

    dates = json.loads(res.text)
    print(dates)

    movie_list = []
    for date in dates:
        print(date)
        for movie in date["movies"]:
            try:
                res = json.loads(requests.get(f'{MOVIE_URL}/movies/{movie}').text)
                movie_list.append(res)
            except:
                return make_response(jsonify({'error': 'error fetching movie microservice'}))
    return make_response(jsonify(movie_list))


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
