from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post
from .models import Comment
from .forms import CommentForm

# Create your views here.

def post_comment(request, post_pk):
    # 获取被评论的文章
    post = get_object_or_404(Post, pk=post_pk)
    # HTTP请求一般get, post两种，表单提交一般是post
    if request.method == 'POST':
        # 用户提交的数据存在request.POST中，这是一个类字典对象
        form = CommentForm(request.POST)
        if form.is_valid():
            # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例， 但还不保存评论数据到数据库。
            comment = form.save(commit=False)
            # 将评论和被评论的文章关联起来
            comment.post = post
            comment.save()
            # redirect会调用get_absolute_url，然后重定向到URL
            return redirect(post)
        else:
            # 数据不合法，重新渲染详情页，并且渲染表单的错误
            # post.comment_set.all()反向查询获取这篇post下的全部评论
            # post.comment_set.all()等价于Comment.objects.filter(post=post)
            comment_list = post.comment_set.all()
            context = {'post': post,
                       'form': form,
                       'comment_list': comment_list
                       }
            return render(request, 'blog/detail.html', context=context)
    return redirect(post)