# -*- coding: utf-8 -*-
import sys

from database import Database
import config

class User:
    """
    This class has many helpers to set user-related stuff in the DB
    """

    def __init__(self):
        self.db = Database()

    def close(self):
        self.db.stop_db()


    def save_media(self, media_id, user_id, filename, time_added):
        """
        Marks media as saved
        """
        try:
          self.db.cursor.execute("INSERT INTO Faves VALUES (?,?,?,?)", (media_id, user_id, filename, time_added))
          return(True)
        except:
            print("Error: Media not saved.", file=sys.stderr)


    def forget_media(self, media_id, user_id):
        """
        Removes saved status
        """
        try:
            self.db.cursor.execute("DELETE FROM Faves WHERE ( media_id = ? AND user_id = ? )", (media_id, user_id))
            return(True)
        except:
            print("Error: Saved media not forgotten.", file=sys.stderr)


    def get_saved_status(self, media_id, user_id):
        """
        Marks media as saved
        """
        self.db.cursor.execute("SELECT count(*) FROM Faves WHERE  ( media_id = ? AND user_id = ? )", (media_id, user_id))
        data = self.db.cursor.fetchone()[0]
        if data == 0:
            # not saved
            return False
        else:
            # saved
            return True


    def get_saved_filename(self, media_id, user_id):
        """
        Marks media as saved
        """
        self.db.cursor.execute("SELECT filename FROM Faves WHERE  ( media_id = ? AND user_id = ? )", (media_id, user_id))
        return(self.db.cursor.fetchone()[0])


    def get_saved_date_added(self, media_id, user_id):
        """
        Marks media as saved
        """
        self.db.cursor.execute("SELECT date_added FROM Faves WHERE  ( media_id = ? AND user_id = ? )", (media_id, user_id))
        return(self.db.cursor.fetchone()[0])


    def remember_count(self, user_id):
        """
        Get a count of remembered media from an user
        """
        self.db.cursor.execute("SELECT count(*) FROM Faves WHERE user_id = ?", (user_id,))
        return(self.db.cursor.fetchone()[0])


    def remember_feed(self, user_id, page):
        """
        Returns the feed from Memory.
        """
        offset = (page - 1) * config.elements_per_page

        query = """SELECT * FROM Media
            WHERE EXISTS (SELECT * FROM Faves
                                WHERE ( Faves.user_id = ? AND Faves.media_id = Media.id ))
            ORDER BY timestamp DESC LIMIT ? OFFSET ?"""

        try:
            self.db.cursor.execute(query, (user_id, config.elements_per_page, offset))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the feed has failed.", file=sys.stderr)


    def hide_account_from_feed(self, user_id, account_id):
        """
        Hides an account from the feed
        """
        try:
          self.db.cursor.execute("INSERT INTO HiddenFromFeed VALUES (?,?)", (user_id, account_id))
          return(True)
        except:
            print("Error: Account not hidden.", file=sys.stderr)


    def show_account_on_feed(self, user_id, account_id):
        """
        De-hide an account from the feed
        """
        try:
            self.db.cursor.execute("DELETE FROM HiddenFromFeed WHERE ( user_id = ? AND account_id = ? )", (user_id, account_id))
            return(True)
        except:
            print("Error: Hidden account not de-hidden.", file=sys.stderr)


    def get_hidden_account_list(self, user_id):
        """
        Lists all accounts hidden from the feed
        Returns a list containing all accounts
        """
        query = ('''SELECT * FROM Accounts
            WHERE EXISTS (SELECT * FROM HiddenFromFeed
                                WHERE ( HiddenFromFeed.user_id = ? AND HiddenFromFeed.account_id = Accounts.id ))''')
        try:
            self.db.cursor.execute(query, (user_id,))
            return(self.db.cursor)
        except:
            print("Error: We could not fetch the list of hidden accounts.", file=sys.stderr)


    def get_hidden_status(self, user_id, account_id):
        """
        Checks if account is hidden
        """
        self.db.cursor.execute("SELECT count(*) FROM HiddenFromFeed WHERE ( user_id = ? AND account_id = ? )", (user_id, account_id))
        data = self.db.cursor.fetchone()[0]
        if data == 0:
            # not hidden
            return False
        else:
            # hidden
            return True
