import sys

from flask import url_for


def get_redirection(origin, media_shortcode, media_owner=''):
    origin_list = origin.split(':')
    endpoint = origin_list[0]
    destination_page = int(origin_list[-1]) if origin_list[-1] != '' else 0
    destination = origin_list[1] if len(origin_list) > 2 else ''

    if endpoint[0:7] == 'profile':
        if destination[0] == '@':  # link from the header
            media_owner = destination[1:]
            destination = 'top'

        if endpoint == 'profile_lists':
            return url_for('account.profile_lists', account_name=media_owner
                           ).replace('%40', '@')
        elif endpoint == 'profile_feed':
            return url_for('account.profile', page=destination_page,
                           account_name=media_owner, display='feed',
                           _anchor=destination).replace('%40', '@')
        else:
            return url_for('account.profile', page=destination_page,
                           account_name=media_owner,
                           _anchor=destination).replace('%40', '@')

    elif endpoint == 'profile_lists':
        return url_for(endpoint, account_name=destination[1:])

    elif endpoint == 'index':
        # Get the shortcode of the previous item BEFORE CALLING THE FUNCTION,
        # pass as media_shortcode
        if media_shortcode == '':
            media_shortcode = destination
        return url_for(endpoint, page=destination_page,
                       _anchor=media_shortcode)

    elif endpoint == 'memory':
        # Get the shortcode of the previous item BEFORE CALLING THE FUNCTION,
        # pass as media_shortcode
        return url_for(endpoint, page=destination_page, _anchor=destination)

    elif endpoint == 'media':
        return url_for('media', media_shortcode=media_shortcode)

    elif endpoint == 'list.list_feed':
        print(('ok', destination, media_shortcode), file=sys.stderr)
        return url_for(endpoint, shortname=destination,
                       _anchor=media_shortcode)

    else:
        return url_for(endpoint, page=destination_page, _anchor=destination)
