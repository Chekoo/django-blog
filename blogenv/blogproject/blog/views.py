from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
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

    def get_context_data(self, **kwargs):
        # 视图函数中将模板变量传给模板是通过render函数的context传递一个字典实现的
        # 在类视图中，这个需要传递的模板变量是通过get_context_data获得的，所以重写该方法，让我们能插入一些我们自定义的模板变量进去
        # 首先获得父类生成的传递给模板的字典
        context = super().get_context_data(**kwargs)
        # 父类生成的字典已含有paginator, page, is_paginated
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        # 调用自己写的pagination_data方法获得分页导航条需要的数据
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        # 将分页导航条的模板变量更新到context中，注意pagination_data返回的也是一个字典
        context.update(pagination_data)
        # 将更新后的context返回，以便ListView使用这个字典中的模板变量去渲染模板
        # context字典中此时已经有了显示分页导航条所需的数据
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        left = []
        right = []
        # 标示第1页页码后是否需要显示省略号
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        # 获得用户当前请求的页码号
        page_number = page.number
        # 获得分页后的总页数
        total_pages = paginator.num_pages
        # 获得整个分页页码列表，比如分4页，[1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 若请求第1页数据，此时只要获取当前页右边的连续页码号，比如分页页码列表是[1,2,3,4]获取的是right = [2,3]
            right = page_range[page_number:page_number + 2]
            # 如果最右边页码号比最后1页的页码好减去1还要小，说明最右边
            if right[-1] < total_pages - 1:
                right_has_more = True
            # 如果最右边页码
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，此时只要获取当前页左边的连续页码号。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            # 如果最左边的页码比第2页的页码号大，则需要省略号
            if left[0] > 2:
                left_has_more = True
            # 如果最左边页码比第1页大，则第一页页码号需要显示
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number: page_number + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data

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
class ArchivesView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year = year,
                                                               created_time__month = month
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

# 标签tag视图函数
class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)