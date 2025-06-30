from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET,require_POST,require_http_methods
# Create your views here.

@require_GET
def get_confessions(request):
    return render(request,"confessions/home.html")

@require_POST
def post_confession(request):
    return HttpResponse("created confession")

@require_GET
def get_confession(request,id:int):
    return HttpResponse("got a confession")

@require_http_methods(["PUT"])
def put_confession(request,id:int):
    return HttpResponse("updated a confession")

@require_http_methods(["DELETE"])
def delete_confession(request,id:int):
    return HttpResponse("deleted a confession")