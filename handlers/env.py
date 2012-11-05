import logging
import os

from apiclient.discovery import build
from google.appengine.api import memcache

import httplib2
import jinja2
from oauth2client.appengine import oauth2decorator_from_clientsecrets

IS_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')
"""Are we running in a Dev environment?"""

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),
                              '../client_secrets{0}.json'.format('_dev' if IS_DEV else ''))

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS

SCOPE = 'https://www.googleapis.com/auth/calendar.readonly'
"""OAuth scope"""

logging.info("OAuth scope: {0}".format(SCOPE))
http = httplib2.Http(memcache)
service = build("calendar", "v3", http=http)
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope=SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

template_dir = os.path.join(os.path.dirname(__file__), '../templates/')
logging.info('Loading templates from: {0}'.format(template_dir))
template_engine = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
