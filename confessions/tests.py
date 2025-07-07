import html
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UsersConfessions,Warnings,BlacklistedUsers
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
import os

def create_test_user():
    """
    Creates a test user
    """
    user = User.objects.create_user(username="testuser",password="@Testpass123",email="testuser@email.com")
    user.save()
    Warnings.objects.create(user=user)
    return user

def create_test_user_2():
    """
    creates a another test user
    """
    user = User.objects.create_user(username="testuser2",password="@Testpass123",email="testuser2@email.com")
    user.save()
    Warnings.objects.create(user=user)
    return user

def create_test_user_1_with_data():
    """
    creates a test user and posts data 
    """
    test_user = create_test_user()
    content="User 1 Content , which is in the valid form of the api's guidelines. Extra Content to be safe from violation."
    UsersConfessions.objects.create(content=content,created_at=timezone.now(),user=test_user)
    return {"user":test_user,"content":content}

def create_test_user_2_with_data():
    """
    creates a test user 2 and posts data 
    """
    test_user = create_test_user_2()
    content="User 2 Content , which is in the valid form of the api's guidelines. Extra Content to be safe from violation."
    UsersConfessions.objects.create(content=content,created_at=timezone.now(),user=test_user)
    return {"user":test_user,"content":content}

def create_blacklisted_user():
    """
    creates a blacklist user in BlacklistedUsers table
    """
    BlacklistedUsers.objects.create(username="testuser",email="testuser@email.com")

def create_about_to_be_blacklisted_user():
    """
    creates a about to be black listed user
    """
    test_user = create_test_user()
    warning_obj = Warnings.objects.get(user=test_user)
    warning_obj.warning_count = 9
    warning_obj.save()
    return test_user

#Create your tests here.
class UserConfessionsModelTests(TestCase):
    def test_create_confession(self):
        test_user = create_test_user()
        test_confession = UsersConfessions.objects.create(user=test_user,content="Test content",created_at=timezone.now())
        test_confession.save()
        self.assertEqual(test_confession.content,UsersConfessions.objects.filter(user=test_user).first().content)
        self.assertEqual(test_confession.created_at,UsersConfessions.objects.filter(user=test_user).first().created_at)

class RegisterUserViewTests(TestCase):
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
            "email":"testuser@email.com"
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
            "email":"testuser@email.com"
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
            "email":"testuser@email.com"
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
            "email":"testuser@email.com"
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
            "email":"testuser@email.com"
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
            "email":"testuser@email.com"
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

class LoginUserViewTests(TestCase):
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

class LogoutUserViewTests(TestCase):
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

class GetConfessionsViewTests(TestCase):
    def test_get_confession_no_login(self):
        """
        For Unauthenticated get request return 302
        """
        response = self.client.get(reverse("confessions:homepage"))
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse("confessions:login_user")+"?next=/confessions/")

    def test_get_confessions_violation(self):
        """
        For a post request followed by redirect (get request) with violation true should return 200 with deletion of user from database and cascade delete all of his resources
        """
        #logging in 
        about_to_be_blacklisted_user = create_about_to_be_blacklisted_user()
        response = self.client.post(reverse("confessions:login_user"),{"username":about_to_be_blacklisted_user.username,"password":"@Testpass123"})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse("confessions:homepage"))
        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertEqual(Warnings.objects.filter(user=about_to_be_blacklisted_user).first().warning_count,9)

        #post content with tag to simulate violation
        violated_content = "<script>alert(1)</script>"
        response = self.client.post(reverse("confessions:post_confession"),{"content":violated_content},follow=True)
        print(response)
        self.assertEqual(response.status_code,200)
        self.assertTrue(not Warnings.objects.filter(user=about_to_be_blacklisted_user).exists())
        self.assertTrue(not UsersConfessions.objects.filter(user=about_to_be_blacklisted_user).exists())
        self.assertTrue(BlacklistedUsers.objects.filter(Q(username=about_to_be_blacklisted_user.username) | Q(email=about_to_be_blacklisted_user.email)).exists())
        self.assertTrue("_auth_user_id" not in self.client.session)
        
    def test_get_confessions_no_users_data(self):
        """
        For a get request following a new user logging in the dashboard should be empty
        """    
        test_user = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        },follow=True)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,"Your diary is empty.")
        self.assertContains(response,"No Confessions From Others Yet")

    def test_get_confessions_only_user_data(self):
        """
        For a get request following a successfull post creation should return 200 and Server Side Rendered User data on the dashboard
        """
        test_user_with_data = create_test_user_1_with_data()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        },follow=True)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,html.escape(test_user_with_data["content"]))
        self.assertContains(response,"No Confessions From Others Yet")
    
    def test_get_confessions_only_other_users_data(self):
        """
        For a get request following a login with no data but other users data should return 200 and Server Side Rendered Other Users Data on dashboard
        """
        test_user_2_with_data = create_test_user_2_with_data()
        test_user_1 = create_test_user()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        },follow=True)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,html.escape(test_user_2_with_data["content"]))
        self.assertContains(response,"Your diary is empty.")
    
    def test_get_confessions_all_users_data(self):
        """
        For a get request following a successfull post creation should return 200 and Server Side Rendered User data on the dashboard
        """
        test_user_2_with_data = create_test_user_2_with_data()
        test_user_1_with_data = create_test_user_1_with_data()
        response = self.client.post(reverse("confessions:login_user"),{
            "username":"testuser",
            "password":"@Testpass123",
        },follow=True)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'<div class="page-wrapper">')
        self.assertContains(response,html.escape(test_user_2_with_data["content"]))
        self.assertContains(response,html.escape(test_user_1_with_data["content"]))