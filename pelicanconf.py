#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Mike Vanbuskirk'
SITENAME = 'sysengcooking'
SITEURL = 'http:/localhost:8000'
SITETITLE = AUTHOR
SITESUBTITLE = 'devops recipes'
SITELOGO = '/images/beach_jpg.jpg'
BROWSER_COLOR = '#333'
PYGMENTS_STYLE = 'github'

ROBOTS = 'index, follow'

PATH = 'content'
THEME = "Flex"
TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'

PLUGIN_PATHS = ['plugins']

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/custom.css': {'path': 'static/custom.css'},
}

CUSTOM_CSS = 'static/custom.css'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Github info
GITHUB_USER = 'codevbus'
GITHUB_SKIP_FORK = True
GITHUB_REPO_COUNT = 2

USE_FOLDER_AS_CATEGORY = False
MAIN_MENU = False
HOME_HIDE_TAGS = True
DISABLE_URL_HASH = True

# Blogroll
LINKS = (('Archives', '/archives.html'),
         ('Categories', '/categories.html'),
         ('Tags', '/tags.html'))

# Social widget
SOCIAL = (('linkedin', 'https://www.linkedin.com/in/mikevanbuskirk/'),
          ('github', 'https://github.com/codevbus'))

COPYRIGHT_YEAR = 2018

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

ARTICLE_URL = 'blog/{slug}/'
ARTICLE_SAVE_AS = 'blog/{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
TAG_URL = 'tags/{slug}/'
TAG_SAVE_AS = 'tags/{slug}/index.html'
TAGS_URL = 'tags.html'
