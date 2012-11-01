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


from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
import json
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

from utils import num_working_days
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

NUM_WEEKS = 4
"""Number of weeks to look back"""

WORK_DAY_START = 9
"""Start of the work day"""

WORK_DAY_END = 19
"""End of the work day"""

WEEKDAY_TO_STR = OrderedDict([
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    ])
"""Lookup of weekday num -> day"""

CAL_ID = 'primary'


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
        data = {
            'url': decorator.authorize_url(),
            'has_credentials': decorator.has_credentials(),
            'title': 'Welcome',
            'page': 'home',
            }
        template = jinja_environment.get_template('grant.html')
        self.response.out.write(template.render(data))


def _get_events(cal_id, time_min, time_max):
    """
    Retrieve events from the Google API

    @param cal_id: str, calendar id
    @param time_min: datetime, from time
    @param time_max: datetime, to time
    @return: list(events)
    """

    http = decorator.http()
    events = []
    endpoint = service.events()
    request = endpoint.list(
        calendarId=cal_id,
        singleEvents=True,
        timeMin=time_min.isoformat('T') + 'Z',
        timeMax=time_max.isoformat('T') + 'Z',
        )
    while request is not None:
        response = request.execute(http=http)
        events.extend(response.get('items', []))
        request = endpoint.list_next(request, response)

    return events


def _get_cal_name(cal_id):
    """
    Retrieve the name (summary) for a calendar.

    @param cal_id: str, calendar id
    @return: str, calendar name
    """

    http = decorator.http()
    response = service.calendars().get(calendarId=cal_id).execute(http=http)
    logging.warning(response)
    return response['summary']


def _generate_stats(time_min, time_max, events):
    """
    Generate stats from a list of events.

    @param events: list(events), events to analyze
    @param time_min: datetime, from time
    @param time_max: datetime, to time
    @return: list(events)
    """

    num_events = 0
    event_days = defaultdict(lambda: 0)
    attendees = 0
    total_duration_in_secs = 0
    for event in events:
        _ac = event['_ac'] = {}
        if 'dateTime' not in event['start']:
            # All-day events
            continue

        # TODO: Sort out declined and tentative events, if not
        # event.organizer.self, find self in event.attendees
        # list(dict)), 'email' = self and 'responseStatus' =
        # 'accepted'
        start = str_to_datetime(event['start']['dateTime'])
        end = str_to_datetime(event['end']['dateTime'])

        _ac['duration'] = end - start

        if event['summary'] == 'Lunch':
            # Don't count lunches as events
            continue
        if end.hour < WORK_DAY_START or start.hour > WORK_DAY_END:
            # TODO: will miss multi-day events
            continue
        if start.weekday() > 4 or end.weekday() > 4:
            # TODO: will exclude events ending or starting in
            # weekends, but stretching into the week
            continue

        _ac['included'] = True
        total_duration_in_secs += _ac['duration'].total_seconds()
        event_days[start.weekday()] += 1
        num_events += 1
        # if list not present, Default to 1 attendant (self)
        attendees += len(event.get('attendees', ['1']))

    # Calculate stats
    stats = {}
    stats['events'] = num_events
    stats['event_days'] = OrderedDict((v, event_days[k]) for (k, v) in WEEKDAY_TO_STR.iteritems())
    stats['total_hours'] = total_duration_in_secs / 60 / 60
    stats['working_days'] = num_working_days(time_min, time_max)
    stats['working_hours'] = (WORK_DAY_END - WORK_DAY_START) * stats['working_days']
    stats['percent_events'] = (stats['total_hours'] / stats['working_hours']) * 100
    stats['avg_attendees'] = attendees / stats['events']
    stats['avg_events_day'] = stats['events'] / stats['working_days']
    stats['events_excluded'] = len(events) - stats['events']

    return stats


class AnalyzeHandler(webapp.RequestHandler):
    @decorator.oauth_required
    def get(self):
        logging.info('Analyzing for: %s', users.get_current_user().nickname())

        time_min = datetime.utcnow() - timedelta(weeks=NUM_WEEKS)
        time_max = datetime.utcnow()

        try:
            events = _get_events(CAL_ID, time_min, time_max)
        except AccessTokenRefreshError:
            return self.redirect('/')
        cal_name = _get_cal_name(CAL_ID)

        stats = _generate_stats(time_min, time_max, events)

        data = {
            'events': events,
            'stats': stats,
            'stats_json': json.dumps(stats),
            'cal_name': cal_name,
            'pformat': pformat,
            'title': cal_name,
            'page': 'analyze',
            'js': 'analyze',
            'css': 'analyze',
            }
        template = jinja_environment.get_template('analyze.html')
        self.response.out.write(template.render(data))


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
