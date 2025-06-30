import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET,require_POST,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

from django.http import JsonResponse

from .schema import UserRegister,UserLogin
from pydantic import ValidationError

# Create your views here.

@csrf_exempt
@require_POST
def register_user(request):
    data = json.loads(request.body)
    try:
        user_data = UserRegister(**data)
        if(user_data.username != "" and user_data.password != ""):
            user = User.objects.create_user(username=user_data.username,password=user_data.password,email=user_data.email)
        else:
            return JsonResponse({"error":"Username or Password cannot be empty"},status=422)
        
        return HttpResponse("User Created!")
    except ValidationError as e:
        return JsonResponse({"error":e.errors()},status=422) 
    
@csrf_exempt
@require_POST
def login_user(request):
    data = json.loads(request.body)
    try:
        creds = UserLogin(**data)
        user = authenticate(username=creds.username,password=creds.password)
        if user is not None:
            login(request,user)
            return JsonResponse({"message":"Logged in successfully"})
        else:
            return JsonResponse({"error":"Invalid Username or Password"},status=401)
    except ValidationError as e:
        return JsonResponse({"errors":e.errors()},status=422)

@csrf_exempt
@require_POST
def logout_user(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully."})

@require_GET
@login_required
def get_confessions(request):
    return render(request,"confessions/home.html")

@require_POST
@login_required
def post_confession(request):
    return HttpResponse("created confession")

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
def delete_confession(request,id:int):
    return HttpResponse("deleted a confession")