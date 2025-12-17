import re
import sys
import emoji
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
TOKEN_ENDPOINT = "https://scarrletrain.netlify.app/.netlify/functions/spotifyToken"

def sanitize_playlist_name(name, fallback_prefix="Playlist", index=None):
    # Remove invalid filesystem and non-ASCII characters
    clean_name = re.sub(r'[<>:"/\\|?*]+|[^\x00-\x7F]+', '', name).strip()
    if clean_name:
        return clean_name

    # If name is empty, try demojizing
    emoji_desc = emoji.demojize(name, language='en')
    emoji_words = re.findall(r':(.*?):', emoji_desc)
    if emoji_words:
        return '_'.join(emoji_words)

    # Fallback to default name
    return f"{fallback_prefix}_{index}" if index else fallback_prefix

def get_user_playlists(sp, user_id):
    return sp.user_playlists(user_id, limit=50)['items']

def prompt_playlist_selection():
    print("Please enter all playlist numbers, separated by spaces:")
    return list(set(re.findall(r'\d+', input())))

def save_selected_playlists(dictionary, selected, filename="playlist_links.csv"):
    with open(filename, "w", encoding="utf-8") as f:
        for num in selected:
            if int(num) in dictionary:
                name, link = dictionary[int(num)]
                f.write(f"{name},{link}\n")


def main():
    def get_access_token():
        r = requests.get(TOKEN_ENDPOINT)
        r.raise_for_status()
        return r.json()["access_token"]

    sp = spotipy.Spotify(auth=get_access_token())

    user_id = sys.argv[1]
    user_info = sp.user(user_id)
    print("Current user: " + user_info['display_name'])

    print("What playlists would you like to download?")
    playlists = get_user_playlists(sp, user_id)

    playlist_dict = {}
    for idx, playlist in enumerate(playlists, start=1):
        name = sanitize_playlist_name(playlist['name'], index=idx)
        link = f"https://open.spotify.com/playlist/{playlist['id']}"
        playlist_dict[idx] = (name, link)
        print(f"{idx}: {name}")

    selected = prompt_playlist_selection()
    save_selected_playlists(playlist_dict, selected)

if __name__ == "__main__":
    main()
