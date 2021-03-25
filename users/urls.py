"""定义users的URL模式"""
from django.urls import path, re_path, include
from django.contrib.auth.views import LoginView

from . import views

app_name = 'users'
urlpatterns =[
    # 登陆主页
    path('login/', views.login_view, name='login'),
    # 注销
    re_path(r'^logout/$', views.logout_view, name='logout'),
    # 注册页面
    re_path(r'^register/$', views.register, name='register'),
    #
    re_path(r'^forget/$', views.forget, name='forget'),
    #
    path('reset/', views.reset, name='reset'),

    re_path(r'^(?P<user_id>\d+)/myinfo$', views.myinfo, name='myinfo'),

    re_path(r'^(?P<user_id>\d+)/myinfo/edit$', views.myinfo_edit, name="myinfo_edit")
]