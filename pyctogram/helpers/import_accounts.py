import json

from bs4 import BeautifulSoup
from requests import get

from pyctogram import db
from pyctogram.model import Account, List


def get_account_data(account_name, headers):
    # This function gets account data from the account_name
    # Returns : account data, if account_name exists
    #           None, if not
    url = f'https://instagram.com/{account_name}'
    try:
        response = get(url, headers=headers, timeout=5)
    except Exception:
        print("Error: Something happened with the connection that "
              f"prevented us to get {account_name}’s info")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script')
    for script in scripts:
        if script.text.startswith('window._sharedData'):
            json_start = script.text.find('{')
            json_end = script.text.rfind('}')+1
            obj = script.text[json_start:json_end]

            try:
                data = json.loads(obj)
                account_data = data['entry_data']['ProfilePage'][0]['graphql'][
                    'user']
                return account_data
            except Exception:
                exit('Error: could not load account data')

    return None


def create_accounts(contacts_to_import, current_user, headers, list_info):
    total = 0
    for contact in contacts_to_import:
        account = Account.query.filter_by(
            account_name=contact).first()
        if not account:
            account_data = get_account_data(contact, headers)

            if not account_data:
                continue

            account = Account(id=account_data["id"],
                              account_name=account_data["username"])  # noqa
            account.full_name = account_data["full_name"]
            account.biography = account_data["biography"]
            account.profile_pic_url = account_data[
                "profile_pic_url"]
            account.profile_pic_url_hd = account_data[
                "profile_pic_url_hd"]
            account.external_url = account_data["external_url"]
            account.external_url_linkshimmed = account_data[
                "external_url_linkshimmed"]
            account.followed_by = account_data["edge_followed_by"][
                "count"]
            account.follow = account_data["edge_follow"]["count"]
            account.last_updated = 0
            account.is_private = int(account_data["is_private"])
            db.session.add(account)

        default_list = List.query.filter_by(
            user_id=current_user.id,
            shortname=list_info['shortname']
        ).first()

        if not default_list:
            default_list = List(
                user_id=current_user.id,
                shortname=list_info['shortname'],
                longname=list_info['longname'],
                description=list_info['description'],
            )
            db.session.add(default_list)

        if account not in current_user.accounts:
            current_user.accounts.append(account)
            total += 1

        if account not in default_list.accounts:
            default_list.accounts.append(account)

    db.session.commit()
    return total
