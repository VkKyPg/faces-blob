from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.images import get_serving_url
import webapp2
import jinja2
import os
import logging

class Person(ndb.Model):
    name_person = ndb.StringProperty(required= True)
    image = ndb.BlobKeyProperty()
    paragraph = ndb.StringProperty(required = False)
    category_id = ndb.StringProperty(required = False)

class Category(ndb.Model):
    category_Name = ndb.StringProperty(required=True)
    people = ndb.StructuredProperty(Person, repeated = True, required = False)
    user_id = ndb.StringProperty(required = True)

class User(ndb.Model):
    name_id = ndb.StringProperty(required=True)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            name_id = user.user_id()
            user = User(name_id = name_id)
            user.put()
            self.redirect('/about')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user_id = users.get_current_user().user_id()
        user_logout= users.create_logout_url ('/')
        category_data = Category.query().fetch()
        category_keys =[]
        for category in category_data:
            category_keys.append(category.key.id())
        template_vars = {'user_id': user_id, 'categories': category_data, "category_keys": category_keys, "user_logout" : user_logout}
        template = jinja2_environment.get_template('templates/index.html')
        self.response.write(template.render(template_vars))

class AddCategoryHandler(webapp2.RequestHandler):
    def post(self):
        category_Name = self.request.get('category_Name')
        user_id = users.get_current_user().user_id()
        category = Category(category_Name = category_Name, user_id = user_id )
        category.put()
        self.redirect('/home')

class AddPersonHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/add_person_photo')
        category_id = self.request.get('category_id')
        user_logout= users.create_logout_url ('/')
        person_data = Person.query().fetch()
        template_vars = {'upload_url': upload_url, 'category_id': category_id, 'people': person_data, 'user_logout' : user_logout}
        template = jinja2_environment.get_template('templates/category.html')
        self.response.write(template.render(template_vars))

class AddPersonPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        name_person = self.request.get('name_person')
        paragraph = self.request.get('paragraph')
        category_id = self.request.get('category_id')
        person = Person(name_person = name_person, image = upload.key(), paragraph = paragraph, category_id = category_id )
        person.put()
        self.redirect('/add_person?category_id=' + category_id)

class DeleteCategoryHandler(webapp2.RequestHandler):
    def post(self):
        id_category = self.request.get('keyid')
        k = ndb.Key(Category, int(id_category))
        k.delete()
        self.redirect('/home')

class DeletePersonHandler(webapp2.RequestHandler):
    def post(self):
        id_people = self.request.get('ppl_id')
        k = ndb.Key(Person, int(id_people))
        k.delete()
        self.redirect('/add_person')

class TutorialHandler(webapp2.RequestHandler):
    def get(self):
        user_id = users.get_current_user().user_id()
        user_logout= users.create_logout_url ('/')
        template_vars = {'user_logout' : user_logout}
        template = jinja2_environment.get_template('templates/tutorial.html')
        self.response.write(template.render(template_vars))

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', LoginHandler),
    ('/home', MainHandler),
    ('/add_category', AddCategoryHandler),
    ('/add_person', AddPersonHandler),
    ('/add_person_photo', AddPersonPhotoHandler),
    ('/delete_category', DeleteCategoryHandler),
    ('/delete_person', DeletePersonHandler),
    ('/about', TutorialHandler),
    ('/view_photo/([^/]+)?', ViewPhotoHandler),
], debug=True)
