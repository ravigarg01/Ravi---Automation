import requests

# Replace with your API key and the video ID
API_KEY = "AIzaSyCG0WkUCV096-g6vvViOtwWfMod3N1hO5s"
VIDEO_ID = "KCoGoHIW2f4"

def get_comment_threads():
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": VIDEO_ID,
        "key": API_KEY,
        "maxResults": 100
    }
    response = requests.get(url, params=params)
    return response.json()

def reply_to_comment(parent_comment_id, reply_text):
    url = f"https://www.googleapis.com/youtube/v3/comments"
    params = {
        "part": "snippet",
        "key": API_KEY
    }
    data = {
        "snippet": {
            "parentId": parent_comment_id,
            "textOriginal": reply_text
        }
    }
    response = requests.post(url, params=params, json=data)
    return response.json()

# Get comments and find the one you want to reply to (you might need to filter the comments)
comments = get_comment_threads()

# For demonstration purposes, let's assume the first comment thread is the one you want to reply to
print(comments)
comment_thread = comments["items"][0]
parent_comment_id = comment_thread["snippet"]["topLevelComment"]["id"]

# Your reply text
reply_text = "Thank you for your comment! We appreciate your feedback."

# Post a reply to the comment

