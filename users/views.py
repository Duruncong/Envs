from django.shortcuts import render
from django.contrib.auth.models import User
from .models import UserProfile
from PIL import Image
from django.contrib import auth
from .forms import RegistrationForm, LoginForm, ForgetForm, ResetForm, UserProfileForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('learning_logs:index'))


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            photo = request.FILES.get('photo')
            # 使用内置User自带create_user方法创建用户，不需要使用save()
            if not photo:
                return render(request,'users/register.html', {'error': '请选择头像!', 'form':form})
            else:
                user = User.objects.create_user(username=username, password=password, email=email)
                user_profile = UserProfile(user=user)
                user_profile.photo = '/static/media/' + username + '.png'
                img = Image.open(photo)
                size = img.size
                print(size)
                # 因为是要圆形，所以需要正方形的图片
                r2 = min(size[0], size[1])
                if size[0] != size[1]:
                    img = img.resize((r2, r2), Image.ANTIALIAS)

                    # 最后生成圆的半径
                r3 = int(r2 / 2)
                img_circle = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
                pima = img.load()  # 像素的访问对象
                pimb = img_circle.load()
                r = float(r2 / 2)  # 圆心横坐标

                for i in range(r2):
                    for j in range(r2):
                        lx = abs(i - r)  # 到圆心距离的横坐标
                        ly = abs(j - r)  # 到圆心距离的纵坐标
                        l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径

                        if l < r3:
                            pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
                img_circle.save('static/media/' + username + '.png')
            # 如果直接使用objects.create()方法后不需要使用save()
                user_profile.save()
            return HttpResponseRedirect(reverse("users:login"))

    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def forget(request):
    if request.method == 'POST':
        form = ForgetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            user = User.objects.filter(username=username)

            if user:
                user = User.objects.get(username=username)
                if user.email == email:
                    request.session['username'] = username
                    return render(request,'users/reset.html')
                else:
                    form = ForgetForm()           # return HttpResponseRedirect(reverse('users:forget', {'error': '您的用户名和邮箱不匹配!'}))
                    return render(request,'users/forget.html',{'form': form,
                        'error': '您的用户名和邮箱不匹配'})
            else:
                form = ForgetForm()
                return render(request, 'users/forget.html', {'form': form,
                        'error': '用户名不存在！'})
    else:
        form = ForgetForm()

    return render(request, 'users/forget.html', {'form': form})


def reset(request):
    if request.method == 'POST':
        form = ResetForm(request.POST)
        username = request.session['username']
        user = User.objects.get(username = username)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 == password2:
                user.set_password(password2)
                user.save()
                return HttpResponseRedirect(reverse('users:login'))
            else:
                return render(request,'users/reset.html', {'error': '两次密码输入不一致！'})
    else:
        form = ResetForm()

    return render(request,'users/reset.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                user = User.objects.get(username=username)
                userprofile = UserProfile.objects.get(user=user)
                request.session['username']=user.username
                photo ='/static/media/'+ user.username + '.png'
                request.session['photo']=photo
                auth.login(request, user)
                return render(request, 'learning_logs/index.html',
                              {'userprofile':userprofile})
            else:
                # 登陆失败
                return render(request, 'users/login.html', {'form': form,
                                 'message': 'Wrong password or This username does not exist.'})
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

@login_required
def myinfo(request, user_id):
    user = User.objects.get(id=user_id)
    userprofile = UserProfile.objects.get(user=user)
    username = request.user.username
    request.session['username'] = username
    return render(request, "users/myinfo.html", {"user":user, "userprofile":userprofile})

@login_required
def myinfo_edit(request, user_id):
    user = User.objects.get(id=user_id)
    userprofile = UserProfile.objects.get(user=user)

    if request.method == "POST":
        form = UserProfileForm(request.POST)

        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            userprofile.birth = form.cleaned_data['birth']
            userprofile.com = form.cleaned_data['com']
            userprofile.telephone = form.cleaned_data['telephone']
            userprofile.save()

            return HttpResponseRedirect(reverse('users:myinfo', args=[user.id]))
    else:
        default_data = {'first_name': user.first_name, 'last_name': user.last_name,
                        'birthday': userprofile.birth, 'telephone': userprofile.telephone,
                        'company': userprofile.com}
        form = UserProfileForm(default_data)

    return render(request, 'users/myinfo_edit.html', {'form': form, 'user': user})



# from django.shortcuts import render, redirect
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from django.contrib.auth import login, logout, authenticate
# from django.views import View
# from openpyxl.drawing.images import Image
# from .models import User
# # Create your views here.
#
#
# def logout_view(request):
#     """注销用户"""
#     del request.session['IS_LOGIN']
#     del request.session['username']
#     del request.session['nickname']
#     return render(request, 'learning_logs/index_unlog.html')
#
#
# def login_view(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username', '')
#         pass_word = request.POST.get('password', '')
#         user = User.objects.filter(username=user_name)  # 查看数据库里是否有该用户名
#         if user:  # 如果存在
#             user = User.objects.get(username=user_name)  # 读取该用户信息
#             if pass_word == user.password:  # 检查密码是否匹配
#                 request.session['IS_LOGIN'] = True
#                 request.session['nickname'] = user.nickname
#                 request.session['username'] = user_name
#                 return render(request,'learning_logs/index.html',{'user':user})
#             else:
#                 return render(request,'users/login.html',{'error': '密码错误!'})
#         else:
#             return render(request, 'users/login.html', {'error': '用户名不存在!'})
#
#     else:
#         return render(request,'users/login.html')
#
#
# def register(request):
#     if request.method =='POST':
#         user_name = request.POST.get('username','')
#         pass_word_1 = request.POST.get('password_1','')
#         pass_word_2 = request.POST.get('password_2','')
#         nick_name = request.POST.get('nickname','')
#         email = request.POST.get('email','')
#         avatar = request.FILES.get('avatar')
#         if User.objects.filter(username = user_name):
#             return render(request,'user/register.html',{'error':'用户已存在'})
#             #将表单写入数据库
#         if(pass_word_1 != pass_word_2):
#             return render(request, 'users/register.html', {'error': '两次密码请输入一致'})
#         user = User()
#         if avatar:
#             user.avatar = 'media/' + user_name + '.png'
#             img = Image.open(avatar)
#             size = img.size
#             print(size)
#             # 因为是要圆形，所以需要正方形的图片
#             r2 = min(size[0], size[1])
#             if size[0] != size[1]:
#                 img = img.resize((r2, r2), Image.ANTIALIAS)
#             # 最后生成圆的半径
#             r3 = int(r2/2)
#             img_circle = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
#             pima = img.load()  # 像素的访问对象
#             pimb = img_circle.load()
#             r = float(r2 / 2)  # 圆心横坐标
#             for i in range(r2):
#                 for j in range(r2):
#                     lx = abs(i - r)  # 到圆心距离的横坐标
#                     ly = abs(j - r)  # 到圆心距离的纵坐标
#                     l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径
#
#                     if l < r3:
#                         pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
#             img_circle.save('static/media/'+user_name+'.png')
#         user.username = user_name
#         user.password = pass_word_1
#         user.email = email
#         user.nickname = nick_name
#         user.save()
#             #返回注册成功页面
#         return render(request,'learning_logs/index.html')
#     else:
#         return render(request,'users/register.html')
#
#
# def logsuccess(request):
#     return render(request, 'learning_logs/index.html')
#
#
# def forget_password(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username','')
#         email = request.POST.get('email','')
#         user = User.objects.filter(username = user_name)
#         if user:
#             user = User.objects.get(username = user_name)
#             if(user.email == email):
#                 request.session['user_name'] = user_name
#                 return render(request,'users/reset.html')
#             else:
#                 return render(request,'users/forget.html',{'error':'您的用户名和邮箱不匹配！'})
#         else:
#             return render(request,'users/forget.html',{'error':'请输入正确的用户名'})
#     else:
#         return  render(request,'users/forget.html')
#
#
# def reset(request):
#     if request.method == 'POST':
#         pass_word1 = request.POST.get('password1','')
#         pass_word2 = request.POST.get('password2','')
#         user_name = request.session['user_name']
#         user = User.objects.get(username = user_name)
#         if pass_word1 == pass_word2:
#             user.password = pass_word1
#             user.save()
#             return render(request,'users/login.html')
#         else:
#             return render(request,'users/reset.html', {'error': '两次密码输入不一致！'})
#     else:
#         return render(request,'users/reset.html')

# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.models import User
# from .models import UserProfile
# from django.contrib import auth
# from .forms import RegistrationForm, LoginForm
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
#
#
# def register(request):
#     if request.method == 'POST':
#
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password2']
#
#             # 使用内置User自带create_user方法创建用户，不需要使用save()
#             user = User.objects.create_user(username=username, password=password, email=email)
#
#             # 如果直接使用objects.create()方法后不需要使用save()
#             user_profile = UserProfile(user=user)
#             user_profile.save()
#
#             return HttpResponseRedirect("/accounts/login/")
#
#     else:
#         form = RegistrationForm()
#
#     return render(request, 'users/register.html', {'form': form})
#
#
# def login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#
#             user = auth.authenticate(username=username, password=password)
#
#             if user is not None and user.is_active:
#                auth.login(request, user)
#                return HttpResponseRedirect(reverse('users:profile', args=[user.id]))
#
#             else:
#                 # 登陆失败
#                  return render(request, 'users/login.html', {'form': form,
#                                'message': 'Wrong password. Please try again.'})
#     else:
#         form = LoginForm()
#
#     return render(request, 'users/login.html', {'form': form})


    # """注册新用户"""
    # if request.method != 'POST':
    #     # 显示空的注册表
    #     form = UserCreationForm()
    # else:
    #     # 处理填写好的表单
    #     form = UserCreationForm(data=request.POST)
    #
    #     if form.is_valid():
    #         new_user = form.save()
    #         # 让用户自动登录，再重定向到主页
    #         authenticated_user = authenticate(username=new_user.username, password=request.POST['password1'])
    #         login(request, authenticated_user)
    #         return HttpResponseRedirect(reverse('learning_logs:index'))
    #
    # context = {'form': form}
    # return render(request, 'users/register.html', context)