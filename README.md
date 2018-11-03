# 📷 Pyctogram

![](https://img.shields.io/badge/please-help-yellow.svg)
![](https://img.shields.io/badge/trapped_in-SVG_factory-red.svg)
![](https://img.shields.io/badge/running_out-of_XML-yellow.svg)
![](https://img.shields.io/badge/send-tags-orange.svg)

A scraper & viewer for Instagram, written in Python.

## ❓ What’s the deal?

Due to various gripes I have with [Instagram](https://instagram.com), I am deleting my account. But there are many of my friends who still use it, and I want to keep on looking at their pictures.

This project aims to create a simple way to see my friend’s latest posts on my computer. The code may be adapted to work on some web hosts or cloud solutions, but it’s still pretty much in development so proceed with care.

It’s my first real *coding* project. I’m a webdesigner who dabbles in Python, and I wanted to scratch an itch. I don’t know anything about software architecture and very little about databases. If you have suggestions for better, nicer, cleaner ways of doing things, please open an issue!

## 🏗 How it works

The code is in Python 3.6. It uses Flask, BeautifulSoup, sqlite3.

The scraping can be done regularly (with a `cron`), or called by the user. The script visits the profile pages of the Instagram users listed, and saves the info in the database. The images are not saved on disk at this point. Of course, if an Insatgram profile is hidden, no info can be saved.

A Flask-based web app lets you browse the saved info, as an image feed (much like an Instagram feed, in the right order and without the ads), as a user profile, or as a specific media page. There’s also the possibiltiy to Save (and Forget) some media, in which case the app saves the image on the disk.

## ⚗ How to install it

After cloning the repo, install Python virtualenv and packages:
```bash
$ cd Pyctogram
$ make install
```

When it’s done, initialize the database and run the server:
```bash
$ make init-db
$ make serve
```
And open a browser page to `http://127.0.0.1:5000/`.

## ⚗ How to use it

### Add contacts
You must register to access the account importer.

After registration, you can add accounts to the default feed by importing `connections.json` file from your [Instagram Data Archive](https://help.instagram.com/181231772500920).  
You can also add accounts from a text file or directly on the application.

### Get accounts media
To update accounts media, you can run the following command:
```bash
$ make update-media
```
It updates all accounts regardless of users or lists (recommanded way to update feeds).

You can also update media from the web interface for the fedd or a list (not recommanded yet, if the feed/list has a lot of contacts).

## 🛠 To Do

- ~~🖼 Display the "Sidecar" objects (when there’s many photos in a single post)~~
- ~~👍 Display latest likes and comments on Media view~~ Following changes by Instagram, it won’t work.
- ~~📇 Importing Instagram-exported accounts lists~~
- ⏬ Calling the scraper from the web interface (with a nice Progress Bar component)
- Optimize the scraper performances
- 🎪 Better Bulma Customization
- More emoji
- ~~🖖 Some JS to help with the navigation (*j*, *k*, *l*, like on Flickr)~~
- ~~🌊 DRY the templates~~
- 🚚 Easy Install, esp. on web hosts
- ~~📄 Lists ! Like Twitter lists,~~ with the possibility to call for a scrape for a specific list
- 📔 Albums
- 📲 Webapp-ify (keep the app on a server, but allow the webapp to download the saved pictures on the phone, to keep a feed of saved photos offline)
- ~~🙈 “Hide from feed” if you want a contact to appear in lists, but not in your main feed~~
- Configuration for "production" environnements

## 📃 Copyrights and License

The Instagram copyrights and brand belong to Facebook, Inc.

Unless otherwise specified, this code is copyright 2018 Joachim Robert and released under the GNU Affero General Public License v3.0. Learn more about this license : https://choosealicense.com/licenses/agpl-3.0/

This work uses code from:
- [Bulma](https://github.com/jgthms/bulma), which is copyright 2018 Jeremy Thomas and whose code is released under [the MIT license](https://github.com/jgthms/bulma/blob/master/LICENSE).
- [Slider](https://github.com/cferdinandi/slider), whose code is released under [the MIT license](https://github.com/jgthms/bulma/blob/master/LICENSE)
