import re
from django.db import models
from django.db.models import Q,F
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

def strip_tags(value):
    return re.sub(r'<[^>]*?>', '', value)

def register_user_validator(request:HttpRequest,username:str,email:str,password:str,userdb:models.Model,blacklist_db:models.Model) -> str:
    
    if(username != "" and password != ""):

        #Check for blacklisted users
        if blacklist_db.objects.filter(Q(username=username) | Q(email=email)).exists():
            return "Username or email belongs to a blacklist"
        
        #Check for already existing User
        if userdb.objects.filter(username=username).exists():
           return "User already exists"

        #Check For Invalid Username
        username_pattern = re.compile(r'^[a-zA-Z](?:(?![_.]{2})[a-zA-Z0-9._]){7,29}$')
        if not username_pattern.match(username):
            return "Username must start with a letter, be 8-30 chars, contain only letters, numbers, . or _, and no consecutive . or _"
        
        #Check for weak password
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$')
        if not password_pattern.match(password):
            return "Password must be at least 8 characters long, include uppercase, lowercase, digit, and special character."
        
        return ""
    
    else:
       return "username and password cannot be empty"

def post_confession_validator(request:HttpRequest,content:str,warning_db:models.Model,confessions_db:models.Model) -> str:
    
    #Spam protection
    last_confession = confessions_db.objects.filter(user=request.user).order_by('-created_at').first()
    if last_confession and timezone.now() - last_confession.created_at < timedelta(seconds=10):
        warning_object = warning_db.objects.get(user=request.user)
        warning_object.warning_count = F("warning_count") + 1
        warning_object.save()
        return f"Warning: Please DO NOT spam posts, wait for atleast 10 seconds till you post a next content, warnings left until BAN: {10 - warning_db.objects.get(user=request.user).warning_count}"
    
    #Check for no data
    if content.strip() == "":
        return "Error: Content cannot be empty or it cannot only contain whitespaces."

    #Check for HTML tags in the content
    clean_content = strip_tags(content)
    if content != clean_content:
        if warning_db.objects.get(user=request.user).warning_count <= 9:
            warning_object = warning_db.objects.get(user=request.user)
            warning_object.warning_count = F("warning_count") + 1
            warning_object.save()
            return f"Warning: DO NOT use HTML tags while creating a post, you have {10 - warning_db.objects.get(user=request.user).warning_count} left ,then you are BANNED from the community."
        
    #Check for minimum and maximum content length
    if len(content)<25 or len(content)>150:
       return "Error: Length of content should be a minimum of 25 character and can be maximum of 150 characters."
    else:
        #Check for same content
        if confessions_db.objects.filter(user=request.user,content=content).exists():
            return "Error: The post already exists"

    return ""
