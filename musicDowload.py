import sys
import os
import time
import re
import csv
import requests
import spotipy
import spotdl
import subprocess

TOKEN_ENDPOINT = "https://scarrletrain.netlify.app/.netlify/functions/spotifyToken"
token = None

# Using Tokens

def get_access_token():
    global token

    if token != None and not token_is_expired(token):
        return token["access_token"]

    r = requests.get(TOKEN_ENDPOINT)
    r.raise_for_status()

    tok = r.json()
    tok["expires_at"] = time.time() + tok["expires_in"]

    token = tok
    return tok["access_token"]

def token_is_expired(tok, skew=60):
    return time.time() >= tok["expires_at"] - skew

def get_sp():
    return spotipy.Spotify(auth=get_access_token())

# Using Ids

def user_validity_check(user_id):
    sp = get_sp()

    try:
        return bool(sp.user(user_id)['display_name'])
    except spotipy.exceptions.SpotifyException:
        return False
    
def load_user_ids():
    user_ids = []
    try:
        with open("id.dat.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            for row in reader:
                    user_ids.append((row[0], row[1]))

    except FileNotFoundError:
        print("No User Ids found, creating file")
        
        open("id.dat.csv", "x").close()

    return user_ids

def edit_user_id(user_id = None, user_display = None):
    user_ids = load_user_ids()

    if user_id == None:
        current_id = input("Enter Spotify User Id: ").strip()
        current_display = input("Enter matching Display Name: ").strip()

        if any(current_id in tup for tup in user_ids) or any(current_display in tup for tup in user_ids):
            edit_user_id(current_id, current_display);
            return
        
        user_ids.append((current_id, current_display))

    else:
        if not any(user_id in tup for tup in user_ids):
            return 
        
        idIndex = next((i for i, v in enumerate(user_ids) if v[0] == user_id), -1)
        displayIndex = next((i for i, v in enumerate(user_ids) if v[1] == user_id), -1)

        if (idIndex != -1):
            if user_display == None:
                current_display = input(f"Enter Display Name for Id {user_ids[idIndex][0]}: ")
                user_ids[idIndex][1] = current_display
            else:
                user_ids[idIndex][1] = user_display
        else:
            if user_id == None:
                current_id = input(f"Enter Spotify User Id for Display Name {user_ids[displayIndex][0]}: ")
                user_ids[displayIndex][0] = current_id
            else:
                user_ids[displayIndex][0] = user_id
    
    file = open("id.dat.csv", "w")

    for tup in user_ids:
        file.write(f"{tup[0]},{tup[1]}")

    file.close()

# Using PLaylists

def load_playlists():
    os.makedirs("Folders", exist_ok=True)

    playlists = []
    try:
        with open("playlist.dat.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            for row in reader:
                playlists.append((row[0], row[1]))

    except FileNotFoundError:
        print("No Playlist File found, creating file")
        
        open("playlist.dat.csv", "x").close()

    return playlists

def list_playlists(playlists = None):
    if playlists is None:
        playlists = load_playlists()

    for count, playlist in enumerate(playlists, start=1):
        print(f'{count}) {playlist[0]}')

def playlist_loop():
    playlists = load_playlists();
    sync_options = r"^(" + "|".join(str(i) for i in range(1, len(playlists) + 1)) + r")$";

    list_playlists(playlists)

    options = [("[N] New (Synced)", 'N'), ("[O] New (One Time)", 'O')]

    if len(playlists) == 0:
        print("You have no playlists currently available to sync")
    else:
        options = [("[Number] Sync", sync_options)] + options

    print()

    option = get_checked_input(options)

    match option:
        case _ if re.fullmatch(sync_options, option):
            return (playlists[int(option) - 1][1], 0)
        case "N":
            playlist = input("Playlist link> ")
            return (playlist, 1)
        case "O":
            playlist = input("Playlist link> ")
            return (playlist, 2)
        case "B":
            return ("", -1)
        case _:
            raise ValueError("Incorrect Option WTH")
        
# Using Downloads

def download_remtemp(link, code):
    match code:
        case 0:
            os.system(f'python -m spotdl sync "{get_sync_file(link)}"')
        case 1:
            os.system(f'python -m spotdl sync {link} --save-file "{get_sync_file(link)}"')
        case 2:
            os.system(f'python -m spotdl download {link}')

def download(link, code):
    dir = ""
    if getattr(sys, "frozen", False):
        dir = os.path.dirname(sys.executable)
    else:
        dir = os.getcwd()

    dir += "\\Folders"

    dir += "\\biitcrush\\"

    if code == 0:
        cmd = f'python -m spotdl sync "{get_sync_file(link)}"'
    elif code == 1:
        cmd = f'python -m spotdl sync {link} --save-file "{get_sync_file(link)}"'
    elif code == 2:
        cmd = f'python -m spotdl download {link}'
    else:
        raise ValueError("Invalid code")

    print(dir)

    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")  # live output

    process.wait()


def get_sync_file(link):
    sync_file = link.removeprefix("https://open.spotify.com/").split("?")[0].replace("/", "_") + ".dat.spotdl"
    return sync_file

def move_folder():
    return
    


# Using Interactions

def get_checked_input(options):
    options += [("[B] Back", 'B'), ("[E] Exit", 'E')]

    for option in options:
        print(option[0])

    while True:
        temp_option = input("> ").upper()

        if re.fullmatch("E", temp_option):
            sys.exit(0)

        elif any(re.fullmatch(reg[1], temp_option) for reg in options):
            return temp_option

# MAIN LOOP

def init():
    os.makedirs("Folders", exist_ok=True)
    open("playlist.dat.csv", "a").close()
    open("id.dat.csv", "a").close()

    # PyInstaller bundles files in a temp folder when --onefile is used
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()

    ffmpeg_path = os.path.join(base_path, "ffmpeg", "ffmpeg.exe")
    ffprobe_path = os.path.join(base_path, "ffmpeg", "ffprobe.exe")

    os.environ["SPOTDL_FFMPEG_PATH"] = ffmpeg_path
    os.environ["SPOTDL_FFPROBE_PATH"] = ffprobe_path  # sometimes needed

def main():
    init()

    (playlist, code) = playlist_loop()
    download(playlist, code)

    sys.exit(0)

main()


