# -*- coding: utf-8 -*-
import time
from database import Database
import config
import sys

class Lists:
    """
    This class has many helpers to get the content from the DB
    """

    def __init__(self):
        self.db = Database()

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.stop_db()


    def get_list_info(self, list_id):
        """
        Returns a tuple as:
            id INTEGER,
            shortname TEXT,
            longname TEXT,
            description TEXT,
            last_updated INTEGER,
            date_added INTEGER,
            count INTEGER
        count is the number of accounts present in the list
        """

        self.db.cursor.execute("SELECT * FROM Lists WHERE id = ?", (list_id,))
        the_list = self.db.cursor.fetchone()

        self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (list_id,))

        return(the_list + (self.db.cursor.fetchone()[0],))

    def get_all_lists_info(self, user_id):
        """
        Returns a tuple of tuples as:
            id INTEGER,
            shortname TEXT,
            longname TEXT,
            description TEXT,
            last_updated INTEGER,
            date_added INTEGER,
            count INTEGER
        count is the number of accounts present in the list
        """
        self.db.cursor.execute("SELECT * FROM Lists WHERE user_id = ? AND is_hidden = 0", (user_id,))
        all_lists = self.db.cursor.fetchall()

        # This will add the count to the `list` objects
        final_list = ()
        for single_list in all_lists:
            self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (single_list[0],))
            final_list += (single_list + (self.db.cursor.fetchone()[0],),)

        return(final_list)


    def get_lists_info_for_account(self, user_id, account_id):
        """
        Returns a tuple containing all the lists in which there is a specific account
        Returns a tuple of `list` objects
        count is the number of accounts present in the list
        """
        query = """SELECT * FROM Lists
                WHERE user_id = ? AND is_hidden = 0
                    AND EXISTS (SELECT * FROM AccountToList
                                WHERE ( AccountToList.account_id = ? AND AccountToList.list_id = Lists.id))"""

        self.db.cursor.execute(query, (user_id, account_id,))
        all_lists = self.db.cursor.fetchall()

        # This will add the count to the `list` objects
        final_list = ()
        for single_list in all_lists:
            self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (single_list[0],))
            final_list += (single_list + (self.db.cursor.fetchone()[0],),)

        return(final_list)



    def get_list_accounts_info(self, list_id):
        """
        Return a tuple of tuples, containing account info for all the accounts in a list
        """
        query = """SELECT * FROM Accounts
            WHERE EXISTS (SELECT * FROM AccountToList
                            WHERE (AccountToList.list_id = ? AND AccountToList.account_id = Accounts.id))"""

        try:
            self.db.cursor.execute(query, (list_id,))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the accounts has failed.", file=sys.stderr)


    def get_list_feed(self, list_id, page = 1):
        """
        Returns the feed.
        """
        offset = (page - 1) * config.elements_per_page

        query = """SELECT * FROM Media
            WHERE EXISTS (SELECT * FROM AccountToList
                            WHERE (AccountToList.list_id = ? AND AccountToList.account_id = Media.owner))
            ORDER BY timestamp DESC LIMIT ? OFFSET ?"""

        try:
            self.db.cursor.execute(query, (list_id, config.elements_per_page, offset))
            return(self.db.cursor.fetchall())
        except:
            print("Error: Getting the feed has failed.", file=sys.stderr)


    def get_list_feed_count(self, list_id):
        """
        Returns the feed count.
        """
        query = """SELECT count(*) FROM Media
            WHERE EXISTS (SELECT * FROM AccountToList
                            WHERE (AccountToList.list_id = ? AND AccountToList.account_id = Media.owner))"""

        try:
            self.db.cursor.execute(query, (list_id,))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the feed details has failed.", file=sys.stderr)


    def get_list_id_from_shortname(self, shortname, user_id):
        """
        Gets the list id (int) from the list shortname and the user_id
        """
        try:
            self.db.cursor.execute("SELECT * FROM Lists WHERE ( shortname = ? AND user_id = ?)", (shortname,user_id))
            return(self.db.cursor.fetchone()[0])
        except:
            print("Error: Getting the ID for %s has failed." % shortname, file=sys.stderr)



    # MANIPULATE LISTS

    def check_if_account_in_list(self, list_id, account_id):
        """
        Checks if account exists in a list, returns boolean
        """
        
        self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ? AND account_id = ?", (list_id, account_id,))
        data = self.db.cursor.fetchone()[0]
        self.db.commit()

        if data == 0:
            # user does not exist
            return False
        else:
            # user exists
            return True


    def check_if_list_name_unique_for_user(self, list_id, user_id):
        """
        Checks if list name exists, returns boolean
        """
        
        self.db.cursor.execute("SELECT count(*) FROM Lists WHERE list_id = ? AND user_id = ? AND is_hidden = 0", (list_id, user_id,))
        data = self.db.cursor.fetchone()[0]
        self.db.commit()

        if data == 0:
            # user does not exist
            return False
        else:
            # user exists
            return True


    def add_account_to_list(self, list_id, account_id):
        """
        Adds an account to a list
        """
        values = (list_id, account_id, time.time())

        try:
            self.db.cursor.execute("INSERT INTO AccountToList VALUES (?, ?, ?)", values)
            self.db.commit()

        except:
            print("Error: Adding %s into the database failed." % account_id, file=sys.stderr)
        

    def remove_account_from_list(self, list_id, account_id):
        """
        Removes one account from a list
        """
        values = (list_id, account_id)
        try:
            self.db.cursor.execute("DELETE FROM AccountToList WHERE list_id = ? AND account_id = ?", values)
            self.db.commit()

        except:
            print("Error: Deleting %s from the database failed." % list_id, file=sys.stderr)


    def add_accounts_to_list(self, list_id, list_of_accounts):
        """
        Adds many accounts from a list
        """
        for account in list_of_accounts:
            self.add_account_to_list(list_id, account)
        

    def remove_accounts_from_list(self, list_id, list_of_accounts):
        """
        Removes many accounts from a list
        """
        for account in list_of_accounts:
            self.remove_account_from_list(list_id, account)
        

    def create_new_list(self, list_info, user_id, is_hidden = 0):
        """
        Creates a new list
        """
        values = (  list_info["shortname"],
                    list_info["longname"],
                    list_info["description"],
                    0,
                    time.time(),
                    user_id,
                    is_hidden )
        
        try:
            self.db.cursor.execute("INSERT INTO Lists (shortname, longname, description, last_updated, date_added, user_id, is_hidden) VALUES (?, ?, ?, ?, ?, ?, ?)", values)
            self.db.commit()
        except:
            print("Error: Adding %s into the database failed." % list_info["shortname"], file=sys.stderr)


    def modify_list(self, list_id, list_info):
        """
        Modifies a list from values supplied in list_info, returns True.
        """
        values = (  list_info["shortname"],
                    list_info["longname"],
                    list_info["description"])
        try:
            self.db.cursor.execute("UPDATE Lists SET shortname = ?, longname = ?, description = ? WHERE id = ?", values + (list_id,))
            self.db.commit()
            return True
        except:
            print("Error: Adding %s into the database failed." % list_info["shortname"], file=sys.stderr)


    def delete_list(self, list_id):
        """
        Deletes a list. Simple. Basic.
        """
        try:
            self.db.cursor.execute("DELETE FROM Lists WHERE id = ?", str(list_id))
            self.db.cursor.execute("DELETE FROM AccountToList WHERE list_id = ?", str(list_id))

            self.db.commit()
            return True
        except:
           print("Error: Deleting %s from the database failed." % list_id, file=sys.stderr)


    def get_page_number_where_shortcode_is_displayed_in_list(self, list_id, media_shortcode):
        """
        Returns the value of the page in a feed where a media is located
        It gets the count of elements (selected from the right list)
                                    that have a timestamp superior to the timestamp
                                        of the element that has `media_shortcode`
        """
        query = """SELECT count(*) FROM Media
                    WHERE EXISTS (SELECT * FROM AccountToList
                                    WHERE (AccountToList.list_id = ?
                                            AND AccountToList.account_id = Media.owner))
                    AND timestamp > (SELECT timestamp FROM Media WHERE shortcode = ?)"""
        try:
            self.db.cursor.execute(query, (list_id, media_shortcode))
            count = self.db.cursor.fetchone()[0]
        except:
           print("Error: Duuuuuude.", file=sys.stderr)

        return count
