from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.versioning import QueryParameterVersioning, URLPathVersioning
from rest_framework.viewsets import ViewSetMixin


from api import models
from rest_framework import serializers, permissions

from api.auth.auth import ApiAuth
from api.serializers.article import ArticleSerializer, ArticleDetailViewSetSerializers


class ArticleView(ViewSetMixin,APIView):
    def list(self, request, *args, **kwargs):
        '''
        课程列表接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        ret = {'code': 1000, 'data': None}

        try:
            queryset = models.Article.objects.all()

            ser = ArticleSerializer(instance=queryset, many=True)

            ret['data'] = ser.data

        except Exception as e:
            ret['code'] = 1001
            ret['error'] = '获取课程失败'

        return Response(ret)

    def retrieve(self, request, *args, **kwargs):
        ret = {'code': 1000, 'data': None}
        try:
            pk = kwargs.get('pk')
            obj = models.Article.objects.filter(pk=pk).first()
            ser = ArticleDetailViewSetSerializers(instance=obj, many=False)
            ret['data'] = ser.data
        except Exception as e:
            ret['code'] = 1001
            ret['error'] = '未获取到资源'
        return Response(ret)

class AgreeView(ViewSetMixin, APIView):
    """
       点赞的接口
       """
    # permission_classes = (permissions.AllowAny,)
    def create(self, request, *args, **kwargs):
        ret = {'code':1000,'data':None}
        try:
            pk = kwargs.get('pk')
            # 方式一：更新赞数

            obj = models.Article.objects.filter(id=pk).first()

            obj.agree_num = obj.agree_num + 1
            obj.save()
            # 方式二：更新赞数
            # F，更新数据库字段
            # Q, 构造复杂条件
            # from django.db.models import F,Q
            # v = Article.objects.filter(id=pk).update(agree_num=F("agree_num") + 1)
            # print(v)
            ret['data'] = obj.agree_num
        except Exception as e:
            ret['code'] = 1001
            ret['error'] = '点赞失败'
        return Response(ret)



