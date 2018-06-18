# -*- coding: utf-8 -*-
import json
import config
from importer import Importer

def get_user_list_from_textfile():
    # This function gets the list of accounts to check
    # from config.account_list_file
    # Returns an object with all the accounts

    try:
        with open(config.account_list_file, 'r') as f:
            x = f.read().splitlines()
        return(x)
    except:
        exit('Error: Account list file (%s) was not found' % config.account_list_file)


def get_user_list_from_insta_export():
    # This function first asks which file to take
    # then parses it
    # Returns an object with all the accounts

    try:
        with open(config.account_json_file, 'r') as f:
            x = f.read().splitlines()
    except:
        print('The Instagram export file (\033[1m%s\033[0m) was not found.' % config.account_json_file)
        print('It could look like /Users/your_name/Downloads/your_instagram/%s' % config.account_json_file)
        print('Please enter the path at which we can access your Instagram export file.')
        path = input('--> ')
        try:
            with open(path, 'r') as f:
              x = f.read().splitlines()
        except:
            exit('Nope. Still impossible to access the file.')

    connections_list = json.loads(x[0])
    return(connections_list['following'])



def main():
    user_list = get_user_list_from_insta_export()

    print("\033[1mImporting users:\033[0m")

    for user in user_list:
        user_data = importer.get_user_data(user)

        if user_data is None:
            print('Warning: user %s has returned no data. You should check if an account still exists by that name.' % user)

        else:
            if importer.user_exists(user[0]) is False:
                importer.add_new_user(user_data)

    print("\033[1mImporting media:\033[0m")
    importer.import_media()


if __name__ == '__main__':
    importer = Importer()
    importer.init_db()
    main()
    importer.close()
