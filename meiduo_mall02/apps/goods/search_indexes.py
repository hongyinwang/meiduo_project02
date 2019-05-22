from haystack import indexes

from .models import SKU

"""
    1.向Haystack和搜索引擎指示搜索的主要字段(document=True)
    2.对那个模型进行检索
    3.对那些数据进行检索
"""
#　模型类文件名indexes,类名SerchIndex
class SKUIndex(indexes.SearchIndex, indexes.Indexable):

    # 1.向Haystack和搜索引擎指示搜索的主要字段
        # text 是惯例命名
        # 每个都SearchIndex需要有一个（也是唯一一个）字段 document=True。
        # 向Haystack和搜索引擎指示哪个字段是用于在其中搜索的主要字段
    text = indexes.CharField(document=True, use_template=True)

    #2.对那个模型进行检索
    def get_model(self):
        """返回建立索引的模型类"""
        return SKU #SKU=Stock Keeping Unit(库存量单位)
    #3.对那些数据进行检索
    def index_queryset(self, using=None):

        return self.get_model().objects.filter(is_launched=True)

