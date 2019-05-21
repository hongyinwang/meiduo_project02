from collections import OrderedDict

from apps.goods.models import GoodsChannel


def get_categories():
    """
    # 1.初始化有序字典
    # 2.查询出所有的频道，根据分组和顺序进行排序
    # 　先根据组id(group_id)进行排序,然后根据顺序(sequence)进行排序,channels(频道)
    # 3.对所有的频道进行遍历
    # 4.获取当前组
    # 5.判断当前频道(组id)是否在频道字典中,不过不在则则初始化当前频道
    # 6.获取当前频道的分类
    # 7.追加当前频道
    # 8.获取当前分类及当前分类的子分类.子子分类,添加到sub_cats
    :return:
    """
    # 1.初始化有序字典
    categories = OrderedDict()
    # 2.查询出所有的频道，根据分组和顺序进行排序
    # 　先根据组id(group_id)进行排序,然后根据顺序(sequence)进行排序,channels(频道)
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 3.对所有的频道进行遍历
    for channel in channels:
        # 4.获取当前组
        group_id = channel.group_id  # 当前组
        # 5.判断当前频道(组id)是否在频道字典中,不过不在则则初始化当前频道
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}
        # 6.获取当前频道的分类
        cat1 = channel.category  # 当前频道的类别

        # 7.追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 8.获取当前分类及当前分类的子分类.子子分类,添加到sub_cats
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories
