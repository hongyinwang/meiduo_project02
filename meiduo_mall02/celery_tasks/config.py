# 消息队列（目前用的是redis）
#roker_url 可以将celery加载的数据存放到redis的14号库
broker_url = "redis://127.0.0.1/14"
#result_backend 可以将celery加载的数据存放到redis的15号库
result_backend = "redis://127.0.0.1/15"