
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UsersConfessions,Warnings,BlacklistedUsers
from django.utils import timezone
from django.urls import reverse
import os

def create_blacklisted_user():
    """
    creates a blacklist user in BlacklistedUsers table
    """
    BlacklistedUsers.objects.create(username="testuser",email="testuser@email.com")

def create_test_user():
    """
    Creates a test user
    """
    user = User.objects.create_user(username="testuser",password="@Testpass123")
    user.save()
    Warnings.objects.create(user=user)
    return user

# Create your tests here.
class UserConfessionsModelTests(TestCase):
    def test_create_confession(self):
        test_user = create_test_user()
        test_confession = UsersConfessions.objects.create(user=test_user,content="Test content",created_at=timezone.now())
        test_confession.save()
        self.assertEqual(test_confession.content,UsersConfessions.objects.filter(user=test_user).first().content)
        self.assertEqual(test_confession.created_at,UsersConfessions.objects.filter(user=test_user).first().created_at)

class UserConfessionsRegisterUserTests(TestCase):
    def test_register_user_clientview(self):
        """
        For a get request the page should display a HTML with status_code 200
        """

        with open("./templates/confessions/register.html", encoding="utf-8") as f:
            expected_html = f.read()
    
        response = self.client.get(reverse("confessions:register_user"))
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertEqual(response.status_code,200)
    
    def test_register_user_apiview(self):
        """
        For a post request with body it should create a user
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"@Testpass123",
            "email":"test@email.com"
        })
        
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/login/")
        self.assertTrue(User.objects.filter(username="testuser").exists())
   
    def test_register_user_empty_username(self):
        """
        For a post request with empty username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"",
            "password":"testpass",
            "email":"test@email.com"
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"username and password cannot be empty")
        self.assertEqual(response.status_code,200)

    def test_register_user_empty_password(self):
        """
        For a post request with empty password it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"",
            "email":"test@email.com"
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"username and password cannot be empty")
        self.assertEqual(response.status_code,200)

    def test_register_user_empty_username_and_password(self):
        """
        For a post request with empty password and username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"",
            "password":"",
            "email":"test@email.com"
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"username and password cannot be empty")
        self.assertEqual(response.status_code,200)
    
    def test_register_user_invalid_username(self):
        """
        For a post request with invalid username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":1,
            "password":"123",
            "email":"test@email.com"
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"Username must start with a letter, be 8-30 chars, contain only letters, numbers, . or _, and no consecutive . or _")
        self.assertEqual(response.status_code,200)
    
    def test_register_user_invalid_email(self):
        """
        For a post request with invalid email it should return 422
        """
        response = self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"123",
            "email":"test"
        })
        self.assertEqual(response.status_code,422)

    def test_register_user_dupilicate_user(self):
        """
        For a post request with body for a dupilicate username it should return 200 with Server Side Rendered HTML with error message
        """
        current_user = create_test_user()

        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"@Anothertestpass123",
            "email":"anothertest@email.com"
        })
        
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"User already exists")
        self.assertEqual(response.status_code,200)

    def test_register_user_invalid_password(self):
        """
        For a post request with body for a invalid password it should return 200 with Server Side Rendered HTML with error message
        """

        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"weakpassword",
            "email":"test@email.com"
        })
        
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"Password must be at least 8 characters long, include uppercase, lowercase, digit, and special character.")
        self.assertEqual(response.status_code,200)
    
    def test_register_user_blacklisted_user(self):
        """
        For a post request trying to create a user who is already blacklisted should return 200 with Server Side Rendered HTML with error message
        """
        create_blacklisted_user()
        response = self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"@Testpass123",
            "email":"testuser@email.com"
        })

        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"Username or email belongs to a blacklist")
        self.assertEqual(response.status_code,200)

class UserConfessionsLoginUserTests(TestCase):
    def test_login_user_clientview(self):
        """
        For a get request the page should display a HTML with status_code 200
        """

        with open("./templates/confessions/login.html", encoding="utf-8") as f:
            expected_html = f.read()
    
        response = self.client.get(reverse("confessions:login_user"))
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertEqual(response.status_code,200)
    
    def test_login_user_apiview(self):
        """
        For a post request with body it should login a user
        """
        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        })
        
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/")
        self.assertTrue("_auth_user_id" in self.client.session)
   
    def test_login_user_empty_username(self):
        """
        For a post request with empty username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:login_user"),{
            "username":"",
            "password":"testpass",
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)

    def test_login_user_empty_password(self):
        """
        For a post request with empty password it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"",
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)

    def test_login_user_empty_username_and_password(self):
        """
        For a post request with empty password and username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:login_user"),{
            "username":"",
            "password":"",
        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)
    
    def test_login_user_invalid_username(self):
        """
        For a post request with invalid username it should return 200 with Server Side Rendered HTML with error message
        """
        response =self.client.post(reverse("confessions:login_user"),{
            "username":1,
            "password":"123",

        })
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)
    
    def test_login_user_wrong_username(self):
        """
        For a post request with wrong username should return 200 with Server Side Rendered HTML with error message
        """

        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{"username":"wrongusername","password":"testpass"})

        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)

    def test_login_user_wrong_password(self):
        """
        For a post request with wrong password should return 200 with Server Side Rendered HTML with error message
        """

        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{"username":"testuser","password":"wrongpassword"})

        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="signup-link">')
        self.assertContains(response,"Invalid Username or Password")
        self.assertEqual(response.status_code,200)

class UserConfessionsLogoutUserTests(TestCase):
    def test_logout_get_request(self):
        """
        For a get request with a logged in user , should return 302
        """
        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        })
        ##logged in
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/")
        self.assertTrue("_auth_user_id" in self.client.session)

        
        response = self.client.get(reverse("confessions:logout_user"))
        ##logged out
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/login/")
        self.assertTrue("_auth_user_id" not in self.client.session)
    
    def test_logout_post_request(self):
        """
        For a post request with a logged in user , should return 302
        """
        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        })
        ##logged in
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/")
        self.assertTrue("_auth_user_id" in self.client.session)

        
        response = self.client.post(reverse("confessions:logout_user"))
        ##logged out
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/login/")
        self.assertTrue("_auth_user_id" not in self.client.session)