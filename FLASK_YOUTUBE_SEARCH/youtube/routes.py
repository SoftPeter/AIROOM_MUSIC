import requests
import os

from flask import Blueprint, render_template, current_app, request, redirect, Flask
from flask_mail import Mail, Message

main = Blueprint('main', __name__)

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'goodzlmn55@gmail.com',
    MAIL_PASSWORD = 'Dudqls7410!')
mail = Mail(app)

@main.route('/', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@main.route('/Hiphop', methods=['GET', 'POST'])
def Hiphop():
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    list_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    videos = []
    #PLyOJ5ZNIl-zBK15LfQpxIeN5czgYpvf8L
    list_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        #'playlistId': request.form.get('query'),
        'playlistId': 'PLBzLqlSrZeIKlY4pgX4ttFAOKpzpV9fis',
        'part': 'snippet',
        'fields': 'items',
        'maxResults': 9
    }
    r = requests.get(list_url, params=list_params)

    results = r.json()['items']

    list_ids = []
    for result in results:
        list_ids.append(result['snippet']['resourceId']['videoId'])

    video_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        'id': ','.join(list_ids),
        'part': 'snippet, contentDetails',
        'maxResults': 9
    }
    r = requests.get(video_url, params=video_params)

    results = r.json()['items']
    for result in results:

        video_data = {
            'id': result['id'],
            'url': f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail': result['snippet']['thumbnails']['high']['url'],
            'title': result['snippet']['title'],
        }
        videos.append(video_data)
    videos.reverse()
    return render_template('index.html', videos=videos)

@main.route('/Piano', methods=['GET', 'POST'])
def Piano():
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    list_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    videos = []

    list_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        #원하는 재생목록ID
        'playlistId': 'PLBzLqlSrZeIIOiFXpuYGMBWZXApL8qODS',
        'part': 'snippet',
        'fields': 'items',
        'maxResults': 9
    }
    r = requests.get(list_url, params=list_params)

    results = r.json()['items']

    list_ids = []
    for result in results:
        list_ids.append(result['snippet']['resourceId']['videoId'])

    video_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        'id': ','.join(list_ids),
        'part': 'snippet, contentDetails',
        'maxResults': 9
    }
    r = requests.get(video_url, params=video_params)

    results = r.json()['items']
    for result in results:

        video_data = {
            'id': result['id'],
            'url': f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail': result['snippet']['thumbnails']['high']['url'],
            'title': result['snippet']['title'],
        }
        videos.append(video_data)
    videos.reverse()
    return render_template('index2.html', videos=videos)

@main.route('/Rock', methods=['GET', 'POST'])
def Rock():
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    list_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    videos = []

    list_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        #원하는 재생목록ID
        'playlistId': 'PLBzLqlSrZeIJOVcuQLnwFsp7-1iqtvfRa',
        'part': 'snippet',
        'fields': 'items',
        'maxResults': 9
    }
    r = requests.get(list_url, params=list_params)

    results = r.json()['items']

    list_ids = []
    for result in results:
        list_ids.append(result['snippet']['resourceId']['videoId'])

    video_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        'id': ','.join(list_ids),
        'part': 'snippet, contentDetails',
        'maxResults': 9
    }
    r = requests.get(video_url, params=video_params)

    results = r.json()['items']
    for result in results:

        video_data = {
            'id': result['id'],
            'url': f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail': result['snippet']['thumbnails']['high']['url'],
            'title': result['snippet']['title'],
        }
        videos.append(video_data)
    videos.reverse()
    return render_template('index.html', videos=videos)

@main.route('/Etc', methods=['GET', 'POST'])
def Etc():
    video_url = 'https://www.googleapis.com/youtube/v3/videos'
    list_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    videos = []

    list_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        #원하는 재생목록ID
        'playlistId': 'PLBzLqlSrZeIJlhu0YzuICsj4wFNa8IeD4',
        'part': 'snippet',
        'fields': 'items',
        'maxResults': 9
    }
    r = requests.get(list_url, params=list_params)

    results = r.json()['items']

    list_ids = []
    for result in results:
        list_ids.append(result['snippet']['resourceId']['videoId'])

    video_params = {
        'key': current_app.config['YOUTUBE_API_KEY'],
        'id': ','.join(list_ids),
        'part': 'snippet, contentDetails',
        'maxResults': 9
    }
    r = requests.get(video_url, params=video_params)

    results = r.json()['items']
    for result in results:

        video_data = {
            'id': result['id'],
            'url': f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail': result['snippet']['thumbnails']['high']['url'],
            'title': result['snippet']['title'],
        }
        videos.append(video_data)
    videos.reverse()
    return render_template('index.html', videos=videos)

@main.route("/email", methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        try:
            #Send email
            title = request.form['email_title']
            content = request.form['email_content']
            msg = Message(title, sender='goodzlmn55@gmail.com', recipients=['goodzlmn55@gmail.com'])
            msg.body = content
            mail.send(msg)

            #file upload
            """
            f = request.files['file']
            os.makedirs(os.path.join("./Customer", title), exist_ok=True)
            f.save(os.path.join("./Customer", title, secure_filename(f.filename)))
            """
            return render_template('success.html')
        except BaseException:
            return render_template('error.html')
    else:
        return render_template('form.html')
