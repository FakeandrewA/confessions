import json

from django.utils import timezone
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

from django.http import JsonResponse

from .schema import UserRegister,UserLogin
from pydantic import ValidationError

from .models import UsersConfessions
# Create your views here.

@require_http_methods(["GET","POST"])
def register_user(request):

    if request.method == "GET":
        return render(request,"confessions/register.html")
    
    try:
        user_data = UserRegister(username=request.POST.get("username"),
                                 password=request.POST.get("password"),
                                 email=request.POST.get("email"))
        if(user_data.username != "" and user_data.password != ""):
            if user_data.username.isdigit():
                return JsonResponse({"error": "Username cannot be purely numeric"}, status=422)
             
            user = User.objects.create_user(username=user_data.username,password=user_data.password,email=user_data.email)
        else:
            return JsonResponse({"error":"Username or Password cannot be empty"},status=422)
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
            return JsonResponse({"error":"Invalid Username or Password"},status=401)
    except ValidationError as e:
        return JsonResponse({"errors":e.errors()},status=422)

@csrf_exempt
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
    return HttpResponse("got a confession")

@require_http_methods(["PUT"])
@login_required
def put_confession(request,id:int):
    return HttpResponse("updated a confession")


@require_http_methods(["DELETE"])
@login_required
@csrf_exempt
def delete_confession(request,id:int):
    confession = get_object_or_404(UsersConfessions,id=id)
    confession.delete()
    return JsonResponse({"deleted":True})