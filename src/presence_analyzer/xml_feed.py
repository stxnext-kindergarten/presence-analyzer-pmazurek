# -*- coding: utf-8 -*-
"""Script to load XML from feed"""
# pylint:skip-file

import os
import urllib
from functools import partial

etc = partial(os.path.join, 'parts', 'etc')

DEPLOY_CFG = etc('deploy.cfg')

DEBUG_CFG = etc('debug.cfg')

_buildout_path = __file__
for i in range(2 + __name__.count('.')):
    _buildout_path = os.path.dirname(_buildout_path)

abspath = partial(os.path.join, _buildout_path)
del _buildout_path


def run(debug=False):
    """
    Retrieves user data from xml feed and saves it to file.
    """
    if debug:
        config = DEBUG_CFG
    else:
        config = DEPLOY_CFG

    from presence_analyzer import app
    app.config.from_pyfile(abspath(config))

    xmlfile = urllib.urlopen(app.config['XML_FEED'])
    content = xmlfile.read()
    filename = app.config['DATA_XML']

    with open(filename, 'w') as target_file:
        target_file.write(content)
