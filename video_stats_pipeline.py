import requests
import json
import os
from dotenv import load_dotenv
from datetime import date

#Use pip install python-dotenv to install the dotenv package

load_dotenv(dotenv_path="./.env")
channel_handle = 'MrBeast'
API_KEY = os.getenv("API_KEY")
key_url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={API_KEY}"


#Json dump is used to convert the data into a json format
#response = requests.get(url)
#data = response.json()
#data_content = json.dumps(data , indent = 1)

def get_playlist_id(url):
    """
    This function is used to get the playlist id of a channel
    """
    try:
        response = requests.get(url)
        data = response.json()
        channel_items = data['items'][0]
        playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return playlist_id
    except requests.exceptions.RequestException as e:
        print(e)

def get_playlist_items(playlist_id , max_results , API_KEY):
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}"
    video_ids = []
    page_token = None
    try:
        while True:
            if page_token:
                url = base_url + f'&pageToken={page_token}'
            else:
                url = base_url
                
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            play_list_items = data.get('items', [])
            for item in play_list_items:
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)
            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return video_ids
    except requests.exceptions.RequestException as e:
        print(e)

def create_batches(video_list , batch_size):
    for batch_start_index in range(0 , len(video_list) ,batch_size):
        batch_end_index = batch_start_index+batch_size
        video_batch = video_list[batch_start_index:batch_end_index]
        yield video_batch

def get_video_info(video_list , API_KEY , size):
    batch_size = size
    extracted_data = []
    try:
        for video_batch in create_batches(video_list , batch_size):
            video_ids_str = ",".join(video_batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None), #Note the method here , you can give thw default value as None or []
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                }

                extracted_data.append(video_data)
        return extracted_data
    except requests.exceptions.RequestException as e:
        print(e)

def save_to_json(extracted_data , indent):
    os.makedirs('./data', exist_ok=True)
    path = f"./data/youtube_video_data_{date.today()}.json"

    with open(path , "w" , encoding='utf-8') as file:
        json.dump(extracted_data , file, indent = indent , ensure_ascii = False)


if __name__ == "__main__":
    playlist_id = get_playlist_id(key_url)
    print('playlist_id: ', playlist_id)
    playlist_items = get_playlist_items(playlist_id , 2 , API_KEY)
    print('End of retrieving playlist items')
    print('Getting video info')
    video_data = get_video_info(playlist_items , API_KEY , 50)
    print(video_data)
    save_to_json(video_data , 4)
    print('End of execution')