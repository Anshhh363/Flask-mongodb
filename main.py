from flask import Flask, request, jsonify
import schemas.schemas as schm
from pydantic import ValidationError
from flask_pymongo import PyMongo, ObjectId
from security.passHash import hashpass


app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# connectivity code for connection of mongodb and flask app
# app.config["MONGO_URI"] = "mongodb://localhost:27017/ProjectDatabase"
app.config["MONGO_URI"] = "mongodb://mongo:27017/local"
db = PyMongo(app).db


# try:
#     # This line will attempt to create a client
#     # If the connection is successful, it means the connection is established.
#     client = db.client
#     print("Connected to MongoDB successfully.")
# except Exception as e:
#     print(f"Connection to MongoDB failed: {str(e)}")


# route for creating a user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        # Create a user document using the schema
        user = schm.User(name=name, email=email, password=hashpass(password))

        # Convert the user object to a dictionary
        user_dict = dict(user)
        # Parse the JSON data into a Pydantic model
        # data = request.get_json()
        # user = schm.User(**data)
        userInsert = db.Users.insert_one(user_dict)
        # objectID = userInsert.inserted_id

        # Return a JSON response with the user data
        response_data = {
            "message": "User created successfully",
            "user": str(user_dict),
        }
        return response_data

    except ValidationError as e:
        # If the JSON data doesn't match the Pydantic model, return a 400 Bad Request response
        return jsonify({"error": str(e)}), 400


# route for getting a user by its id(objectid)
@app.route("/users/<id>")
def user_profile(id):
    user = db.Users.find_one_or_404({"_id": ObjectId(id)})
    user["_id"] = str(user["_id"])
    return jsonify(user)


# route for getting all users
@app.route("/users")
def list_user_profiles():
    # Retrieve all documents from the collection
    users = db.Users.find()

    # Convert the cursor to a list of dictionaries
    users_list = []
    for user in users:
        user["_id"] = str(user["_id"])
        users_list.append(user)

    # Return the JSON response
    return jsonify(users_list)


# route for updating user through its id(object)
@app.route("/users/<id>", methods=["PUT"])
def update_user_profile(id):
    data = request.get_json()
    update_query = {"$set": data}
    user = db.Users.find_one_and_update({"_id": ObjectId(id)}, update_query)
    if user is None:
        return "User not found", 404
    return "user updated successfully"


# route for deleting a user
@app.route("/users/<id>", methods=["DELETE"])
def delete_user_profile(id):
    user = db.Users.delete_one({"_id": ObjectId(id)})
    if user is None:
        return "User not found", 404
    return "user deleted successfully"


if __name__ == "__main__":
    app.run(debug=True, port=8002, host="0.0.0.0")
