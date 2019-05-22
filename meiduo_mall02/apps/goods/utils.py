
#数据写的太死了
# def get_brandcrumb(cat):
    #     # cat 传递过来的是一个 三级分类
    #
    #     # 组织面包屑数据
    #     """
    #     {
    #         cat1:一级分类内容,
    #         cat2:二级分类内容,
    #         cat3:三级分类内容
    #     }
    #     """
    # return {
    #     'cat1':cat.parent.parent,
    #     'cat2':cat.parent,
    #     'cat3':cat
    # }

#数据尽量不要写死
def get_brandcrumb(cat):
    """

    :param cat:
    :return:
    """
    #cat不知道是几级分类
    breadcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':''
    }
    #cat父类不存在
    if cat.parent is None:
        breadcrumb['cat1']=cat
    #cat子类数量为零
    elif cat.subs.count() == 0:
        breadcrumb['cat3']=cat
        breadcrumb['cat2']=cat.parent
        breadcrumb['cat1']=cat.parent.parent
    else:
        breadcrumb['cat2']=cat
        breadcrumb['cat1']=cat.parent

    return breadcrumb

