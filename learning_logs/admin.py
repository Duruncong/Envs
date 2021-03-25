from django.contrib import admin
from .models import Topic,Entry,Article,Category,Tag,ArticleComment
from django_summernote.admin import SummernoteModelAdmin
# Register your models here.

class PostAdmin(SummernoteModelAdmin):
    def post_tag(self, obj):
        return [pt.name for pt in obj.tags.all()]

    summernote_fields = ('content')  # 给content字段添加富文本
    list_display = ['article_id', 'title', 'status', 'category', 'post_tag', 'created_time']
    search_fields = ['title']  # 搜索框
    list_filter = ['created_time']  # 过滤器

#ass ArticleAdmin(admin.ModelAdmin):
class CommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'body', 'title']
    search_fields = ['title']  # 搜索框

admin.site.register(Article, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(ArticleComment,CommentAdmin)
admin.site.register(Topic)
admin.site.register(Entry)