#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Experimental application for getting appointment statistics out of
your Google Calendar.

Inspired by the Google examples here:
https://developers.google.com/api-client-library/python/platforms/google_app_engine
"""

__author__ = 'allan@chartbeat.com (Allan Beaufour)'


from datetime import datetime
from datetime import timedelta
import logging
import os
from pprint import pformat

from apiclient.discovery import build
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import httplib2
import jinja2
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError

from utils import str_to_datetime


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

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

NUM_WEEKS = 1
"""Number of weeks to look back"""


http = httplib2.Http(memcache)
service = build("calendar", "v3", http=http)
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/calendar.readonly',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainHandler(webapp.RequestHandler):
    @decorator.oauth_aware
    def get(self):
        variables = {
            'url': decorator.authorize_url(),
            'has_credentials': decorator.has_credentials()
            }
        template = jinja_environment.get_template('grant.html')
        self.response.out.write(template.render(variables))


class AnalyzeHandler(webapp.RequestHandler):
    @decorator.oauth_required
    def get(self):
        try:
            logging.info('Analyzing for: %s', users.get_current_user().nickname())
            timeMin = datetime.utcnow() - timedelta(weeks=NUM_WEEKS)
            timeMax = datetime.utcnow()
            http = decorator.http()
            request = service.events().list(
                calendarId='primary',
                singleEvents=True,
                timeMin=timeMin.isoformat('T') + 'Z',
                timeMax = timeMax.isoformat('T') + 'Z',
                # TODO: don't limit results
                maxResults=10,
                )
            response = request.execute(http=http)
            events = response.get('items', [])
            # TODO: only getting the first page. Need to call .next()
            # and iterate

            template = jinja_environment.get_template('analyze.html')
            for event in events:
                end = str_to_datetime(event['end']['dateTime'])
                start = str_to_datetime(event['start']['dateTime'])
                event['duration'] = end - start
                event['as_str'] = pformat(event, indent=2)
            self.response.out.write(template.render({'events': events}))

        except AccessTokenRefreshError:
            self.redirect('/')


def main():
    application = webapp.WSGIApplication(
    [
        ('/', MainHandler),
        ('/analyze', AnalyzeHandler),
        (decorator.callback_path, decorator.callback_handler()),
    ],
    debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
