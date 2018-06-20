# -*- coding: utf-8 -*-
import sqlite3

import config

class Database:
    """
    This class will start the connection to the DB and make sure we have
    the right DB structure
    """

    def __init__(self):
        self.db = sqlite3.connect(config.database_file)
        self.cursor = self.db.cursor()

    def init_db(self):
        self.db = sqlite3.connect(config.database_file)
        self.cursor = self.db.cursor()

        # Create all the DB structure if it doesn't already exist
        # Accounts :
        #   id INTEGER,
        #   username TEXT,
        #   full_name TEXT,
        #   biography TEXT,
        #   profile_pic_url TEXT,
        #   profile_pic_url_hd TEXT,
        #   external_url TEXT,
        #   external_url_linkshimmed TEXT,
        #   followed_by INTEGER,
        #   follow INTEGER,
        #   last_updated INTEGER,
        #   is_private INTEGER,
        #   is_deleted INTEGER
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Accounts (id INTEGER UNIQUE, username TEXT UNIQUE, full_name TEXT, biography TEXT, profile_pic_url TEXT, profile_pic_url_hd TEXT, external_url TEXT, external_url_linkshimmed TEXT, followed_by INTEGER, follow INTEGER, last_updated INTEGER, is_private INTEGER, is_deleted INTEGER)')

        # Media :
        #   id INTEGER,
        #   owner INTEGER,
        #   media_type TEXT,
        #   is_video INTEGER, # boolean
        #   display_url TEXT,
        #   display_resources TEXT,
        #   caption TEXT,
        #   tagged_users TEXT, # JSON object with list of usernames tagged in the photo
        #   shortcode TEXT,
        #   timestamp INTEGER,
        #   likes TEXT, # JSON object containing edge_media_preview_like
        #   comments TEXT, # JSON object containing edge_media_to_comment
        #   thumbnails TEXT, # JSON object containing thumbnails
        #   sidecar TEXT # JSON object containing the whole edge_sidecar_to_children.edges
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Media (id INTEGER UNIQUE, owner INTEGER, media_type TEXT, is_video INTEGER, display_url TEXT, display_resources TEXT, caption TEXT, tagged_users TEXT, shortcode TEXT, timestamp INTEGER, likes TEXT, comments TEXT, thumbnails TEXT, sidecar TEXT)')

        # Faves :
        #   media_id INTEGER,
        #   user_id INTEGER,
        #   filename TEXT,
        #   date_added INTEGER
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Faves (media_id INTEGER, user_id INTEGER, filename TEXT, date_added INTEGER)')

        # Lists :
        #   id INTEGER,
        #   shortname TEXT,
        #   longname TEXT,
        #   description TEXT,
        #   last_updated INTEGER
        #   date_added INTEGER
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Lists (id INTEGER PRIMARY KEY, shortname TEXT UNIQUE, longname TEXT, description TEXT, last_updated INTEGER, date_added INTEGER)')

        # AccountToList :
        #   list_id INTEGER,
        #   account_id INTEGER,
        #   date_added INTEGER
        self.cursor.execute('CREATE TABLE IF NOT EXISTS AccountToList (list_id INTEGER, account_id INTEGER, date_added INTEGER)')


        # HiddenFromFeed :
        #   user_id INTEGER,
        #   account_id INTEGER,
        self.cursor.execute('CREATE TABLE IF NOT EXISTS HiddenFromFeed (user_id INTEGER, account_id INTEGER)')


        # TODO
        # USERS :
        #   id INTEGER,
        #   name TEXT,
        #   security stuff
        #   


    def commit(self):
        # A function for commiting changes to the DB

        self.db.commit()


    def stop_db(self):
        # A function for commiting changes to the DB and closing it.
        # Because we do things properly around here

        self.db.commit()
        self.db.close()




