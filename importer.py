# -*- coding: utf-8 -*-
import config

from requests import get
from bs4 import BeautifulSoup
import json
import time

from database import Database


class Importer:

    def __init__(self):
        self.db = Database()

    def init_db(self):
        self.db.init_db()

    def close(self):
        self.db.stop_db()

    def get_account_list(self):
        # This function gets the list of accounts to check
        # from database
        # Returns an object with all the accounts

        try:
            self.db.cursor.execute("SELECT account_name FROM Accounts ORDER BY last_updated DESC")
            return(self.db.cursor.fetchall())
        except:
            exit("Error: Getting list of accounts has failed.")


    def get_account_data(self, account_name):
        # This function gets account data from the account_name
        # Returns : account data, if account_name exists
        #           None, if not


        url = 'https://instagram.com/%s' % account_name
        try:
            response = get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'})
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
                    exit('Error: could not load account data')

                try:
                    account_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
                    return(account_data)
                except KeyError:
                    #exit('Error: account_name returned no data, check if valid')
                    return None


    def account_exists(self, account_name):
        # Check if account_name exists, returns boolean

        self.db.cursor.execute("SELECT count(*) FROM Accounts WHERE account_name = ?", (account_name,))
        data = self.db.cursor.fetchone()[0]
        self.db.commit()

        if data == 0:
            # print("account does not exist")
            return False
        else:
            # print("account exists")
            return True


    def add_new_account(self, account_data):
        # Adds a new account to the DB
        # username is account_name in DB

        print("New account added to database : %s" % account_data["username"]) 
        
        values = (  account_data["id"],
                    account_data["username"],
                    account_data["full_name"],
                    account_data["biography"],
                    account_data["profile_pic_url"],
                    account_data["profile_pic_url_hd"],
                    account_data["external_url"],
                    account_data["external_url_linkshimmed"],
                    account_data["edge_followed_by"]["count"],
                    account_data["edge_follow"]["count"],
                    0,
                    int(account_data["is_private"]))
        
        try:
            self.db.cursor.execute("INSERT INTO Accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            self.db.commit()
            return True
        except:
            exit("Error: Adding %s into the database failed." % account_data["username"])
        

    def link_account_to_user(self, user_id, account_id):

        values = (user_id, account_id, time.time())

        try:
            self.db.cursor.execute("INSERT INTO AccountToUser VALUES (?, ?, ?)", values)
            self.db.commit()
            return True
        except:
            exit("Error: Linking user %s to account %s in the database failed." % (user_id, account_id))


    def get_account_timestamp(self, account_id):
        # Gets the timestamp (latest upload we have in DB) of an account

        try:
            self.db.cursor.execute("SELECT last_updated FROM Accounts WHERE id=?", (account_id,))
            ts = self.db.cursor.fetchone()
            self.db.commit()
            return(ts)
        except:
            exit("Error: Getting the timestamp of %s has failed." % account_id)


    def set_account_timestamp(self, account_id, timestamp):
        # Sets the timestamp (latest upload we have in DB) of an account

        try:
            self.db.cursor.execute("UPDATE Accounts SET last_updated=? WHERE id=?", (timestamp,account_id,))
            self.db.commit()
        except:
            exit("Error: Setting the timestamp of %s has failed." % account_id)


    def add_data_to_db(self, account_data):
        # Adds new pictures to the DB

        account_timestamp = self.get_account_timestamp(account_data['id'])[0]

        latest_timestamp = account_data['edge_owner_to_timeline_media']['edges'][0]['node']['taken_at_timestamp']
        
        media_count = 0

        for media in account_data['edge_owner_to_timeline_media']['edges']:
            node = media['node']

            # check if media has been uploaded after the latest upload from this account
            if node['taken_at_timestamp'] > account_timestamp and node['__typename'] != 'GraphVideo':
                
                # get caption
                caption = ''
                for caption_edge in node['edge_media_to_caption']['edges']:
                    caption += caption_edge['node']['text']

                # list tagged accounts in a simple list
                tagged_accounts = []
                if 'edge_media_to_tagged_user' in node:
                    for tagged_account in node['edge_media_to_tagged_user']['edges']:
                        tagged_accounts.append(tagged_account['node']['user']['username'])

                # check if there are some "sidecar" images
                if node['__typename'] == 'GraphSidecar':
                    sidecar = json.dumps(node['edge_sidecar_to_children']) if 'edge_sidecar_to_children' in node else ''
                else:
                    sidecar = ''

                values = (    node['id'],
                              node['owner']['id'],
                              node['__typename'],
                              int(node['is_video']),             # boolean
                              node['display_url'],
                              json.dumps(node['display_resources']) if 'display_resources' in node else '',
                              caption,
                              json.dumps(tagged_accounts),                     # JSON object with list of account_names tagged in the photo
                              node['shortcode'],
                              node['taken_at_timestamp'],
                              json.dumps(node['edge_media_preview_like']) if 'edge_media_preview_like' in node else '',  # JSON object containing edge_media_preview_like
                              json.dumps(node['edge_media_to_comment']) if 'edge_media_to_comment' in node else '',    # JSON object containing edge_media_to_comment
                              json.dumps(node['thumbnail_resources']) if 'thumbnail_resources' in node else '',      # JSON object containing thumbnails
                              sidecar                                       # JSON object containing the whole edge_sidecar_to_children.edges
                              )

                try:
                    self.db.cursor.execute("INSERT INTO Media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                    self.db.commit()
                    media_count += 1
                except:
                    exit("Error: Adding an image by %s into the database failed." % account_data["username"])


        self.set_account_timestamp(account_data['id'], latest_timestamp)

        return media_count

    def tag_account_as_deleted(self, account):
        # Tags account as DELETED
        try:
            self.db.cursor.execute("UPDATE Accounts SET is_deleted=1 WHERE account_name=?", (account,))
            self.db.commit()
        except:
            exit("Error: Changing the status of account %s failed." % account)

    def tag_account_as_existing(self, account):
        # Removes DELETED tag
        try:
            self.db.cursor.execute("UPDATE Accounts SET is_deleted=0 WHERE account_name=?", (account,))
            self.db.commit()
        except:
            exit("Error: Changing the status of account %s failed." % account)


    def import_media(self, from_accounts = None):

        print("\033[1mImporting media:\033[0m")

        if from_accounts is not None:
            account_list = from_accounts
        else:
            account_list = [i[0] for i in self.get_account_list()]

        self.db.commit()

        account_count = 0
        total_media_added = 0

        for index, account in enumerate(account_list):
            account_data = self.get_account_data(account)

            if account_data is None:
                print('Warning: account %s has returned no data. You should check if an account still exists by that name.' % account)

            else:
                if account_data['is_private'] is False and account_data['edge_owner_to_timeline_media']['count'] > 0:
                    media_added = self.add_data_to_db(account_data)
                    if media_added > 0:
                        print("%d/%d : %d new media added for account %s" % (index + 1, len(account_list), media_added, account_data['username']))
                        account_count += 1
                    total_media_added += media_added


        if account_count > 1:
            print("We got \033[1m%s\033[0m new media from \033[1m%s\033[0m accounts" % (total_media_added, account_count))
        elif account_count > 0:
            print("We got \033[1m%s\033[0m new media from \033[1mone\033[0m account" % total_media_added)
        else:
            print("No new media were found at this time")


if __name__ == '__main__':
    i = Importer()
    # i.init_db()
    i.import_media()
    i.close()
