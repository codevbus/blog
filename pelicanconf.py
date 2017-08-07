#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = 'Mike Vanbuskirk'
SITENAME = 'sysengcooking'
SITEURL = 'http://localhost:8000'

PATH = 'content'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'

THEME = os.path.join(os.environ.get('HOME'),'build/pelican-themes/pelican-bootstrap3')
BOOTSTRAP_THEME = 'sandstone'
BANNER = 'images/banner.jpg'
BANNER_SUBTITLE = 'devops recipes'

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_TAGS_ON_SIDEBAR = True


PLUGIN_PATHS = [os.path.join(os.environ.get('HOME'),'build/pelican-plugins')]
PLUGINS = ['i18n_subsites', ]
JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

CUSTOM_CSS = 'static/custom.css'

STATIC_PATHS = ['images', 'extra/custom.css']

# Tell Pelican to change the path to 'static/custom.css' in the output dir
EXTRA_PATH_METADATA = {
    'extra/custom.css': {'path': 'static/custom.css'}
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

GITHUB_USER = 'codevbus'
GITHUB_SKIP_FORK = True
GITHUB_REPO_COUNT = 2

# Blogroll
LINKS = None

# Social widget
SOCIAL = (('linkedin', 'https://www.linkedin.com/in/mikevanbuskirk/'),
          ('github', 'https://github.com/codevbus'),
          ('quora', 'https://quora.com/profile/Mike-Vanbuskirk'))

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

ARTICLE_URL = 'blog/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{slug}.html'
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'
TAG_URL = 'tags/{slug}.html'
TAG_SAVE_AS = 'tags/{slug}.html'
TAGS_URL = 'tags.html'
