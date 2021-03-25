from django.db import models
from django.contrib import  admin
import static
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    birth = models.CharField('Birthday', max_length=50, blank=True)

    telephone = models.CharField('Telephone', max_length=50, blank=True)

    com = models.CharField('Company', max_length=128, blank=True)

    comment_num = models.PositiveIntegerField(verbose_name='评论数', default=0)  # 评论数

    mod_date = models.DateTimeField('Last modified', auto_now=True)

    photo = models.ImageField(upload_to = 'media', default="/static/media/default.png")  #用户头像

    def __str__(self):
        return "user:{}".format(self.user.__str__())

    def comment(self):
        self.comment_num += 1
        self.save(update_fields=['comment_num'])

    def comment_del(self):
        self.comment_num -= 1
        self.save(update_fields=['comment_num'])

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'  # 指定后台显示模型复数名称