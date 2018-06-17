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
