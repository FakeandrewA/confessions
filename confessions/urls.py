from django.urls import path
from .views import get_confessions,get_confession,post_confession,put_confession,delete_confession,register_user,login_user,logout_user

app_name = "confessions"
urlpatterns = [
    path("register/",register_user,name="register_user"),
    path("login/",login_user,name="login_user"),
    path("logout/",logout_user,name="logout_user"),
    path("",get_confessions,name="homepage"), # if request was get
    path("<int:id>/",get_confession,name="get_confession"),
    path("create/",post_confession,name="post_confession"),
    path("update/<int:id>/",put_confession,name="update_confession"),
    path("delete/<int:id>/",delete_confession,name="delete_confession")
]