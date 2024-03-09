import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import spotipy
import spotipy.util as util
from dotenv import load_dotenv
load_dotenv()


username = os.getenv("SPOTIPY_USERNAME")

try:
    token=util.prompt_for_user_token(username)
except:
    os.remove(f".cache-{username}")
    token=util.prompt_for_user_token(username)
spotipyObject = spotipy.Spotify(auth=token)
user = spotipyObject.current_user()

spotify_playlist_id=input("Paste the url here : ")
m=spotify_playlist_id.find("t/")+2
n=spotify_playlist_id.find("?")
spotify_playlist_id=spotify_playlist_id[m:n:]

res=spotipyObject.playlist(spotify_playlist_id)
youtube_playlist_name=res["name"]
spotify_tracks_dict=spotipyObject.playlist_tracks(spotify_playlist_id)
spotify_tracks=[]
for i in spotify_tracks_dict["items"]:
    spotify_tracks.append(i["track"]["name"] + " " + i["track"]["album"]["artists"][0]["name"])

print("\nTracks in the provided spotify playist are :")
for i in spotify_tracks:
    print(i)



scope=os.getenv("YOUTUBE_SCOPE")
credentials=None

if os.path.exists("token.pickle"):
    with open("token.pickle","rb") as token:
        credentials = pickle.load(token)

if not credentials or not credentials.valid:

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file("ytsec.json",
        scopes=[scope],)
        flow.run_local_server(prompt="consent",authorization_prompt_message="")
        credentials = flow.credentials

        with open("token.pickle","wb") as f:
            pickle.dump(credentials, f)


youtube = build("youtube","v3",credentials=credentials)

res=youtube.playlists().insert(part="snippet,status",body={"snippet":{"title": youtube_playlist_name },"status" :{"privacyStatus": "public"}}).execute()
youtube_playlist_id=res["id"]

for track in spotify_tracks:
    res=youtube.search().list(q=track,part="id",type='video',maxResults=1).execute()
    res_kind=res["items"][0]["id"]["kind"]
    res_videoid=res["items"][0]["id"]["videoId"]
    res_body={
        "snippet":{
            "playlistId" : youtube_playlist_id,
            "resourceId" : {
                'kind': res_kind,
                "videoId": res_videoid
            }
        }
    }
    res=youtube.playlistItems().insert(part="snippet",body=res_body).execute()


youtube_playlist_url = f"https://www.youtube.com/playlist?list={youtube_playlist_id}"
print(youtube_playlist_url)