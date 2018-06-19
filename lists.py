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
        '''
        Returns a tuple as:
            id INTEGER,
            shortname TEXT,
            longname TEXT,
            description TEXT,
            last_updated INTEGER,
            date_added INTEGER,
            count INTEGER
        count is the number of accounts present in the list
        '''

        self.db.cursor.execute("SELECT * FROM Lists WHERE id = ?", (list_id,))
        the_list = self.db.cursor.fetchone()

        self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (the_list[0],))

        return(the_list + (self.db.cursor.fetchone()[0],))


    def get_list_accounts_info(self, list_id):
        '''
        Return a tuple of tuples, containing user info for all the users in a list
        '''
        try:
            self.db.cursor.execute("SELECT account_id FROM AccountToList WHERE list_id = ?", (list_id,))
            accounts = tuple([str(i[0]) for i in self.db.cursor.fetchall()])
        except:
            exit("Error: Getting the accounts for %s has failed." % shortname)
            #print(str(accounts), file=sys.stderr)

        try:
            query = "SELECT * FROM Accounts WHERE id IN (%s)" % ','.join('?' for i in accounts)
            self.db.cursor.execute(query, accounts)
            return(self.db.cursor.fetchall())
        except:
            exit("Error: Getting the accounts has failed.")


    def get_list_feed(self, list_id, page = 1):
        '''
        Returns the feed.
        '''
        offset = (page - 1) * config.elements_per_page

        try:
            self.db.cursor.execute("SELECT account_id FROM AccountToList WHERE list_id = ?", (list_id,))
            accounts = tuple([str(i[0]) for i in self.db.cursor.fetchall()])
        except:
            exit("Error: Getting the accounts for %s has failed." % shortname)
            #print(str(accounts), file=sys.stderr)

        try:
            query = "SELECT * FROM Media WHERE owner IN (%s) ORDER BY timestamp DESC LIMIT ? OFFSET ?" % ','.join('?' for i in accounts)
            self.db.cursor.execute(query, accounts + (config.elements_per_page, offset))
            return(self.db.cursor.fetchall())
        except:
            exit("Error: Getting the feed has failed.")


    def get_list_feed_count(self, list_id):
        """
        Returns the feed count.
        """
        try:
            self.db.cursor.execute("SELECT account_id FROM AccountToList WHERE list_id = ?", (list_id,))
            accounts = [str(i[0]) for i in self.db.cursor.fetchall()]
        except:
            exit("Error: Getting the accounts for %s has failed." % shortname)

        try:
            query = "SELECT count(*) FROM Media WHERE owner IN (%s)" % ','.join('?' for i in accounts)
            self.db.cursor.execute(query, accounts)
            return(self.db.cursor.fetchone()[0])
        except:
            exit("Error: Getting the feed details has failed.")


    def get_list_id_from_shortname(self, shortname):
        try:
            shortname
        except:
            exit("Error : shortname not supplied")

        try:
            self.db.cursor.execute("SELECT * FROM Lists WHERE shortname = ?", (shortname,))
            return(self.db.cursor.fetchone()[0])
        except:
            exit("Error: Getting the ID for %s has failed." % shortname)


    def get_all_lists_info(self):
        '''
        Returns a tuple of tuples as:
            id INTEGER,
            shortname TEXT,
            longname TEXT,
            description TEXT,
            last_updated INTEGER,
            date_added INTEGER,
            count INTEGER
        count is the number of accounts present in the list
        '''


        self.db.cursor.execute("SELECT * FROM Lists")
        all_lists = self.db.cursor.fetchall()

        final_list = ()
        for single_list in all_lists:
            self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (single_list[0],))
            final_list += (single_list + (self.db.cursor.fetchone()[0],),)


        return(final_list)


    def get_lists_info_for_user(self, account_id):
        '''
        Returns a tuple containing all the lists for a given user
        Returns a tuple of tuples as:
            id INTEGER,
            shortname TEXT,
            longname TEXT,
            description TEXT,
            last_updated INTEGER,
            date_added INTEGER,
            count INTEGER
        count is the number of accounts present in the list
        '''


        self.db.cursor.execute("SELECT * FROM AccountToList WHERE account_id = ?", (account_id,))
        lists_id = [str(i[0]) for i in self.db.cursor.fetchall()]

        query = "SELECT * FROM Lists WHERE id IN (%s)" % ','.join('?' for i in lists_id)
        self.db.cursor.execute(query, lists_id)

        all_lists = self.db.cursor.fetchall()

        final_list = ()
        for single_list in all_lists:
            self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ?", (single_list[0],))
            final_list += (single_list + (self.db.cursor.fetchone()[0],),)

        return(final_list)


    # MANIPULATE LISTS

    def check_if_account_in_list(self, list_id, account_id):
        # Check if username exists, returns boolean
        
        self.db.cursor.execute("SELECT count(*) FROM AccountToList WHERE list_id = ? AND account_id = ?", (list_id, account_id,))
        data = self.db.cursor.fetchone()[0]
        self.db.commit()

        if data == 0:
            # print("user does not exist")
            return False
        else:
            # print("user exists")
            return True

        

    def add_account_to_list(self, list_id, account_id):
        # AccountToList :
        #   list_id INTEGER,
        #   account_id INTEGER,
        #   date_added INTEGER

        values = (list_id, account_id, time.time())

        try:
            self.db.cursor.execute("INSERT INTO AccountToList VALUES (?, ?, ?)", values)
            self.db.commit()

        except:
            exit("Error: Adding %s into the database failed." % account_id)
        
    def remove_account_from_list(self, list_id, account_id):

        values = (list_id, account_id)

        try:
            self.db.cursor.execute("DELETE FROM AccountToList WHERE list_id = ? AND account_id = ?", values)
            self.db.commit()

        except:
            exit("Error: Deleting %s from the database failed." % list_id)


    def add_accounts_to_list(self, list_id, list_of_accounts):
        for account in list_of_accounts:
            self.add_account_to_list(list_id, account)
        

    def remove_accounts_from_list(self, list_id, list_of_accounts):
        for account in list_of_accounts:
            self.remove_account_from_list(list_id, account)
        


    def create_new_list(self, list_info):
        # Lists :
        #   id INTEGER,
        #   shortname TEXT,
        #   longname TEXT,
        #   description TEXT,
        #   last_updated INTEGER
        #   date_added INTEGER

        values = (  list_info["shortname"],
                    list_info["longname"],
                    list_info["description"],
                    0,
                    time.time() )
        
        try:
            self.db.cursor.execute("INSERT INTO Lists (shortname, longname, description, last_updated, date_added) VALUES (?, ?, ?, ?, ?)", values)
            self.db.commit()
            return True
        except:
            exit("Error: Adding %s into the database failed." % list_info["shortname"])

    def delete_list(self, list_id):

        try:
            self.db.cursor.execute("DELETE FROM Lists WHERE id = ?", str(list_id))
            self.db.cursor.execute("DELETE FROM AccountToList WHERE list_id = ?", str(list_id))

            self.db.commit()
            return True
        except:
           exit("Error: Deleting %s from the database failed." % list_id)


