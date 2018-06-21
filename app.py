# -*- coding: utf-8 -*-

import config

import os
import sys
import requests

import time
import json
import datetime

from user import User
from lists import Lists
from importer import Importer
from exporter import Exporter
from pagination import Pagination
import forms

from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import abort
from flask import flash

from werkzeug.utils import secure_filename
UPLOAD_FOLDER = './temp/'
ALLOWED_EXTENSIONS = set(['txt', 'json'])


DEFAULT_USER_ID = 0
DEFAULT_LIST_INFO = {'shortname': '_feed',
                     'longname': 'Feed',
                     'description': 'Default Feed List'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'THIS_SHOULD_BE_CHANGED'

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route("/", defaults={'page': 1})
@app.route("/page/<int:page>")
def index(page):
    e = Exporter()
    l = Lists()
    u = User()

    shortname = DEFAULT_LIST_INFO['shortname']
    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    # gets
    count = l.get_list_feed_count(list_id = list_id)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = l.get_list_feed(list_id = list_id, page = page)

    # sets
    posts = []

    for media in feed:

        # gets
        owner_profile = e.get_account_profile(media[1])
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
        post['owner_account_name'] = owner_profile[1]
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
    user_id = DEFAULT_USER_ID

    # gets
    count = u.remember_count(user_id)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = u.remember_feed(user_id, page)

    # sets
    posts = []

    for media in feed:

        # gets
        owner_profile = e.get_account_profile(media[1])
        saved_status = u.get_saved_status(media[0], 0)

        # sets
        likes = json.loads(media[10])['count']
        comments = json.loads(media[11])['count']

        post = {}

        owner_account_name = e.get_account_name_from_account_id(media[1])
        date = datetime.datetime.fromtimestamp(media[9]).strftime('%Y-%m-%d_%H-%M')
        post['filename'] = 'images/' + str(user_id) + '/' + date + '_' + media[8] + '_by-' + owner_account_name + '.jpg'
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
        post['owner_account_name'] = owner_profile[1]
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

    if not media:
        abort(404)

    owner_profile = e.get_account_profile(media[1])

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
    media_export['owner_account_name'] = owner_profile[1]
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

    display_as_feed = False
    if request.args.get('display') == 'feed':
        display_as_feed = True

    # Main user is 0
    user_id = DEFAULT_USER_ID

    # gets
    media = e.get_media_from_shortcode(media_shortcode)

    if not media:
        abort(404)

    # Create the filename and download the image
    owner_account_name = e.get_account_name_from_account_id(media[1])
    date = datetime.datetime.fromtimestamp(media[9]).strftime('%Y-%m-%d_%H-%M')
    filename = date + '_' + media_shortcode + '_by-' + owner_account_name + '.jpg'
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

    redirection = get_redirection(origin, media_shortcode, display_as_feed)

    return redirect(redirection)

@app.route("/forget/<media_shortcode>")
def forget(media_shortcode):
    origin = request.args.get('origin', default='')
    e = Exporter()

    display_as_feed = False
    if request.args.get('display') == 'feed':
        display_as_feed = True

    # gets
    media_id = e.get_media_id_from_shortcode(media_shortcode)
    e.close()

    if not media_id:
        abort(404)

    # Main user is 0
    user_id = DEFAULT_USER_ID

    u = User()
    if u.get_saved_status(media_id, user_id) is True:
      fileaddr = './static/images/' + str(user_id) + '/'
      filename = u.get_saved_filename(media_id, user_id)
      target = fileaddr + filename
      #print(target, file=sys.stderr)

      u.forget_media(media_id, user_id)
      if os.path.isfile(target):
        os.remove(target)
    u.close()

    redirection = get_redirection(origin, media_shortcode, display_as_feed)

    return redirect(redirection)



@app.route("/@<account_name>", defaults={'page': 1})
@app.route("/@<account_name>/page/<int:page>")
def profile(account_name, page):
    e = Exporter()
    u = User()

    display_as_feed = False
    if request.args.get('display') == 'feed':
        display_as_feed = True

    # gets
    account_id = e.get_account_id_from_account_name(account_name)
    
    if not account_id:
        abort(404)

    profile = e.get_account_profile(account_id)
    count = e.get_account_feed_count(account_id)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = e.get_account_feed(account_id, page)

    #sets
    author = {}

    author['id'] = account_id
    author['account_name'] = account_name
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

        post['owner_account_name'] = author['account_name']
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

        post['origin'] = '@' + account_name + ':' + str(page)

        posts.append(post)

    u.close()
    e.close()
    return render_template('profile/index.html',
                            author=author,
                            posts=posts,
                            pagination=pagination,
                            display_as_feed=display_as_feed)

@app.route("/@<account_name>/lists")
def profile_lists(account_name):
    e = Exporter()
    l = Lists()

    #gets
    account_id = e.get_account_id_from_account_name(account_name)

    if not account_id:
        abort(404)

    profile = e.get_account_profile(account_id)

    the_lists_tup = l.get_lists_info_for_account(account_id)

    #sets
    author = {}

    author['id'] = account_id
    author['account_name'] = account_name
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

    lists = []
    for single_list in the_lists_tup:
        single_dict = {}
        keys = ('id','shortname','longname','description','last_updated','date_added','count')
        for k, s in zip(keys, single_list):
            single_dict[k] = s
        lists.append(single_dict)

    e.close()
    l.close()

    return render_template('profile/lists.html',
                            author=author,
                            lists=lists)


@app.route("/list/<shortname>", defaults={'page': 1})
@app.route("/list/<shortname>/page/<int:page>")
def list_feed(shortname, page):
    e = Exporter()
    u = User()
    l = Lists()

    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    if not list_id:
        abort(404)

    # gets
    count = l.get_list_feed_count(list_id)

    # instances
    pagination = Pagination(page, config.elements_per_page, count)

    if page > pagination.pages:
      page = pagination.pages

    feed = l.get_list_feed(list_id, page)

    # sets
    posts = []

    for media in feed:

        # gets
        owner_profile = e.get_account_profile(media[1])
        saved_status = u.get_saved_status(media[0], 0)

        # sets
        likes = json.loads(media[10])['count']
        comments = json.loads(media[11])['count']

        post = {}

        post['is_saved'] = saved_status

        post['media_id'] = media[0]
        post['owner'] = media[1]
        post['media_type'] = media[2]
        post['display_url'] = media[4]
        post['caption'] = media[6]
        post['tagged_users'] = media[7]
        post['shortcode'] = media[8]
        post['timestamp'] = datetime.datetime.fromtimestamp(media[9])
        post['likes'] = likes
        post['comments'] = comments
        
        if post['media_type'] == 'GraphSidecar':
            post['sidecar'] = json.loads(media[13])
        else:
            post['sidecar'] = []


        post['owner_id'] = owner_profile[0]
        post['owner_account_name'] = owner_profile[1]
        post['owner_full_name'] = owner_profile[2]
        post['owner_profile_pic_url'] = owner_profile[4]

        post['origin'] = 'feed:' + str(page)

        posts.append(post)

    the_list_tup = l.get_list_info(list_id)
    the_list = {}
    keys = ('id','shortname','longname','description','last_updated','date_added','count')
    for k, s in zip(keys, the_list_tup):
        the_list[k] = s

    #print(str(the_list), file=sys.stderr)

    l.close()
    u.close()
    e.close()
    return render_template('lists/feed.html',
                                the_list = the_list,
                                posts=posts,
                                pagination=pagination)


@app.route("/list/create", methods=['POST', 'GET'])
def list_create():
    if request.method == 'POST':

        new_list, errors = forms.check_list_form(request_form = request.form)

        if errors != {}:
            for error in errors.values():
                flash(str(error))
            return render_template('lists/create.html', errors = errors)

        #return str(new_list)

        l = Lists()

        user_id = DEFAULT_USER_ID
        l.create_new_list(new_list, user_id)

        l.close()

        return redirect(url_for('list_accounts', shortname = new_list['shortname']))

    else:
        return render_template('lists/create.html')


@app.route("/list/<shortname>/edit", methods=['POST', 'GET'])
def list_edit(shortname):
    l = Lists()

    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    if not list_id:
        abort(404)

    if request.method == 'POST':
        returned_list, errors = forms.check_list_form(request_form = request.form)

        if errors != {}:
            for error in errors.values():
                flash(str(error))
            return render_template('lists/edit.html', errors = errors)

        l = Lists()

        l.modify_list(list_id, returned_list) 

        l.close()

        return redirect(url_for('list_accounts', shortname = returned_list['shortname']))

    else:

        the_list_tup = l.get_list_info(list_id)
        the_list = {}
        keys = ('id','shortname','longname','description','last_updated','date_added','count')
        for k, s in zip(keys, the_list_tup):
            the_list[k] = s

        return render_template('lists/edit.html', list = the_list)



@app.route("/list/<shortname>/accounts")
def list_accounts(shortname):
    l = Lists()

    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    if not list_id:
        abort(404)

    the_accounts_tup = l.get_list_accounts_info(list_id)

    the_accounts = []
    for account in the_accounts_tup:
        single_dict = {}
        keys = ('id',
                'account_name',
                'full_name',
                'biography',
                'profile_pic_url',
                'profile_pic_url_hd',
                'external_url',
                'external_url_linkshimmed',
                'followed_by',
                'follow',
                'last_updated',
                'is_private',
                'is_deleted')
        for k, a in zip(keys, account):
            single_dict[k] = a
        the_accounts.append(single_dict)

    the_list_tup = l.get_list_info(list_id)
    the_list = {}
    keys = ('id','shortname','longname','description','last_updated','date_added','count')
    for k, t in zip(keys, the_list_tup):
        the_list[k] = t

#print(str(the_list), file=sys.stderr)

    l.close()
    return render_template('lists/accounts.html',
                                the_list = the_list,
                                accounts = the_accounts)


@app.route("/list/<shortname>/add")
def list_add(shortname):
    e = Exporter()
    l = Lists()

    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    # if not list_id:
    #     abort(404)
    #     
    #     


    # Get the accounts for that user
    the_accounts_tup = e.get_all_accounts_info(user_id)


    # Set Accounts list
    the_accounts = []
    for account in the_accounts_tup:
        single_dict = {}
        keys = ('id',
                'account_name',
                'full_name',
                'biography',
                'profile_pic_url',
                'profile_pic_url_hd',
                'external_url',
                'external_url_linkshimmed',
                'followed_by',
                'follow',
                'last_updated',
                'is_private')
        for k, a in zip(keys, account):
            single_dict[k] = a

        single_dict['is_in_list'] = l.check_if_account_in_list(list_id = list_id, account_id = single_dict['id'])
        the_accounts.append(single_dict)


    # Get List Info
    the_list_tup = l.get_list_info(list_id)
    the_list = {}
    keys = ('id','shortname','longname','description','last_updated','date_added','count')
    for k, t in zip(keys, the_list_tup):
        the_list[k] = t

    # Close the DB
    e.close()
    l.close()

    return render_template('lists/add_users.html',
                                the_list = the_list,
                                accounts = the_accounts)


@app.route("/list/<shortname>/add/<account_name>")
def list_add_user(shortname, account_name):
    e = Exporter()
    l = Lists()

    account_id = e.get_account_id_from_account_name(account_name)
    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    if not account_id:
        abort(404)
    if not list_id:
        abort(404)

    if l.check_if_account_in_list(list_id, account_id) is False:
        l.add_account_to_list(list_id, account_id)

    e.close()
    l.close()

    return redirect(url_for('list_feed', shortname = shortname))

@app.route("/list/add/<account_name>")
def list_choices_for_user(account_name):
    lists = get_lists()

    return render_template('lists/choices.html',
                                lists = lists,
                                account_name = account_name)


@app.route("/list/<shortname>/remove/<account_name>")
def list_remove_user(shortname, account_name):
    e = Exporter()
    l = Lists()

    account_id = e.get_account_id_from_account_name(account_name)
    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(shortname, user_id)

    if not account_id:
        abort(404)
    if not list_id:
        abort(404)

    l.remove_account_from_list(list_id, account_id)

    e.close()
    l.close()

    return redirect(url_for('list_accounts', shortname = shortname))

@app.route("/list/<shortname>/delete", methods = ["GET", "POST"])
def list_delete(shortname):
    if request.method == 'POST':
        if request.form['submit'] == 'submit':
            l = Lists()
            
            user_id = DEFAULT_USER_ID
            list_id = l.get_list_id_from_shortname(shortname, user_id)

            if not list_id:
                abort(404)

            l.delete_list(list_id)
            l.close()

            return redirect(url_for('list_lists'))

    flash('Are you sure you want to delete this list? There is no turning back.')
    return render_template('lists/confirm.html', shortname = shortname)


@app.route("/lists")
def list_lists():
    lists = get_lists()

    return render_template('lists/index.html', lists = lists)




@app.route("/import/json", methods=['POST', 'GET'])
def import_from_json():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            contacts_to_import = []
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
                contacts_to_import = json.loads(f.read().splitlines()[0])

            contacts_to_import = list(contacts_to_import['following'].keys())

            if contacts_to_import == []:
                flash('No contact to import')
                return redirect(request.url)

            i = Importer()

            total = 0
            for contact in contacts_to_import:
                if not i.user_exists(contact):
                    contact_info = i.get_account_data(contact)
                    if i.add_new_user(contact_info):
                        total += 1 

            i.close()

            return redirect(url_for('import_success', import_count = total))

    return render_template('import/json.html')



@app.route("/import/text", methods=['POST', 'GET'])
def import_from_text():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            contacts_to_import = []
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
                contacts_to_import = f.read().splitlines()

            if contacts_to_import == []:
                flash('No contact to import')
                return redirect(request.url)

            i = Importer()

            total = 0
            for contact in contacts_to_import:
                contact_info = i.get_account_data(contact)
                if not i.user_exists(contact):
                    if i.add_new_user(contact_info):
                        total += 1

            i.close()

            return redirect(url_for('import_success', import_count = total))

    return render_template('import/text.html')



@app.route("/import", methods=['POST', 'GET'])
def import_from_form():

    if request.method == 'POST':

        if request.form['contacts'] == '':
            flash('Please fill in the text area before clicking the button.')
            return render_template('import/form.html', errors = 'The text area should not be empty.')

        contacts_to_import = request.form['contacts'].splitlines()

        i = Importer()

        total = 0
        for contact in contacts_to_import:
            contact_info = i.get_account_data(contact)
            if not i.user_exists(contact):
                if i.add_new_user(contact_info):
                    total += 1

        i.close()

        return redirect(url_for('import_success', import_count = total))
    else:
        return render_template('import/form.html')

@app.route("/import/success")
def import_success():
    import_count = request.args['import_count']

    return render_template('import/success.html', import_count = import_count)



@app.route("/feed/hidden-accounts")
def list_hidden_accounts():
#TODO
    u = User()

    list_shortname = DEFAULT_LIST_INFO['shortname']

    # Get the accounts
    the_accounts_tup = u.get_hidden_account_list(list_shortname = list_shortname, user_id = DEFAULT_USER_ID)

    # Set Accounts list
    the_accounts = []
    for account in the_accounts_tup:
        single_dict = {}
        keys = ('id',
                'account_name',
                'full_name',
                'biography',
                'profile_pic_url',
                'profile_pic_url_hd',
                'external_url',
                'external_url_linkshimmed',
                'followed_by',
                'follow',
                'last_updated',
                'is_private',
                'is_deleted')
        for k, a in zip(keys, account):
            single_dict[k] = a

        the_accounts.append(single_dict)

    u.close()


    return render_template('feed/hidden.html', accounts = the_accounts)


@app.route("/feed/hide/<account_name>")
def hide_account(account_name):
    e = Exporter()
    l = Lists()
    
    list_id = l.get_list_id_from_shortname(shortname = DEFAULT_LIST_INFO['shortname'], user_id = DEFAULT_USER_ID)
    account_id = e.get_account_id_from_account_name(account_name)

    if not account_id:
        abort(404)

    l.remove_account_from_list(list_id = list_id, account_id = account_id)
    #u.hide_account_from_feed(user_id = DEFAULT_USER_ID, account_id = account_id)


    l.close()
    e.close()

    destination = request.args['from']

    if(destination == 'profile'):
        return redirect(url_for('profile', account_name = account_name).replace('%40', '@'))
    if(destination == 'profile_feed'):
        return redirect(url_for('profile', account_name = account_name, display = 'feed').replace('%40', '@'))
    if(destination == 'profile_lists'):
        return redirect(url_for('profile_lists', account_name = account_name).replace('%40', '@'))

    return redirect(url_for('index'))


@app.route("/feed/unhide/<account_name>")
def show_account(account_name):
    e = Exporter()
    l = Lists()
    
    list_id = l.get_list_id_from_shortname(shortname = DEFAULT_LIST_INFO['shortname'], user_id = DEFAULT_USER_ID)
    account_id = e.get_account_id_from_account_name(account_name)

    if not account_id:
        abort(404)

    l.add_account_to_list(list_id = list_id, account_id = account_id)
    #u.show_account_on_feed(user_id = DEFAULT_USER_ID, account_id = account_id)

    l.close()
    e.close()

    destination = request.args['from']

    if(destination == 'profile'):
        return redirect(url_for('profile', account_name = account_name).replace('%40', '@'))
    if(destination == 'profile_feed'):
        return redirect(url_for('profile', account_name = account_name, display = 'feed')).replace('%40', '@')
    if(destination == 'profile_lists'):
        return redirect(url_for('profile_lists', account_name = account_name).replace('%40', '@'))

    return redirect(url_for('list_hidden_accounts'))








# FUNCTIONS

def get_lists():
    l = Lists()

    user_id = DEFAULT_USER_ID
    all_lists = l.get_all_lists_info(user_id)

    lists = []
    for single_list in all_lists:
        single_dict = {}
        keys = ('id','shortname','longname','description','last_updated','date_added','user_id','count')
        for k, s in zip(keys, single_list):
            single_dict[k] = s
        lists.append(single_dict)

    l.close()

    return lists
app.jinja_env.globals['get_lists'] = get_lists


def check_if_account_in_list(list_shortname, account_name):
    l = Lists()
    e = Exporter()

    user_id = DEFAULT_USER_ID
    list_id = l.get_list_id_from_shortname(list_shortname, user_id)
    account_id = e.get_account_id_from_account_name(account_name)

    if not account_id:
        abort(404)
    if not account_id:
        abort(404)

    result = l.check_if_account_in_list(list_id, account_id)

    l.close()
    e.close()

    return result
app.jinja_env.globals['account_is_in_list'] = check_if_account_in_list


def check_if_account_is_hidden(account_id):
    u = User()

    result = u.get_hidden_status(list_shortname = DEFAULT_LIST_INFO['shortname'],
                                 user_id = DEFAULT_USER_ID,
                                 account_id = account_id)

    u.close()

    return result
app.jinja_env.globals['account_is_hidden'] = check_if_account_is_hidden


def get_redirection(origin, media_shortcode, display_as_feed = False):
    if origin[0] == '@':
        colonindex = origin.find(':')
        account_name = origin[1:colonindex]
        page = origin[colonindex+1:]
        if display_as_feed == True:
            return url_for('profile', page = page, account_name = account_name, display = 'feed').replace('%40', '@')
        else:
            return url_for('profile', page = page, account_name = account_name).replace('%40', '@')
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)