# -*- coding: utf-8 -*-
import json

import sys

from database import Database
import config

class Exporter:
    """
    This class has many helpers to get the content from the DB
    """

    def __init__(self):
        self.db = Database()

    def close(self):
        self.db.stop_db()


    def get_feed(self, page = 1, user = 0):
        """
        Returns the feed for a user, not counting hidden elements
        Note : by default, user is 0, because we don't have any user management system yet. Not sure we'll go this route.
        """
        offset = (page - 1) * config.elements_per_page

        query = """SELECT * FROM Media
            WHERE NOT EXISTS (SELECT * FROM HiddenFromFeed
                                WHERE ( HiddenFromFeed.user_id = ? AND HiddenFromFeed.account_id = Media.owner ))
            ORDER BY timestamp DESC LIMIT ? OFFSET ?"""

        try:
            self.db.cursor.execute(query, (user, config.elements_per_page, offset,))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the feed has failed.", file=sys.stderr)


    def get_feed_count(self, user = 0):
        """
        Returns the feed count for a user, not counting hidden elements
        """
        query = """SELECT count(*) FROM Media
            WHERE NOT EXISTS (SELECT * FROM HiddenFromFeed
                                WHERE ( HiddenFromFeed.user_id = ? AND HiddenFromFeed.account_id = Media.owner ))"""

        try:
            self.db.cursor.execute(query, (user,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the feed details has failed.", file=sys.stderr)


    def get_user_feed(self, user_id, page = 1):
        """
        Returns the feed for an user.
        """
        offset = (page - 1) * config.elements_per_page

        try:
            self.db.cursor.execute("SELECT * FROM Media WHERE owner = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?", (user_id, config.elements_per_page, offset,))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the timestamp of %s has failed." % user_id, file=sys.stderr)


    def get_user_feed_count(self, user_id):
        """
        Returns the feed count for an user.
        """
        try:
            self.db.cursor.execute("SELECT count(*) FROM Media WHERE owner = ?", (user_id,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the feed count for user %s has failed." % user_id, file=sys.stderr)


    def get_user_profile(self, user_id):
        """
        Returns the feed for an user.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (user_id,))
            return(self.db.cursor.fetchone())
        except:
            print("Error: Getting the profile for user %s has failed." % user_id, file=sys.stderr)


    def get_user_id_from_username(self, username):
        """
        Returns the id for an user's username.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE username = ?", (username,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the ID for %s has failed." % username, file=sys.stderr)


    def get_username_from_user_id(self, user_id):
        """
        Returns the username for an user's id.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (user_id,))
            return(self.db.cursor.fetchone()[1])
        except:
            print("Error: Getting the ID for %s has failed." % user_id, file=sys.stderr)


    def get_media_id_from_shortcode(self, shortcode):
        """
        Returns the id for the media shortcode.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Media WHERE shortcode = ?", (shortcode,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the ID for media %s has failed." % shortcode, file=sys.stderr)


    def get_media_from_shortcode(self, media_shortcode):
        """
        Returns a media object from ID.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Media WHERE shortcode = ?", (media_shortcode,))
            return(self.db.cursor.fetchone())
        except:
            print("Error: Getting the media for %s has failed." % media_shortcode, file=sys.stderr)


    def get_all_accounts_info(self):
        """
        Return a tuple of tuples, containing user info for all the users in a list
        """
        try:
            query = "SELECT * FROM Accounts"
            self.db.cursor.execute(query)
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the accounts has failed.", file=sys.stderr)
