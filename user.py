# -*- coding: utf-8 -*-
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
            exit("Error: Media not saved.")

    def forget_media(self, media_id, user_id):
        """
        Removes saved status
        """
        try:
            self.db.cursor.execute("DELETE FROM Faves WHERE ( media_id = ? AND user_id = ? )", (media_id, user_id))
            return(True)
        except:
            exit("Error: Saved media not forgotten.")

    def get_saved_status(self, media_id, user_id):
        """
        Marks media as saved
        """
        self.db.cursor.execute("SELECT count(*) FROM Faves WHERE  ( media_id = ? AND user_id = ? )", (media_id, user_id))
        data = self.db.cursor.fetchone()[0]
        if data == 0:
            # print("not saved")
            return False
        else:
            # print("saved")
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

    def remember(self, user_id):
        """
        Get a list of all remembered media
        """
        self.db.cursor.execute("SELECT media_id FROM Faves WHERE user_id = ?", (user_id,))
        return(self.db.cursor.fetchall())



    def hide_account_from_feed(self, user_id, account_id):
        """
        Hides an account from the feed
        """
        try:
          self.db.cursor.execute("INSERT INTO HiddenFromFeed VALUES (?,?)", (user_id, account_id))
          return(True)
        except:
            exit("Error: Account not hidden.")

    def show_account_on_feed(self, user_id, account_id):
        """
        De-hide an account from the feed
        """
        try:
            self.db.cursor.execute("DELETE FROM HiddenFromFeed WHERE ( user_id = ? AND account_id = ? )", (user_id, account_id))
            return(True)
        except:
            exit("Error: Hidden account not de-hidden.")

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
            exit("Error: We could not fetch the list of hidden accounts.")


    def get_hidden_status(self, user_id, account_id):
        """
        Checks if account is hidden
        """
        self.db.cursor.execute("SELECT count(*) FROM HiddenFromFeed WHERE ( user_id = ? AND account_id = ? )", (user_id, account_id))
        data = self.db.cursor.fetchone()[0]
        if data == 0:
            # print("not hidden")
            return False
        else:
            # print("hidden")
            return True
