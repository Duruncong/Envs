from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from learning_log import settings
from .models import Article, ArticleComment, Category, Tag
from users.forms import LoginForm
from users.models import UserProfile



# Create your views here.
def index(request):
    """学习笔记的主页"""
    if request.user is not None and request.user.is_active:
        userprofile = UserProfile.objects.get(user=request.user)
        return render(request, 'learning_logs/index.html', {'userprofile':userprofile})
    else:
        return render(request, 'learning_logs/index.html')


def articles(request):  # 查看文章
    form = LoginForm()
    posts = Article.objects.filter(status='p')  # 获取全部的Article对象
    x = 0
    request.session['x'] = x
    paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    mposts = Article.objects.count()
    m = int(mposts)
    n = int(settings.PAGE_NUM + x)
    if m - n > 0:
        datastatus = True
    else:
        datastatus = False

    if request.user is not None and request.user.is_active:
        userprofile = UserProfile.objects.get(user=request.user)
        return render(request, 'learning_logs/articles.html', {'post_list': post_list, 'userprofile': userprofile,
                                                               'datastatus':datastatus})
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                user = auth.authenticate(username=username, password=password)

                if user is not None and user.is_active:
                    user = User.objects.get(username=username)
                    userprofile = UserProfile.objects.get(user=user)
                    auth.login(request, user)
                    return render(request, 'learning_logs/articles.html',
                                  {'userprofile': userprofile,'post_list': post_list,
                                    'datastatus':datastatus})
                else:
                    # 登陆失败
                    return render(request, 'learning_logs/articles.html', {'form': form,'datastatus':datastatus,'post_list': post_list,
                                                                'message': 'Wrong password or This username does not exist.'})
        else:
            form = LoginForm()

        return render(request, 'learning_logs/articles.html', {'post_list': post_list, 'datastatus':datastatus, 'form':form})


def loadmore(request):
    posts = Article.objects.filter(status='p')
    x = request.session['x']
    x += 2
    request.session['x'] = x
    print(x)
    paginator = Paginator(posts, settings.PAGE_NUM+x)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    mposts = Article.objects.count()
    m = int(mposts)
    n = int(settings.PAGE_NUM+x)
    if m-n > 0:
        datastatus=True
    else:
        datastatus=False

    if request.user is not None and request.user.is_active:
        userprofile = UserProfile.objects.get(user=request.user)
        return render(request, 'learning_logs/articles.html', {'post_list': post_list, 'userprofile': userprofile,
                                                                    'datastatus':datastatus})
    else:
        return render(request, 'learning_logs/articles.html', {'post_list': post_list, 'datastatus':datastatus})


def detail(request, id):  # 查看文章详情
    try:
        post = Article.objects.get(article_id=str(id))
        post.viewed()  # 更新浏览次数
        # tags = Tag.objects.all()  # 获取文章对应所有标签
    except Article.DoesNotExist:
        raise Http404
    comments = ArticleComment.objects.filter(article=str(id))
    paginator = Paginator(comments, 3)  # 每页显示3条评论
    page = request.GET.get('page')  # 获取URL中page参数的值
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)

    x = 1
    previous_post = Article.objects.filter(article_id=str(id - x))
    while previous_post and id != 0:
        previous_post = Article.objects.get(article_id=str(id - x))
        if previous_post and previous_post.status == 'p':
            previous_post = Article.objects.get(article_id=str(id - x))
            break
        else:
            x += 1
            previous_post = Article.objects.filter(article_id=str(id - x))

    y = 1
    next_post = Article.objects.filter(article_id=str(id + y))
    while next_post:
        next_post = Article.objects.get(article_id=str(id + y))
        if next_post and next_post.status == 'p':
            next_post = Article.objects.get(article_id=str(id + y))
            break
        else:
            y += 1
            next_post = Article.objects.filter(article_id=str(id + y))
    if request.user is not None and request.user.is_active:
        userprofile = UserProfile.objects.get(user=request.user)
        return render(request, 'learning_logs/detail.html', {'post': post,
                                                             'comment_list':comment_list,'previouspost':previous_post,
                                                             'nextpost':next_post,'userprofile':userprofile})
    else:
        return render(request, 'learning_logs/detail.html', {'post': post,
                                                             'comment_list': comment_list,
                                                             'previouspost': previous_post,
                                                             'nextpost': next_post,})


def commentpost(request):
    if request.method == 'POST':
        comment = request.POST.get('comment','')
        id = request.POST.get('id')
        print("ok")
        if comment!='':
            message = comment
            userimg = 'media/'+request.session['username']+'.png'
            username = request.session['username']
            article = Article.objects.get(article_id = str(id))
            newrecord = ArticleComment()
            newrecord.body = message
            newrecord.article = id
            newrecord.userimg = userimg
            newrecord.username = username
            newrecord.title = article.title
            newrecord.save()
            user = User.objects.get(username=username)
            userprofile = UserProfile.objects.get(user=user)
            userprofile.comment()
            return HttpResponse()


def comment_del(request):
    if request.method=='POST':
        comment_id = request.POST.get("comment_id")
        user_name = request.session['username']
        user = User.objects.get(username=user_name)
        ArticleComment.objects.filter(id=str(comment_id)).delete()
        user.comment_del()
        comments = ArticleComment.objects.filter(username=user_name)
        paginator = Paginator(comments, 1)  # 每页显示数量，对应settings.py中的PAGE_NUM
        page = request.GET.get('page')  # 获取URL中page参数的值
        try:
            comment_list = paginator.page(page)
        except PageNotAnInteger:
            comment_list = paginator.page(1)
        except EmptyPage:
            comment_list = paginator.page(paginator.num_pages)
        return HttpResponse()


@login_required
def category(request,id):
    userprofile = UserProfile.objects.get(user=request.user)
    post_list =Article.objects.filter(category_id = str(id))
    cname = Category.objects.get(id=str(id))
    # paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    # page = request.GET.get('page')  # 获取URL中page参数的值
    # try:
    #     post_list = paginator.page(page)
    # except PageNotAnInteger:
    #     post_list = paginator.page(1)
    # except EmptyPage:
    #     post_list = paginator.page(paginator.num_pages)
    return render(request, 'learning_logs/category.html', {'post_list':post_list,'userprofile':userprofile,
                                                           'cname':cname})


def tags(request,id):
    userprofile = UserProfile.objects.get(user=request.user)
    # 查询相关标签文章
    post_list = Article.objects.filter(tags=id)
    tname = Tag.objects.get(id=str(id))
    return render(request, 'learning_logs/tags.html', {'post_list':post_list,'userprofile':userprofile,
                                                           'tname':tname})


def archives(request,year,month):
    userprofile = UserProfile.objects.get(user=request.user)
    # 查询X年X月的文章
    post_list = Article.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    archives = Article.objects.dates('created_time', 'month')
    for archive in archives:
        if archive.year == year and archive.month == month:
            # paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
            # page = request.GET.get('page')  # 获取URL中page参数的值
            # try:
            #     post_list = paginator.page(page)
            # except PageNotAnInteger:
            #     post_list = paginator.page(1)
            # except EmptyPage:
            #     post_list = paginator.page(paginator.num_pages)
            return render(request, 'learning_logs/archives.html', {'post_list':post_list,'userprofile':userprofile,
                                                                    'archive':archive})


def search(request):
    # if request.method =='POST':
    search_info = request.POST.get('info','')
    posts = Article.objects.filter(title__icontains = search_info)
    paginator = Paginator(posts, settings.PAGE_NUM)  # 每页显示数量，对应settings.py中的PAGE_NUM
    page = request.GET.get('page')  # 获取URL中page参数的值
    results = Article.objects.filter(title__icontains = search_info).count()
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    if request.user is not None and request.user.is_active:
        userprofile = UserProfile.objects.get(user=request.user)
        return render(request, 'learning_logs/search.html', {'post_list': post_list,'userprofile':userprofile,
                                                             'results':results})
    else:
        return render(request, 'learning_logs/search.html', {'post_list': post_list,'results':results})

    # return render(request, 'learning_logs/articles.html')


# def index_unlog(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#
#             user = auth.authenticate(username=username, password=password)
#
#             if user is not None and user.is_active:
#                 user = User.objects.get(username=username)
#                 userprofile = UserProfile.objects.get(user=user)
#                 auth.login(request, user)
#                 return render(request, 'learning_logs/index.html',
#                               {'userprofile':userprofile})
#             else:
#                 # 登陆失败
#                 # return JsonResponse(request, {'res':0})
#                 return render(request, 'learning_logs/index_unlog.html', {'form': form,
#                                  'message': 'Wrong password or This username does not exist.'})
#     else:
#         form = LoginForm()
#
#     return render(request, 'learning_logs/index_unlog.html', {'form':form})