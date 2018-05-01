from django import forms
from .models import Comment

# 通过这个类，调用这个类的一些方法和属性，Django会自动为我们创建常规的表单代码
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  #　表明这个表单对应的数据库模型是Comment类
        fields = ['name', 'email', 'url', 'text'] # fields指定了表单需要显示的字段
