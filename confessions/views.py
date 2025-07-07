import json
import re
#decorators
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt

#shortcuts
from django.shortcuts import render,redirect,get_object_or_404
from django.forms.models import model_to_dict

#functions
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone

#response
from django.http import JsonResponse

#models and Schemas
from django.contrib.auth.models import User
from .schema import UserRegister,UserLogin
from pydantic import ValidationError
from .models import UsersConfessions

# Create your views here.

@require_http_methods(["GET","POST"])
def register_user(request):

    if request.method == "GET":
        return render(request,"confessions/register.html")
    
    try:
        #Validation for user_data
        user_data = UserRegister(username=request.POST.get("username"),
                                 password=request.POST.get("password"),
                                 email=request.POST.get("email"))
        
        #Check for empty password and username
        if(user_data.username != "" and user_data.password != ""):

            #Check For Invalid Username
            username_pattern = re.compile(r'^[a-zA-Z](?:(?![_.]{2})[a-zA-Z0-9._]){7,29}$')
            if not username_pattern.match(user_data.username):
                return render(request,"confessions/register.html",{"error":"Username must start with a letter, be 8-30 chars, contain only letters, numbers, . or _, and no consecutive . or _"})
            
            #Check for weak password
            password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$')
            if not password_pattern.match(user_data.password):
                return render(request, "confessions/register.html", {"error": "Password must be at least 8 characters long, include uppercase, lowercase, digit, and special character."})
            
            #Check for already existing User
            if User.objects.filter(username=user_data.username).exists():
                return render(request,"confessions/register.html",{"error":"User already exists"})
            
            #Create user if no errors were found
            User.objects.create_user(username=user_data.username,password=user_data.password,email=user_data.email)

        else:
            return render(request,"confessions/register.html",{"error":"username and password cannot be empty"})

        #Redirect to login if user successfully created
        return redirect("/confessions/login/")
    
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
            return redirect("/confessions/")
        else:
            return render(request,"confessions/login.html",{"error":"Invalid Username or Password"})
        
    except ValidationError as e:
        return JsonResponse({"errors":e.errors()},status=422)


# @csrf_exempt
@require_POST
def logout_user(request):
    logout(request)
    return redirect("/confessions/login/")

@require_GET
@login_required(login_url="/confessions/login/")
def get_confessions(request):
    user_posts = UsersConfessions.objects.filter(user=request.user).order_by("-created_at")
    others_posts = UsersConfessions.objects.exclude(user=request.user).order_by("-created_at")
    return render(request,"confessions/home.html",{"confessions":user_posts,"others_confessions":others_posts})

@require_POST
@login_required
def post_confession(request):
    content = request.POST.get("content")
    if not content:
        return JsonResponse({"error":"Content is required"},status=422)
    UsersConfessions.objects.create(content=content,user=request.user,created_at=timezone.now())
    return redirect("/confessions/")

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
    
    
    