import sys
import csv
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
TOKEN_ENDPOINT = "https://scarrletrain.netlify.app/.netlify/functions/spotifyToken"

def transfer(data):
    with open('.tempdat', 'w') as f:
        f.write(data)

def is_valid_user(user_id, sp):
    try:
        return bool(sp.user(user_id)['display_name'])
    except spotipy.exceptions.SpotifyException:
        return False

def load_user_ids():
    user_ids = []
    try:
        with open("user_ids.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            for count, row in enumerate(reader, start=1):
                if len(row) >= 2:
                    print(f"{count}) {row[1]}")
                    user_ids.append(row[0])
    except FileNotFoundError:
        print("No user_ids.csv file found.")
        sys.exit(1)
    return user_ids

def save_new_user(user_id):
    display_name = input("Enter display name **You cannot change this**: ").strip()
    with open("user_ids.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([user_id, display_name])

def main():
    def get_access_token():
        r = requests.get(TOKEN_ENDPOINT)
        r.raise_for_status()
        return r.json()["access_token"]

    sp = spotipy.Spotify(auth=get_access_token())

    get_links = input("Would you like to search for folders (Y/N): ").strip().upper()
    
    if get_links == "Y":
        user_ids = load_user_ids()
        user_choice = input("Select user ID from list or input new one: ").strip()

        if user_choice.isdigit() and 1 <= int(user_choice) <= len(user_ids):
            user_id = user_ids[int(user_choice) - 1]
            transfer(user_id)

        elif is_valid_user(user_choice, sp):
            user_id = user_choice
            print("User: " + sp.user(user_id)['display_name'])
            if input("Would you like to save this user ID? (Y/N): ").strip().upper() == "Y":
                save_new_user(user_id)
            else:
                print("User ID not saved.")
            transfer(user_id)

        else:
            print("Invalid option. Exiting.")
            sys.exit(1)

    elif get_links == "N":
        print("Skipping folder search.")
        sys.exit(2)
    else:
        print("Invalid option. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
