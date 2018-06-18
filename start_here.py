# -*- coding: utf-8 -*-
import os
import json
import config
from importer import Importer

import argparse


def get_user_list_from_textfile(text_file):
    # This function gets the list of accounts to check
    # from config.account_list_file
    # Returns an object with all the accounts

    try:
        with open(text_file, 'r') as f:
            x = f.read().splitlines()
        return(x)
    except:
        exit('Error: Account list file (%s) was not found' % text_file)


def get_user_list_from_insta_export(instagram_export_path):
    # This function first asks which file to take
    # then parses it
    # Returns an object with all the accounts
  
    if instagram_export_path is not None:
      file_path = instagram_export_path
    else:
      file_path = config.account_json_file

    try:
        with open(file_path, 'r') as f:
            x = f.read().splitlines()
    except:
        print('The Instagram export file (\033[1m%s\033[0m) was not found.' % file_path)
        print('It could look like /Users/your_name/Downloads/your_instagram/%s' % file_path)
        print('Please enter the path at which we can access your Instagram export file.')
        path = input('--> ')
        try:
            with open(path, 'r') as f:
              x = f.read().splitlines()
        except:
            exit('Nope. Still impossible to access the file.')

    connections_list = json.loads(x[0])
    return(connections_list['following'])



def import_user_list(from_text_file = None, from_list = None, from_instagram = None):
    importer = Importer()
    importer.init_db()

    if from_text_file is not None:
      user_list = get_user_list_from_textfile(from_text_file)
    elif from_list is not None:
      user_list = from_list
    else:
      user_list = get_user_list_from_insta_export(from_instagram)

    print("\033[1mImporting users:\033[0m")

    user_count = 0

    for user in user_list:
        if importer.user_exists(user) is False:
            user_data = importer.get_user_data(user)

            if user_data is None:
                print('Warning: user %s has returned no data. You should check if an account still exists by that name.' % user)

            else:
                importer.add_new_user(user_data)
                user_count += 1

    if user_count > 1:
        print("\033[1m%s\033[0m new users were added" % user_count)
    elif user_count > 0:
        print("\033[1mOne\033[0m new user was added")
    else:
        print("No new users were added")

    importer.import_media(from_users=user_list)
    importer.close()


def file_exists(string):
    if not os.path.isfile(str(string)):
        msg = "%s is not a valid file" % string
        raise argparse.ArgumentTypeError(msg)
    return str(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start up your Pyctogram installation by adding some users.', prog='Pyctogram')
    parser.add_argument('-i','--from_instagram',help='''Import from the `connections.json` export file from Instagram.
      Please supply a valid path to the file.''', type=file_exists)
    parser.add_argument('-t','--from_text_file',help='''Import from a text file containing one username per line.
      Please supply a valid path to the file.''', type=file_exists)
    parser.add_argument('-l','--from_list',help='Import from a list of usernames, separated by commas : joachimrobert,instagram')

    args = parser.parse_args()

    if args.from_instagram:
        print("Importing from source: %s" % args.from_instagram)
        import_user_list(from_instagram=args.from_instagram)

    if args.from_text_file:
        print("Importing from source: %s" % args.from_text_file)
        import_user_list(from_text_file=args.from_text_file)

    if args.from_list:
        print("Importing from list: %s" % args.from_list)
        list_value = args.from_list.split(',')
        import_user_list(from_list=list_value)

    if not any(vars(args).values()):
        import_user_list()
