# -*- coding: utf-8 -*-

import time
from time import strftime
from exporter import Exporter

def display_feed(page):
    feed = e.get_feed(page)

    for media in feed:
        media_id = media[0]
        owner = media[1]
        media_type = media[2]
        is_video = bool(media[3])
        display_url = media[4]
        display_resources = media[5]
        caption = media[6]
        tagged_users = media[7]
        shortcode = media[8]
        timestamp = time.gmtime(media[9])
        likes = media[10]
        comments = media[11]
        thumbnails = media[12]
        sidecar = media[13]

        owner_profile = e.get_user_profile(owner)

        owner_id = owner_profile[0]
        owner_username = owner_profile[1]
        owner_full_name = owner_profile[2]
        owner_biography = owner_profile[3]
        owner_profile_pic_url = owner_profile[4]
        owner_profile_pic_url_hd = owner_profile[5]
        owner_external_url = owner_profile[6]
        owner_external_url_linkshimmed = owner_profile[7]
        owner_followed_by = owner_profile[8]
        owner_follow = owner_profile[9]
        owner_last_updated = time.gmtime(owner_profile[10])
        owner_is_private = bool(owner_profile[11])
        owner_is_deleted = bool(owner_profile[12])


        pubtime = strftime("%Y-%m-%d %H:%M", timestamp)

        print("%s : %s posted '%s' at %s" % (pubtime, owner_full_name, caption[0:50], display_url))



def main():
    display_feed(1)


if __name__ == '__main__':
    e = Exporter()
    main()
    e.close()
    