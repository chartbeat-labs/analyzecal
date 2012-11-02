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


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from handlers.analyze import AnalyzeHandler
from handlers.env import decorator
from handlers.index import IndexHandler


def main():
    application = webapp.WSGIApplication(
    [
        ('/', IndexHandler),
        ('/analyze', AnalyzeHandler),
        (decorator.callback_path, decorator.callback_handler()),
    ],
    debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
