from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView

# Create your views here.
# 主页函数
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

# 详细页面函数
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
               'form': form,
               'comment_list': comment_list
               }
    return render(request, 'blog/detail.html', context=context)

# 归档页面函数
def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year = year,
                                    created_time__month = month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

# 分类页面函数
class CategoryView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
# get_queryset默认获取指定模型的全部列表数据,覆写该方法，改变它默认行为
# 根据URL中捕获的id(pk)获取分类，从URL捕获的命名组参数值保存在实例的kwargs(一个字典)属性里，非命名组参数保存在实例的args(一个列表)属性里
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)
