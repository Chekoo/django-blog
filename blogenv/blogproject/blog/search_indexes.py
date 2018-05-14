from haystack import indexes
from .models import Post

# 相对应某个App下的数据进行全文检索，就要在该app下创建一个search_indexes.py文件，然后创建
# 一个XXindex类，并且继承SearchIndex和Indexable
# 为Post创建一个索引
class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()