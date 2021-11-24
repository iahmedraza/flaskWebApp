from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import  (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    unset_jwt_cookies)
from datetime import timezone, timedelta, datetime


app = Flask(__name__)
client = pymongo.MongoClient('localhost', 27017)
db = client["appDB"]
userCollection = db["users"]
jwt = JWTManager(app)
app.secret_key = "Ahmed"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)



# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

#function for required pasrse require arguments
def add_argumemts(*args):    
    requireArgs = args
    payload = request.form
    # print(request,'+++++')
    
    if payload:
        for requireArg in requireArgs:
            if not requireArg in payload:
                return {requireArg : "This feild is required."} ,400 
    else:
         return {"message": "body can not be empty"}, 400
    
    return None



@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    parser = add_argumemts("name","email","password") #will return none if required feilds are not empty
    if parser: 
        # print(parser,'--')
        return parser
    payload = request.form
    name = payload["name"].lower()
    email = payload["email"].lower()
    password = generate_password_hash(payload["password"])

    if userCollection.find_one({"email":email}):
        return render_template("register.html", error="Email already exists."), 400

    data = {
        "name": name,
        "email" : email,
        "password": password
    }
    
    userCollection.insert_one(data)
    
    return  render_template("register.html",userCreated="Account is created"), 201    



@app.route('/welcome')
@jwt_required()
def welcome():
    return render_template("welcome.html"), 200

@app.route('/', methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')

    parser = add_argumemts("email","password") #will return none if required feilds are not empty
    if parser: 
        return parser

    data = request.form
    user = userCollection.find_one({"email": data['email'].lower() }, {"_id": 1,"password":1})
    
    if user: # check with email
        hash_password = user['password']
        isPassword = check_password_hash(hash_password,data["password"]) 
        if isPassword: #check password match
            userid = str(user["_id"])
            respone = make_response(redirect(url_for("welcome")))
            access_token = create_access_token(identity = userid, fresh=True)
            refresh_token = create_refresh_token(userid)
            set_access_cookies(respone,access_token)
            return respone, 301
    

    return render_template("login.html" ,error="Invalid details."), 401 
 
@app.route('/logout')
def logout():
    response = make_response(redirect("/"))
    unset_jwt_cookies(response)
    return response, 301   

if __name__ == '__main__':
    app.run(debug=True, port= 5000)