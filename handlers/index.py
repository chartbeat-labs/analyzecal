from google.appengine.api import users
from google.appengine.ext import webapp

from handlers.env import template_engine


class IndexHandler(webapp.RequestHandler):
    """
    Index/welcome page for the application.
    """

    def get(self):
        data = {
            'title': 'Welcome',
            'page': 'home',
            'logout_url': users.create_logout_url('/'),
            }
        template = template_engine.get_template('index.html')
        self.response.out.write(template.render(data))
