# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app

import requests
import json

# Firebase 초기화
initialize_app()

CLIENT_ID = "57463a7493704291ba40756ea9548e4d"
CLIENT_SECRET = "0271126819da402a9c01282f1aa70d17"

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get token: {response.text}")

@https_fn.on_request()
def get_spotify_track(req: https_fn.Request) -> https_fn.Response:
    track_id = req.args.get('track_id', '1ygmHMAn6HYtCrQ4fHqD0x')
    try:
        token = get_spotify_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        response = requests.get(url, headers=headers)


        if response.status_code == 200:
            track = response.json()

            # 트랙 정보 추출
            track_info = {
                "Track Name": track["name"],
                "Artist": track["artists"][0]["name"],
                "Album": track["album"]["name"],
                "Release Date": track["album"]["release_date"],
                "Spotify URL": track["external_urls"]["spotify"],
                "Album Cover": track["album"]["images"][0]["url"],
                "Popularity": track["popularity"],
                "Duration (ms)": track["duration_ms"]
            }

            # JSON 응답 반환
            return https_fn.Response(
                json.dumps(track_info, indent=2),  # JSON 형식으로 변환
                headers={"Content-Type": "application/json"},  # Content-Type 설정
                status=200
            )
        else:
            return https_fn.Response(f"Spotify API Error: {response.text}", status=500)

    except Exception as e:
        return https_fn.Response(f"Error: {str(e)}", status=500)
