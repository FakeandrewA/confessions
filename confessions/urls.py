from django.urls import path
from .views import get_confessions,get_confession,post_confession,put_confession,delete_confession
urlpatterns = [
    path("",get_confessions), # if request was get
    path("<int:id>/",get_confession),
    path("create/",post_confession),
    path("update/<int:id>",put_confession),
    path("delete/<int:id>",delete_confession)
]