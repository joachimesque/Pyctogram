# -*- coding: utf-8 -*-
import config

from requests import get
from bs4 import BeautifulSoup
import json

from database import Database


class Importer:

    def __init__(self):
        self.db = Database()

    def init_db(self):
        self.db.init_db()

    def close(self):
        self.db.stop_db()

    def get_user_list(self):
        # This function gets the list of accounts to check
        # from database
        # Returns an object with all the accounts

        try:
            self.db.cursor.execute("SELECT username FROM Accounts")
            return(self.db.cursor.fetchall())
        except:
            exit("Error: Getting list of users has failed.")


    def get_user_data(self, user_name):
        # This function gets user data from the username
        # Returns : User data, if username exists
        #           None, if not


        url = 'https://instagram.com/%s' % user_name
        try:
            response = get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0'})
        except:
            print("Error: Something happened with the connection")
            self.db.stop_db()
            exit("The DB has been saved")

        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')

        for script in scripts:
            if script.text.startswith('window._sharedData'):
                json_start = script.text.find('{')
                json_end = script.text.rfind('}')+1
                obj = script.text[json_start:json_end]

                try:
                    data = json.loads(obj)
                except:
                    exit('Error: could not load user data')

                try:
                    user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
                    return(user_data)
                except KeyError:
                    #exit('Error: username returned no data, check if valid')
                    return None


    def user_exists(self, user):
        # Check if user exists, returns boolean

        self.db.cursor.execute("SELECT count(*) FROM Accounts WHERE username = ?", (user,))
        data = self.db.cursor.fetchone()[0]

        if data == 0:
            # print("user does not exist")
            return False
        else:
            # print("user exists")
            return True


    def add_new_user(self, user_data):
        # Adds a new user to the DB
        
        print("Adding user %s to database" % user_data["username"]) 
        
        values = (  user_data["id"],
                    user_data["username"],
                    user_data["full_name"],
                    user_data["biography"],
                    user_data["profile_pic_url"],
                    user_data["profile_pic_url_hd"],
                    user_data["external_url"],
                    user_data["external_url_linkshimmed"],
                    user_data["edge_followed_by"]["count"],
                    user_data["edge_follow"]["count"],
                    0,
                    int(user_data["is_private"]),
                    0)
        
        try:
            self.db.cursor.execute("INSERT INTO Accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            return True
        except:
            exit("Error: Adding %s into the database failed." % user_data["username"])
        

    def get_user_timestamp(self, user_id):
        # Gets the timestamp (latest upload we have in DB) of an user

        try:
            self.db.cursor.execute("SELECT last_updated FROM Accounts WHERE id=?", (user_id,))
            return(self.db.cursor.fetchone())
        except:
            exit("Error: Getting the timestamp of %s has failed." % user_id)


    def set_user_timestamp(self, user_id, timestamp):
        # Sets the timestamp (latest upload we have in DB) of an user

        try:
            self.db.cursor.execute("UPDATE Accounts SET last_updated=? WHERE id=?", (timestamp,user_id,))
        except:
            exit("Error: Setting the timestamp of %s has failed." % user_id)


    def add_data_to_db(self, user_data):
        # Adds new pictures to the DB

        user_timestamp = self.get_user_timestamp(user_data['id'])[0]

        latest_timestamp = user_data['edge_owner_to_timeline_media']['edges'][0]['node']['taken_at_timestamp']
        
        media_count = 0

        for media in user_data['edge_owner_to_timeline_media']['edges']:
            node = media['node']

            # check if media has been uploaded after the latest upload from this user
            if node['taken_at_timestamp'] > user_timestamp and node['__typename'] != 'GraphVideo':
                
                # get caption
                caption = ''
                for caption_edge in node['edge_media_to_caption']['edges']:
                    caption += caption_edge['node']['text']

                # list tagged users in a simple list
                tagged_users = []
                for tagged_user in node['edge_media_to_tagged_user']['edges']:
                    tagged_users.append(tagged_user['node']['user']['username'])

                # check if there are some "sidecar" images
                if node['__typename'] == 'GraphSidecar':
                    sidecar = json.dumps(node['edge_sidecar_to_children'])
                else:
                    sidecar = ''

                values = (    node['id'],
                              node['owner']['id'],
                              node['__typename'],
                              int(node['is_video']),             # boolean
                              node['display_url'],
                              json.dumps(node['display_resources']),
                              caption,
                              json.dumps(tagged_users),                     # JSON object with list of usernames tagged in the photo
                              node['shortcode'],
                              node['taken_at_timestamp'],
                              json.dumps(node['edge_media_preview_like']),  # JSON object containing edge_media_preview_like
                              json.dumps(node['edge_media_to_comment']),    # JSON object containing edge_media_to_comment
                              json.dumps(node['thumbnail_resources']),      # JSON object containing thumbnails
                              sidecar                                       # JSON object containing the whole edge_sidecar_to_children.edges
                              )
                
                try:
                    self.db.cursor.execute("INSERT INTO Media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                    media_count += 1
                except:
                    exit("Error: Adding an image by %s into the database failed." % user_data["username"])


        self.set_user_timestamp(user_data['id'], latest_timestamp)

        if media_count > 0:
            return("%d new media added for user %s" % (media_count, user_data['username']))
        else:
            return("No new media added for user %s" % user_data['username'])

    def tag_user_as_deleted(self, user):
        # Tags user as DELETED
        try:
            self.db.cursor.execute("UPDATE Accounts SET is_deleted=1 WHERE username=?", (user,))
        except:
            exit("Error: Changing the status of user %s failed." % user)

    def tag_user_as_existing(self, user):
        # Removes DELETED tag
        try:
            self.db.cursor.execute("UPDATE Accounts SET is_deleted=0 WHERE username=?", (user,))
        except:
            exit("Error: Changing the status of user %s failed." % user)


    def import_media(self):

        user_list = self.get_user_list()

        for user in user_list:
            user_data = self.get_user_data(user[0])

            if user_data is None:
                print('Warning: user %s has returned no data. You should check if an account still exists by that name.' % user)

            else:
                if user_data['is_private'] is False and user_data['edge_owner_to_timeline_media']['count'] > 0:
                    print(self.add_data_to_db(user_data))



if __name__ == '__main__':
    i = Importer()
    # i.init_db()
    i.import_media()
    i.close()
