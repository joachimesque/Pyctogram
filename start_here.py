# -*- coding: utf-8 -*-
import os
import json
import config
from importer import Importer
from lists import Lists

import argparse

DEFAULT_USER_ID = 0
DEFAULT_LIST_INFO = {'shortname': '_feed',
                     'longname': 'Feed',
                     'description': 'Default Feed List'}

def get_account_list_from_textfile(text_file):
    # This function gets the list of accounts to check
    # from config.account_list_file
    # Returns an object with all the accounts

    try:
        with open(text_file, 'r') as f:
            x = f.read().splitlines()
        return(x)
    except:
        exit('Error: Account list file (%s) was not found' % text_file)


def get_account_list_from_insta_export(instagram_export_path):
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
        print('It could look like /accounts/your_name/Downloads/your_instagram/%s' % file_path)
        print('Please enter the path at which we can access your Instagram export file.')
        path = input('--> ')
        try:
            with open(path, 'r') as f:
              x = f.read().splitlines()
        except:
            exit('Nope. Still impossible to access the file.')

    connections_list = json.loads(x[0])
    return(connections_list['following'])



def import_account_list(from_text_file = None, from_list = None, from_instagram = None):
    importer = Importer()
    importer.init_db()

    if from_text_file is not None:
      account_list = get_account_list_from_textfile(from_text_file)
    elif from_list is not None:
      account_list = from_list
    else:
      account_list = get_account_list_from_insta_export(from_instagram)

    print("\033[1mImporting accounts:\033[0m")

    account_count = 0

    if account_list != []:
        importer.create_new_list(list_info = DEFAULT_LIST_INFO, user_id = DEFAULT_USER_ID, is_hidden = 1)
        _feed_list = importer.get_list_id_from_shortname(shortname = DEFAULT_LIST_INFO['shortname'], user_id = DEFAULT_USER_ID)

    failed_accounts = []

    for index, account in enumerate(account_list):
        if importer.account_exists(account) is False:
            account_data = importer.get_account_data(account)
            i = index + 1

            if account_data is None:
                status = '🤷‍♀ Account %s has returned no data' % account
                importer.progress(i, len(account_list), status = status)

                # print('Warning: account %s has returned no data. You should check if an account still exists by that name.' % account)
                failed_accounts.append(account)
            else:
                if importer.add_new_account(account_data = account_data):
                    importer.link_account_to_user(user_id = DEFAULT_USER_ID, account_id = account_data["id"])
                    importer.add_account_to_list(list_id = _feed_list, account_id = account_data["id"])

                    if account_data['is_private'] is False and account_data['edge_owner_to_timeline_media']['count'] > 0:
                        media_added = importer.add_data_to_db(account_data)
                        if media_added > 0:
                          status = '🙋‍♀ Added %s media for %s' % (media_added, account)
                          importer.progress(i, len(account_list), status = status)
                          #print("%d/%d : %d new media added for account %s" % (index + 1, len(account_list), media_added, account_data['username']))
                    else:
                        status = '🙅‍♀ No new media for %s' % account
                        importer.progress(i, len(account_list), status = status)

                    account_count += 1

                else:
                    status = '🤦‍♀ Could not save %s’s info' % account
                    importer.progress(i, len(account_list), status = status)
                    failed_accounts.append(account)

                importer.commit()

    if account_count > 1:
        print("\033[1m%s\033[0m new accounts were added" % account_count)
    elif account_count > 0:
        print("\033[1mOne\033[0m new account was added")
    else:
        print("No new accounts were added")

    if failed_accounts != []:
        error_file_name = 'missed_connections.txt'
        print("%s accounts could not be imported." % len(failed_accounts))
        with open(error_file_name, 'w') as file:
            file.write('\n'.join(failed_accounts))
            print("To try importing them again, you can run the script again,"\
                  " with the argument: \033[1m-t %s\033[0m" % error_file_name)

    importer.close()


def file_exists(string):
    if not os.path.isfile(str(string)):
        msg = "%s is not a valid file" % string
        raise argparse.ArgumentTypeError(msg)
    return str(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start up your Pyctogram installation by adding some accounts.',
                                      prog='Pyctogram')
    parser.add_argument('-i','--from_instagram',help='''Import from the `connections.json` export file from Instagram.
      Please supply a valid path to the file.''', type=file_exists)
    parser.add_argument('-t','--from_text_file',help='''Import from a text file containing one username per line.
      Please supply a valid path to the file.''', type=file_exists)
    parser.add_argument('-l','--from_list',help='Import from a list of usernames, separated by commas: joachimrobert,instagram')

    args = parser.parse_args()

    if args.from_instagram:
        print("Importing from source: %s" % args.from_instagram)
        import_account_list(from_instagram = args.from_instagram)

    if args.from_text_file:
        print("Importing from source: %s" % args.from_text_file)
        import_account_list(from_text_file = args.from_text_file)

    if args.from_list:
        print("Importing from list: %s" % args.from_list)
        list_value = args.from_list.split(',')
        import_account_list(from_list = list_value)

    if not any(vars(args).values()):
        import_account_list()
