from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView

# Create your views here.
# 主页函数

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    #paginate_by属性，开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 5

# def index(request):
#     post_list = Post.objects.all()
#     return render(request, 'blog/index.html', context={'post_list': post_list})

# 详细页面函数
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    # 阅读量+1， 看做是detail视图函数的调用
    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_view()
        return response

    # 对应detail视图函数中，根据文章ID获取文章，随后对post.body进行markdown渲染
    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return post

    # 对应detail视图函数中生成评论表单，获取post下的评论列表的代码部分，返回一个字典。
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     post.increase_views()  # 阅读量+1
#     post.body = markdown.markdown(post.body,
#                                   extensions=[
#                                       'markdown.extensions.extra',
#                                       'markdown.extensions.codehilite',
#                                       'markdown.extensions.toc',
#                                   ])
#     form = CommentForm()
#     comment_list = post.comment_set.all()
#     context = {'post': post,
#                'form': form,
#                'comment_list': comment_list
#                }
#     return render(request, 'blog/detail.html', context=context)

# 归档页面函数
class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter('created_time__year = year,'
                                                               'created_time__month = month'
                                                               )

# def archives(request, year, month):
#     post_list = Post.objects.filter(created_time__year = year,
#                                     created_time__month = month
#                                     ).order_by('-created_time')
#     return render(request, 'blog/index.html', context={'post_list': post_list})

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


# def category(request, pk):
#     cate = get_object_or_404(Category, pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})
