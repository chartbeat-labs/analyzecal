import logging

from google.appengine.api import users
from google.appengine.ext import webapp

from handlers.env import decorator
from handlers.env import service
from handlers.env import template_engine
from utils.gae import get_all_items
from utils.gae import get_cal_name


def _get_calendar_list():
    params = dict()
    return get_all_items(service.calendarList(), params, decorator.http())


class ChooseCalendarHandler(webapp.RequestHandler):
    """
    Allow the user to choose a calendar to analyze.
    """

    @decorator.oauth_required
    def get(self):
        logging.info('Analyzing for: %s', users.get_current_user().nickname())

        items = _get_calendar_list()
        primary = get_cal_name('primary', service, decorator.http())

        data = {
            'title': 'Choose Calendar',
            'page': 'analyze',
            'primary': primary,
            'items': items,
            }
        template = template_engine.get_template('choose_cal.html')
        self.response.out.write(template.render(data))
