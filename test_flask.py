from unittest import TestCase
from app import app
from models import db, User, Post

# please create a testing db 'user_test' to test this application

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserFlaskTestCase(TestCase):
    '''Test routes for Users.'''
    
    def setUp(self):
        '''Clean up existing users'''
        Post.query.delete()
        User.query.delete()
        
        db.session.commit()
        
    def tearDown(self):
        '''Clean up failed transactions'''
        Post.query.delete()
        User.query.delete()
        db.session.rollback()
        
    def test_redirect_to_users(self):
        '''Make sure homepage redirects to user list'''
        with app.test_client() as client:
            resp = client.get('/')
            
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/users")
            
    def test_show_form(self):
        '''Displays correct form'''
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Last Name:', html)
            
    def test_generate_new_user(self):
        '''New user should display new page with its associated info'''
        with app.test_client() as client:
            resp = client.post('/users/new',
                               data={'first_name': 'Test',
                                     'last_name': 'User', 'image_url': ''}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p><b>Test User</b></p>', html)
            self.assertIn('<img src="https://bitsofco.de/content/images/2018/12/broken-1.png"', html)
            
    def test_edit_user(self):
        '''shows edit user form'''
        user = User(first_name="Test", last_name="Edit", image_url="https://www.outbrain.com/techblog/wp-content/uploads/2017/05/road-sign-361513_960_720.jpg")
        db.session.add(user)
        db.session.commit()
        
        with app.test_client() as client:
            
            resp = client.get(f'/users/{user.id}/edit?')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'placeholder="{user.first_name}"', html)
            
        # ####note to future self, test for errors like when an ID isn't in the database
        
        
    def test_show_posts_form(self):
        '''shows new post form'''
        user = User(first_name="Test2", last_name="Edit2", image_url="https://www.outbrain.com/techblog/wp-content/uploads/2017/05/road-sign-361513_960_720.jpg")
        db.session.add(user)
        db.session.commit()
        
        with app.test_client() as client:
            resp = client.get(f'/users/{user.id}/posts/new')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('placeholder="Title Text"', html)

    def test_add_post(self):
        '''New post is added to db and displays on page'''
        user = User(first_name="Test3", last_name="Edit3", image_url="https://www.outbrain.com/techblog/wp-content/uploads/2017/05/road-sign-361513_960_720.jpg")
        db.session.add(user)
        db.session.commit()
        
        
        with app.test_client() as client:
            resp = client.post(f'/users/{user.id}/posts/new', data={
                'title': 'Test Title',
                'content': 'Test Content'
            }, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Test Title</h1>', html)
            
    def test_show_post(self):
        '''Makes sure correct post is shown'''
        user = User(first_name="Test4", last_name="Edit4", image_url="https://www.outbrain.com/techblog/wp-content/uploads/2017/05/road-sign-361513_960_720.jpg")
        db.session.add(user)
        db.session.commit()
        post = Post(title="Title", content="content", user_id=4)
        db.session.add(post)
        db.session.commit()
        
        with app.test_client() as client:
            resp = client.get(f'/posts/{post.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>content</p>', html)