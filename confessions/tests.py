import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UsersConfessions
from django.utils import timezone
from django.urls import reverse
import os

def create_test_user():
    """
    Creates a test user
    """
    user = User.objects.create_user(username="testuser",password="testpass")
    user.save()
    return user

#Create your tests here.
class UserConfessionsModelTests(TestCase):
    def test_create_confession(self):
        test_user = create_test_user()
        test_confession = UsersConfessions.objects.create(user=test_user,content="Test content",created_at=timezone.now())
        test_confession.save()
        self.assertEqual(test_confession.content,UsersConfessions.objects.filter(user=test_user).first().content)
        self.assertEqual(test_confession.created_at,UsersConfessions.objects.filter(user=test_user).first().created_at)

class UserConfessionsRegisterUserTests(TestCase):
    def test_register_user_get(self):
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
    
    def test_register_user_post(self):
        """
        For a post request with body it should create a user
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"testpass",
            "email":"test@email.com"
        })
        
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,"/confessions/login/")
        self.assertTrue(User.objects.filter(username="testuser").exists())
   
    def test_register_user_empty_username_post(self):
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

    def test_register_user_empty_password_post(self):
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

    def test_register_user_empty_username_and_password_post(self):
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
    
    def test_register_user_invalid_username_post(self):
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
    
    def test_register_user_invalid_email_post(self):
        """
        For a post request with invalid email it should return 422
        """
        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"123",
            "email":"test"
        })
        self.assertEqual(response.status_code,422)

    def test_register_dupilicate_user_post(self):
        """
        For a post request with body for a dupilicate username it should return 200 with Server Side Rendered HTML with error message
        """
        current_user = create_test_user()

        response =self.client.post(reverse("confessions:register_user"),{
            "username":"testuser",
            "password":"anothertestpass",
            "email":"anothertest@email.com"
        })
        
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,'<div class="widget">')
        self.assertContains(response,'<div class="login-link">')
        self.assertContains(response,"User already exists")
        self.assertEqual(response.status_code,200)

# class UserConfessionsLoginUserTests(TestCase):
#     def test_login_user_get(self):
#         """
#         For a get request the page should display a HTML with status_code 200
#         """

#         with open("./templates/confessions/login.html", encoding="utf-8") as f:
#             expected_html = f.read()
    
#         response = self.client.get(reverse("confessions:login_user"))
#         self.assertContains(response,'<div class="page-wrapper">')
#         self.assertContains(response,'<div class="widget">')
#         self.assertContains(response,'<div class="signup-link">')
#         self.assertEqual(response.status_code,200)
    
#     def test_login_user_post(self):
#         """
#         For a post request with body it should login a user
#         """
#         test_user = create_test_user()
#         response = self.client.post(reverse("confessions:login_user"),{
#             "username":"testuser",
#             "password":"testpass",
#         })
        
#         self.assertEqual(response.status_code,302)
#         self.assertRedirects(response,"/confessions/")
#         self.assertTrue("_auth_user_id" in self.client.session)
   
#     def test_login_user_empty_username_post(self):
#         """
#         For a post request with empty username it should return 422
#         """
#         response =self.client.post(reverse("confessions:login_user"),{
#             "username":"",
#             "password":"testpass",
#         })
#         self.assertEqual(response.status_code,422)

#     def test_login_user_empty_password_post(self):
#         """
#         For a post request with empty password it should return 422
#         """
#         response =self.client.post(reverse("confessions:login_user"),{
#             "username":"testuser",
#             "password":"",
#         })
#         self.assertEqual(response.status_code,422)

#     def test_login_user_empty_username_and_password_post(self):
#         """
#         For a post request with empty password and username it should return 422
#         """
#         response =self.client.post(reverse("confessions:login_user"),{
#             "username":"",
#             "password":"",
#         })
#         self.assertEqual(response.status_code,422)
    
#     def test_login_user_invalid_username_post(self):
#         """
#         For a post request with invalid username it should return 422
#         """
#         response =self.client.post(reverse("confessions:login_user"),{
#             "username":1,
#             "password":"123",

#         })
#         self.assertEqual(response.status_code,422)
    
#     def test_login_user_wrong_username_post(self):
#         """
#         For a post request with wrong username should return 401
#         """

#         test_user = create_test_user()
#         response = self.client.post(reverse("confessions:login_user"),{"username":"wrongusername","password":"testpass"})

#         self.assertEqual(response.status_code,401)

#     def test_login_user_wrong_password_post(self):
#         """
#         For a post request with wrong password should return 401
#         """

#         test_user = create_test_user()
#         response = self.client.post(reverse("confessions:login_user"),{"username":"testuser","password":"wrongpassword"})

#         self.assertEqual(response.status_code,401)