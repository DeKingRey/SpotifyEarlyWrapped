"""Docstring
Spotify Early Wrapped By Miguel Monreal
On 8/08/24"""

"""Next add buttons to html to customise things like limit and length of time"""

from flask import Flask, redirect, request, render_template, url_for, session
import requests
import urllib.parse
import os
from dotenv import load_dotenv
import sys
# loading variables from .env file

#project_folder = '/home/KingRey/mysite'  # Adjust the path as needed
#if project_folder not in sys.path:
#    sys.path.append(project_folder)

# Load environment variables

#load_dotenv(os.path.join(project_folder, '.env'))

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("session_key")

#API credentials
redirect_uri = "http://localhost:5000/callback"
#redirect_uri = "https://KingRey.pythonanywhere.com/callback"
scopes = "user-top-read user-read-private user-read-email"

#Authentication URL's
auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"

#this link can be changed, might use queries instead of something specific later on
user_info_url = "https://api.spotify.com/v1/me/top/tracks"


@app.route("/")
def Authorization():
    #redirects to the authentication page
    params = {
        "client_id": os.getenv("client_id"),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes
    }

    #this gets the authentication url and encodes it with url lib
    auth_request_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

    #redirects
    return redirect(auth_request_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        print("No code found in request.")
    session["code"] = code
    session["profile_pic"] = GetProfilePic(code)
    return redirect(url_for("Home"))
    #return redirect(url_for("Filters", code=code))

@app.route("/home")
def Home():
    profile_pic = session.get("profile_pic")
    return render_template("home.html", profile_pic=profile_pic)

@app.route("/filters", methods=["GET", "POST"])
def Filters():
    code = session.get("code")
    if request.method == "POST":
        print("post")
        timeframe = request.form["timeframe"]
        limit = request.form["limit"]

        session["timeframe"] = timeframe
        session["limit"] = limit

        FindTopSongs(code, timeframe, limit)
        return redirect(url_for("Results"))
    
    timeframe = session.get("timeframe", "")
    limit = session.get("limit", "")

    return render_template("filters.html")

def FindTopSongs(code, timeframe, limit):
    #gets the auth key from a dictionary called request.arg
    #code = request.args.get("code")

    #gets the sessions acess token if it exists
    access_token = session.get("access_token")

    #if it doesn't exist it will get it
    if not access_token:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret")
        }

        #sends out a post to the API of the data
        auth_response = requests.post(token_url, data=data)

        if auth_response.status_code == 200:
            #gets the tokens from the response
            tokens = auth_response.json()
            #gets the access token specifically
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")

            session["access_token"] = access_token
            session["refresh_token"] = refresh_token
        else:
            print(f"Failed to get access token.\n Error Code: {auth_response.status_code}\n {auth_response.text}")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "time_range": timeframe,
        "limit": limit
    }

    print(f"Timeframe: {timeframe} \n Limit: {limit}")

    user_response = requests.get(user_info_url, headers=headers, params=params)

    if user_response.status_code == 401:
        access_token = refresh_access_token()

        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            user_response = requests.get(user_info_url, headers=headers, params=params)

    #gets the data
    if user_response.status_code == 200:
        user_data = user_response.json()
        top_songs = []
        for albums in user_data:
            if albums == "items":
                for album in user_data[albums]:
                    for items in album:
                        if items == "name":
                            top_songs.append(album[items])
        session["results"] = top_songs                             
    else:
        print(f"Failed to get user data.\n Error Code: {user_response.status_code}\n {user_response.text}")

def refresh_access_token():
    refresh_token = session.get("refresh_token")
    
    if refresh_token:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret")
        }
        
        # Send request to refresh the access token
        auth_response = requests.post(token_url, data=data)
        
        if auth_response.status_code == 200:
            tokens = auth_response.json()
            access_token = tokens.get("access_token")
            
            # Store the new access token in the session
            session["access_token"] = access_token
            print("Access token refreshed.")
            return access_token
        else:
            print(f"Failed to refresh access token.\n Error Code: {auth_response.status_code}\n {auth_response.text}")
            return None
    else:
        print("No refresh token available.")
        return None


@app.route("/results")
def Results():
    i = 0
    outcome = []
    #need to get the results if the album type is not SINGLE
    results = session.get("results", [])
    for result in results:
        i += 1
        outcome.append(f"{i}. {result}\n")
    
    return render_template("index.html", outcome=outcome)

def GetProfilePic(code):
    user_profile_url = "https://api.spotify.com/v1/me"
    access_token = session.get("access_token")

    #if it doesn't exist it will get it
    if not access_token:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret")
        }

        #sends out a post to the API of the data
        auth_response = requests.post(token_url, data=data)

        if auth_response.status_code == 200:
            #gets the tokens from the response
            tokens = auth_response.json()
            #gets the access token specifically
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")

            session["access_token"] = access_token
            session["refresh_token"] = refresh_token
        else:
            print(f"Failed to get access token.\n Error Code: {auth_response.status_code}\n {auth_response.text}")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    user_response = requests.get(user_profile_url, headers=headers)

    if user_response.status_code == 401:
        access_token = refresh_access_token()

        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            user_response = requests.get(user_profile_url, headers=headers)

    #gets the data
    if user_response.status_code == 200:
        user_data = user_response.json()
        profile_pic = user_data["images"][0]["url"]
        return profile_pic                     
    else:
        print(f"Failed to get user data.\n Error Code: {user_response.status_code}\n {user_response.text}")

#remove this when uploading to web
if __name__ == "__main__":
    app.run(debug=True)