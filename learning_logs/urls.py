"""定义learning_logs的URL模式"""

from django.urls import path, re_path
from . import views

app_name = 'learning_logs'
urlpatterns = [
    # 主页
    path('', views.index, name='index'),
    # 显示所有的文章
    path('articles/', views.articles, name='articles'),
    # 加载更多
    path('articles/more', views.loadmore, name='loadmore'),
    # 详情
    path('articles/<int:id>/', views.detail, name='detail'),
    # 分类
    path('category/<int:id>/', views.category, name='category'),
    # 标签
    path('tags/<int:id>/', views.tags, name='tags'),
    # 归档
    path('archives/<int:year>/<int:month>/', views.archives, name='archives'),

    path('commentpost',views.commentpost,name='commentpost'),

    path('commentdel',views.comment_del,name='comment_del'),
    # 搜索
    path('search/',views.search,name='search'),
]