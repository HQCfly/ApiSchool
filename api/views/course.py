from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.versioning import QueryParameterVersioning, URLPathVersioning
from rest_framework.viewsets import ViewSetMixin

from api import models
from rest_framework import serializers

from api.auth.auth import ApiAuth
from api.serializers.course import CourseSerializer, CourseDetailSerializer


class CourseView(ViewSetMixin, APIView):
    # 方法一
    # versioning_class = URLPathVersioning
    # renderer_class = [JSONRenderer, BrowsableAPIRenderer]
    #
    # def get(self, request, *args, **kwargs):
    #
    #     ret = {'code': 1000, 'data': None}
    #
    #     print(ret)
    #     try:
    #         queryset = models.Course.objects.all()
    #         ser = CourseSerializer(instance=queryset,many=True)
    #         ret['data'] = ser.data
    #     except Exception as e:
    #         ret['code'] = 1001
    #         ret['error'] = '获取课程失败'
    #
    #     return Response(ret)

    #方法二
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
            queryset = models.Course.objects.all()

            ser = CourseSerializer(instance=queryset, many=True)

            ret['data'] = ser.data

        except Exception as e:
            ret['code'] = 1001
            ret['error'] = '获取课程失败'

        return Response(ret)

    def retrieve(self, request, *args, **kwargs):
        """
        课程详细接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        ret = {'code': 1000, 'data': None}

        try:
            # 课程ID=2
            pk = kwargs.get('pk')

            # 课程详细对象
            obj = models.CourseDetail.objects.filter(course_id=pk).first()
            ser = CourseDetailSerializer(instance=obj, many=False)

            ret['data'] = ser.data

        except Exception as e:
            ret['code'] = 1001
            ret['error'] = '获取课程失败'

        return Response(ret)



# b.查看所有学位课并打印学位课名称以及学位课的奖学金

# c.展示所有的专题课

# d. 查看id=1的学位课对应的所有模块名称

# e.获取id = 1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses

# f.获取id = 1的专题课，并打印该课程相关的所有常见问题

# g.获取id = 1的专题课，并打印该课程相关的课程大纲

# h.获取id = 1的专题课，并打印该课程相关的所有章节