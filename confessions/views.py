import json
import re

#decorators
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt

#shortcuts
from django.shortcuts import render,redirect,get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import F,Q

#functions
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

#response
from django.http import JsonResponse

#models and Schemas
from django.contrib.auth.models import User
from .schema import UserRegister,UserLogin
from pydantic import ValidationError
from .models import UsersConfessions,Warnings,BlacklistedUsers

#utility
from .utils import register_user_validator,post_confession_validator

# Create your views here.

@require_http_methods(["GET","POST"] )
def register_user(request):

    if request.method == "GET":
        return render(request,"confessions/register.html")
    
    try:
        #Validation for user_data
        user_data = UserRegister(username=request.POST.get("username"),
                                 password=request.POST.get("password"),
                                 email=request.POST.get("email"))
    
        error_message = register_user_validator(request=request,username=user_data.username,email=user_data.email,password=user_data.password,userdb=User,blacklist_db=BlacklistedUsers)
        
        if not error_message:
            #Create user if no errors were found
            new_User = User.objects.create_user(username=user_data.username,password=user_data.password,email=user_data.email)
            Warnings.objects.create(user=new_User) 
        else:
            return render(request,"confessions/register.html",{"error":error_message})
        
        #Redirect to login if user successfully created
        return redirect(reverse("confessions:login_user"))
    
    except ValidationError as e:
        return JsonResponse({"error":e.errors()},status=422) 
    
@require_http_methods(["GET","POST"])
def login_user(request):
    if request.method == "GET":
        return render(request,"confessions/login.html")
    try:
        creds = UserLogin(username=request.POST.get("username"),password=request.POST.get("password"))
        
        user = authenticate(username=creds.username,password=creds.password)
        if user is not None:
            login(request,user)
            return redirect(reverse("confessions:homepage"))
        else:
            return render(request,"confessions/login.html",{"error":"Invalid Username or Password"})
        
    except ValidationError as e:
        return JsonResponse({"errors":e.errors()},status=422)

@require_http_methods(["GET","POST"])
def logout_user(request):
    logout(request)
    return redirect(reverse("confessions:login_user"))

@require_GET
@login_required(login_url="/confessions/login/")
def get_confessions(request):

    #Check for user's guidelines violation count 
    if Warnings.objects.get(user=request.user).warning_count == 10:
            UsersConfessions.objects.filter(user=request.user).delete()
            Warnings.objects.filter(user=request.user).delete()
            blacklisted_user = User.objects.get(id=request.user.id)
            BlacklistedUsers.objects.create(email=blacklisted_user.email,username=blacklisted_user.username)
            User.objects.filter(id=request.user.id).delete()
            return redirect(reverse("confessions:logout_user"))
    
    error_message = request.GET.get("error")
    if error_message:
        # store temporarily in session or use Django messages
        request.session['tmp_error'] = error_message
        return redirect('/confessions/')  # remove query param
    
    user_posts = UsersConfessions.objects.filter(user=request.user).order_by("-created_at")
    others_posts = UsersConfessions.objects.exclude(user=request.user).order_by("-created_at")

    tmp_error = request.session.pop('tmp_error', None)
    if tmp_error:
        return render(request,"confessions/home.html",{"confessions":user_posts,"others_confessions":others_posts,"error":tmp_error})
    return render(request,"confessions/home.html",{"confessions":user_posts,"others_confessions":others_posts})

@require_POST
@login_required
def post_confession(request):
    content = request.POST.get("content")
    if not content:
        return JsonResponse({"error":"Content is required"},status=422)
    
    content = content.strip()
    error_message = post_confession_validator(request,content,Warnings,UsersConfessions)
    if error_message:
        return redirect(f"{reverse('confessions:homepage')}?error={error_message}")
    
    UsersConfessions.objects.create(content=content,user=request.user,created_at=timezone.now())
    return redirect(reverse("confessions:homepage"))

@require_GET
@login_required
def get_confession(request,id:int):
    confession = get_object_or_404(UsersConfessions,id=id)
    if request.user == confession.user:
        confession_dict = model_to_dict(confession)
        return JsonResponse({"confession":confession_dict},status=200)
    
    return JsonResponse({"error":"unauthorized action"},status=403)

@require_http_methods(["PUT"])
@login_required
def put_confession(request,id:int):
    newContent = json.loads(request.body)["content"]
    confession = get_object_or_404(UsersConfessions,id=id)
    if request.user == confession.user:
        confession.content = newContent
        confession.save()
        return JsonResponse({"updated":True})
    return JsonResponse({"updated":False},status=403)


@require_http_methods(["DELETE"])
@login_required
def delete_confession(request,id:int):
    confession = get_object_or_404(UsersConfessions,id=id)
    if request.user == confession.user:
        confession.delete()
        return JsonResponse({"deleted":True},status=204)
    else:
        return JsonResponse({"deleted":False},status=403)
    
    
    