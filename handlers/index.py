from google.appengine.ext import webapp

from handlers.env import decorator
from handlers.env import template_engine


class IndexHandler(webapp.RequestHandler):
    @decorator.oauth_aware
    def get(self):
        data = {
            'url': decorator.authorize_url(),
            'has_credentials': decorator.has_credentials(),
            'title': 'Welcome',
            'page': 'home',
            }
        template = template_engine.get_template('grant.html')
        self.response.out.write(template.render(data))
