"""Docstring
Spotify Early Wrapped By Miguel Monreal
On 8/08/24"""

from flask import Flask, redirect, request, render_template, url_for, session
import requests
import urllib.parse
import os
from dotenv import load_dotenv
# loading variables from .env file

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("session_key")

#API credentials
redirect_uri = "http://localhost:5000/callback"
scopes = "user-top-read user-read-private user-read-email"

#Authentication URL's
auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"

#this link can be changed, might use queries instead of something specific later on
user_info_url = "https://api.spotify.com/v1/me/top/tracks?limit=10"


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
    #Main()
    FindTopSongs()
    return redirect(url_for("Results"))

def FindTopSongs():
    #gets the auth key from a dictionary called request.arg
    code = request.args.get("code")

    #checks if the code is null
    if not code:
        print("No code found in request.")

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

        #makes a dictionary to be able to authorize with the taken access token
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        #gets the data
        user_response = requests.get(user_info_url, headers=headers)
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
    else:
        print(f"Failed to get access token.\n Error Code: {auth_response.status_code}\n {auth_response.text}")

@app.route("/main")
def Main():
    FindTopSongs()
    #return render_template("index.html", outcome=outcome)

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

if __name__ == "__main__":
    app.run(debug=True)


"""if items == "album":
                                for item in album[items]:
                                    #print(item, album[items][item], "\n\n")
                                    if item == "album_type":
                                        top_songs.append(album[items]["name"])
                            elif items == "name":
                                print(album[items])"""