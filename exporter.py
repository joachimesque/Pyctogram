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


    def get_account_feed(self, account_id, page = 1):
        """
        Returns the feed for an user.
        """
        offset = (page - 1) * config.elements_per_page

        try:
            self.db.cursor.execute("SELECT * FROM Media WHERE owner = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?", (account_id, config.elements_per_page, offset,))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the timestamp of %s has failed." % account_id, file=sys.stderr)


    def get_account_feed_count(self, account_id):
        """
        Returns the feed count for an user.
        """
        try:
            self.db.cursor.execute("SELECT count(*) FROM Media WHERE owner = ?", (account_id,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the feed count for user %s has failed." % account_id, file=sys.stderr)


    def get_account_profile(self, account_id):
        """
        Returns the feed for an user.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (account_id,))
            return(self.db.cursor.fetchone())
        except:
            print("Error: Getting the profile for user %s has failed." % account_id, file=sys.stderr)


    def get_account_id_from_account_name(self, account_name):
        """
        Returns the id for an user's account_name.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE account_name = ?", (account_name,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the ID for %s has failed." % account_name, file=sys.stderr)


    def get_account_name_from_account_id(self, account_id):
        """
        Returns the account_name for an account's id.
        """
        try:
            self.db.cursor.execute("SELECT * FROM Accounts WHERE id = ?", (account_id,))
            return(self.db.cursor.fetchone()[1])
        except:
            print("Error: Getting the ID for %s has failed." % account_id, file=sys.stderr)


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


    def get_all_accounts_info(self, user_id):
        """
        Return a tuple of tuples, containing account info for all the accounts in a list
        """
        try:
            query = """SELECT * FROM Accounts
                    WHERE EXISTS (SELECT * FROM AccountToUser
                                    WHERE AccountToUser.account_id = Accounts.id AND AccountToUser.user_id = ?)"""
            self.db.cursor.execute(query, (user_id,))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the accounts has failed.", file=sys.stderr)

