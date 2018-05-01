from ..models import Post, Category
from django import template

register = template.Library()

# 注册为模板标签
# register.simple_tag, 这样可以在模板中使用语法{% get_recent_posts %}调用这个函数
@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]

# dates返回一个列表,列表中的元素为每一篇文章（Post）的创建时间，且是 Python 的 date 对象，精确到月份，降序排列。
# order='DESC' 表明降序排列（即离当前越近的时间越排在前面）
@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')

@register.simple_tag
def get_categories():
    return Category.objects.all()
