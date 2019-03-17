from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from api.views import course,account,article,shoppingcar,payment,order,orderView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 关于课程的接口
    url(r'^course/$', course.CourseView.as_view({'get': 'list'})),
    url(r'^course/(?P<pk>\d+)/$', course.CourseView.as_view({'get': 'retrieve'})),
    # 关于文章的接口
    url(r'^article/$', article.ArticleView.as_view({'get': 'list'})),
    url(r'^article/(?P<pk>\d+)/$', article.ArticleView.as_view({'get': 'retrieve'})),
    # 点赞的接口
    url(r'^article/(?P<pk>\d+)/agree/$', article.AgreeView.as_view({'post': 'create'})),


    # 购物车
    url(r'^shoppingcar/$', shoppingcar.ShoppingCarViewSet.as_view()),
    # url(r'^shoppingcar/$', shoppingcar.ShoppingCarViewSet.as_view({'post':'create','get':'list','delete':'destroy','put':'patch'})),
    #结算中心
    url(r'^payment/$', payment.PaymentViewSet.as_view()),
    #支付中心
    url(r'^order/$', order.OrdersViewSet.as_view()),
    url(r'^ordercheck/$', orderView.ordercheck),
    url(r'^ordercheck/$', orderView.ordershow),
    #登录权限接口
    url(r'^auth/$', account.AuthView.as_view()),
]
