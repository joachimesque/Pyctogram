import json

from bs4 import BeautifulSoup
from requests import get


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
