# -*- coding: utf-8 -*-

import config

import os
import sys
import requests

import time
import json
import datetime

from user import User
from exporter import Exporter
from pagination import Pagination

from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for

app = Flask(__name__)

@app.route("/", defaults={'page': 1})
@app.route("/page/<int:page>")
def index(page):
    e = Exporter()
    u = User()

    # gets
    count = e.get_feed_count()

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = e.get_feed(page)

    # sets
    posts = []

    for media in feed:

        # gets
        owner_profile = e.get_user_profile(media[1])
        saved_status = u.get_saved_status(media[0], 0)

        # sets
        likes = json.loads(media[10])['count']
        comments = json.loads(media[11])['count']

        post = {}

        post['is_saved'] = saved_status

        post['media_id'] = media[0]
        post['owner'] = media[1]
        post['media_type'] = media[2]
        # post['is_video'] = bool(media[3])
        post['display_url'] = media[4]
        # post['display_resources'] = media[5]
        post['caption'] = media[6]
        post['tagged_users'] = media[7]
        post['shortcode'] = media[8]
        post['timestamp'] = datetime.datetime.fromtimestamp(media[9])
        post['likes'] = likes
        post['comments'] = comments
        #post['thumbnails'] = json.loads(media[12])
        
        if post['media_type'] == 'GraphSidecar':
            post['sidecar'] = json.loads(media[13])
        else:
            post['sidecar'] = []


        post['owner_id'] = owner_profile[0]
        post['owner_username'] = owner_profile[1]
        post['owner_full_name'] = owner_profile[2]
        # post['owner_biography'] = owner_profile[3]
        post['owner_profile_pic_url'] = owner_profile[4]
        # post['owner_profile_pic_url_hd'] = owner_profile[5]
        # post['owner_external_url'] = owner_profile[6]
        # post['owner_external_url_linkshimmed'] = owner_profile[7]
        # post['owner_followed_by'] = owner_profile[8]
        # post['owner_follow'] = owner_profile[9]
        # post['owner_last_updated'] = time.gmtime(owner_profile[10])
        # post['owner_is_private'] = bool(owner_profile[11])
        # post['owner_is_deleted'] = bool(owner_profile[12])

        post['origin'] = 'feed:' + str(page)

        posts.append(post)

    u.close()
    e.close()
    return render_template('feed/index.html', posts=posts, pagination=pagination)

@app.route("/memory/", defaults={'page': 1})
@app.route("/memory/page/<int:page>")
def memory(page):
    e = Exporter()
    u = User()

    # Main user is 0
    user_id = 0

    # gets
    user_memory_raw = tuple(u.remember(user_id))

    user_memory = ()

    for x in user_memory_raw:
      user_memory += x

    # return(str(user_memory))
    count = len(user_memory)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = e.get_memory_feed(user_memory, page)

    # sets
    posts = []

    for media in feed:

        # gets
        owner_profile = e.get_user_profile(media[1])
        saved_status = u.get_saved_status(media[0], 0)

        # sets
        likes = json.loads(media[10])['count']
        comments = json.loads(media[11])['count']

        post = {}

        owner_username = e.get_username_from_user_id(media[1])
        date = datetime.datetime.fromtimestamp(media[9]).strftime('%Y-%m-%d_%H-%M')
        post['filename'] = 'images/' + str(user_id) + '/' + date + '_' + media[8] + '_by-' + owner_username + '.jpg'
        post['is_saved'] = saved_status

        post['media_id'] = media[0]
        post['owner'] = media[1]
        post['media_type'] = media[2]
        # post['is_video'] = bool(media[3])
        post['display_url'] = media[4]
        # post['display_resources'] = media[5]
        post['caption'] = media[6]
        post['tagged_users'] = media[7]
        post['shortcode'] = media[8]
        post['timestamp'] = datetime.datetime.fromtimestamp(media[9])
        post['likes'] = likes
        post['comments'] = comments
        #post['thumbnails'] = json.loads(media[12])
        
        if post['media_type'] == 'GraphSidecar':
            post['sidecar'] = json.loads(media[13])
        else:
            post['sidecar'] = []


        post['owner_id'] = owner_profile[0]
        post['owner_username'] = owner_profile[1]
        post['owner_full_name'] = owner_profile[2]
        # post['owner_biography'] = owner_profile[3]
        post['owner_profile_pic_url'] = owner_profile[4]
        # post['owner_profile_pic_url_hd'] = owner_profile[5]
        # post['owner_external_url'] = owner_profile[6]
        # post['owner_external_url_linkshimmed'] = owner_profile[7]
        # post['owner_followed_by'] = owner_profile[8]
        # post['owner_follow'] = owner_profile[9]
        # post['owner_last_updated'] = time.gmtime(owner_profile[10])
        # post['owner_is_private'] = bool(owner_profile[11])
        # post['owner_is_deleted'] = bool(owner_profile[12])
        
        post['origin'] = 'memory:' + str(page)

        posts.append(post)

    u.close()
    e.close()
    return render_template('feed/memory.html', posts=posts, pagination=pagination)

@app.route("/p/<media_shortcode>")
def media(media_shortcode):
    e = Exporter()
    u = User()
    
    # gets
    media = e.get_media_from_shortcode(media_shortcode)
    owner_profile = e.get_user_profile(media[1])

    saved_status = u.get_saved_status(media[0], 0)

    u.close()


    # sets
    media_likes = json.loads(media[10])['count']
    media_comments = json.loads(media[11])['count']

    media_export = {}

    media_export['is_saved'] = saved_status

    media_export['media_id'] = media[0]
    # media_export['owner'] = media[1]
    media_export['media_type'] = media[2]
    # media_export['is_video'] = bool(media[3])
    media_export['display_url'] = media[4]
    # media_export['display_resources'] = media[5]
    media_export['caption'] = media[6]
    media_export['tagged_users'] = media[7]
    media_export['shortcode'] = media[8]
    media_export['timestamp'] = datetime.datetime.fromtimestamp(media[9])
    media_export['likes'] = media_likes
    media_export['comments'] = media_comments

    if media_export['media_type'] == 'GraphSidecar':
        media_export['sidecar'] = json.loads(media[13])
    else:
        media_export['sidecar'] = []


    media_export['owner_id'] = owner_profile[0]
    media_export['owner_username'] = owner_profile[1]
    media_export['owner_full_name'] = owner_profile[2]
    # media_export['owner_biography'] = owner_profile[3]
    media_export['owner_profile_pic_url'] = owner_profile[4]
    # media_export['owner_profile_pic_url_hd'] = owner_profile[5]
    # media_export['owner_external_url'] = owner_profile[6]
    # media_export['owner_external_url_linkshimmed'] = owner_profile[7]
    # media_export['owner_followed_by'] = owner_profile[8]
    # media_export['owner_follow'] = owner_profile[9]
    # media_export['owner_last_updated'] = time.gmtime(owner_profile[10])
    # media_export['owner_is_private'] = bool(owner_profile[11])
    # media_export['owner_is_deleted'] = bool(owner_profile[12]

    media_export['origin'] = media[8]

    e.close()
    return render_template('media/index.html', post=media_export)

@app.route("/save/<media_shortcode>")
def save(media_shortcode):
    origin = request.args.get('origin', default='')
    e = Exporter()

    # Main user is 0
    user_id = 0

    # gets
    media = e.get_media_from_shortcode(media_shortcode)

    # Create the filename and download the image
    owner_username = e.get_username_from_user_id(media[1])
    date = datetime.datetime.fromtimestamp(media[9]).strftime('%Y-%m-%d_%H-%M')
    filename = date + '_' + media_shortcode + '_by-' + owner_username + '.jpg'
    fileaddr = './static/images/' + str(user_id) + '/'

    media_url = media[4]

    if not os.path.exists(fileaddr):
      os.makedirs(fileaddr)

    destination = fileaddr + filename

    with open(destination, 'wb') as handle:
        response = requests.get(media_url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)


    u = User()
    if u.get_saved_status(media[0], user_id) is False:
      u.save_media(media[0], user_id, filename, int(time.time()))
    
    e.close()
    u.close()

    redirection = get_redirection(origin, media_shortcode)

    return redirect(redirection)

@app.route("/forget/<media_shortcode>")
def forget(media_shortcode):
    origin = request.args.get('origin', default='')
    e = Exporter()
    # gets
    media_id = e.get_media_id_from_shortcode(media_shortcode)
    e.close()

    # Main user is 0
    user_id = 0

    
    u = User()
    if u.get_saved_status(media_id, user_id) is True:
      fileaddr = './static/images/' + str(user_id) + '/'
      filename = u.get_saved_filename(media_id, user_id)
      target = fileaddr + filename
      print(target, file=sys.stderr)

      u.forget_media(media_id, user_id)
      if os.path.isfile(target):
        os.remove(target)
    u.close()


    redirection = get_redirection(origin, media_shortcode)

    return redirect(redirection)



@app.route("/@<username>", defaults={'page': 1})
@app.route("/@<username>/page/<int:page>")
def profile(username, page):
    e = Exporter()
    u = User()


    display_as_feed = False
    if request.args.get('display') == 'feed':
        display_as_feed = True


    # gets
    user_id = e.get_user_id_from_username(username)

    profile = e.get_user_profile(user_id)
    count = e.get_user_feed_count(user_id)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = e.get_user_feed(user_id, page)

    #sets
    author = {}

    author['id'] = user_id
    author['username'] = username
    author['full_name'] = profile[2]
    author['biography'] = profile[3]
    author['profile_pic_url'] = profile[4]
    author['profile_pic_url_hd'] = profile[5]
    author['external_url'] = profile[6]
    author['external_url_linkshimmed'] = profile[7]
    author['followed_by'] = profile[8]
    author['follow'] = profile[9]
    author['last_updated'] = datetime.datetime.fromtimestamp(profile[10])
    author['is_private'] = bool(profile[11])
    # author['is_deleted'] = bool(profile[12])

    posts = []
    for media in feed:
        saved_status = u.get_saved_status(media[0], 0)

        #sets
        media_likes = json.loads(media[10])['count']
        media_comments = json.loads(media[11])['count']
        media_thumbnail_320 = json.loads(media[12])[3]['src']

        post = {}

        post['owner_username'] = author['username']
        post['owner_profile_pic_url'] = author['profile_pic_url']
        post['owner_full_name'] = author['full_name']

        post['is_saved'] = saved_status

        post['media_id'] = media[0]
        post['owner'] = media[1]
        post['media_type'] = media[2]
        # post['is_video'] = bool(media[3])
        post['display_url'] = media[4]
        # post['display_resources'] = media[5]
        post['caption'] = media[6]
        post['tagged_users'] = media[7]
        post['shortcode'] = media[8]
        post['timestamp'] = datetime.datetime.fromtimestamp(media[9])
        post['likes'] = media_likes
        post['comments'] = media_comments
        post['thumbnail_320'] = media_thumbnail_320
        
        if post['media_type'] == 'GraphSidecar':
            post['sidecar'] = json.loads(media[13])
        else:
            post['sidecar'] = []

        post['origin'] = '@' + username + ':' + str(page)

        posts.append(post)

    u.close()
    e.close()
    return render_template('profile/index.html',
                            author=author,
                            posts=posts,
                            pagination=pagination,
                            display_as_feed=display_as_feed)

def get_redirection(origin, media_shortcode):
    if origin[0] == '@':
      colonindex = origin.find(':')
      username = origin[1:colonindex]
      page = origin[colonindex+1:]
      return url_for('profile', page = page, username = username)
    elif origin[0:4] == 'feed':
      colonindex = origin.find(':')
      page = origin[colonindex+1:]
      return url_for('index', page = page)
    elif origin[0:6] == 'memory':
      colonindex = origin.find(':')
      page = origin[colonindex+1:]
      return url_for('memory', page = page)
    elif origin == 'media' or origin is '':
      return url_for('media', media_shortcode = media_shortcode)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page



if __name__ == '__main__':
    app.run(debug=True)