# -*- coding: utf-8 -*-
from database import Database
import config

def main():
    print('''For now, importing Instagram-exported lists is not yet possible.
Please edit %s by adding accounts.
Then run `$ python3 importer.py`.
'''
           % config.account_list_file)

if __name__ == '__main__':
    db = Database()
    db.init_db()
    main()
    db.stop_db()