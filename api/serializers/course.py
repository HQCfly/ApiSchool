from api import models

from rest_framework import serializers

from api.models import CourseCategory, DegreeCourse,CourseSubCategory

class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化
    """
    # one2one/fk/choice
    course_type = serializers.CharField(source='get_course_type_display')
    status = serializers.CharField(source='get_status_display')
    # many to many 学位课程表和大类
    degree_course = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()

    class Meta:
        model = models.Course


        fields = ['id','name','course_img','course_type','degree_course','status'
            ,'brief','pub_date','order','attachment_path','sub_category','period',
                  'template_id','degree_course','sub_category']

    def get_sub_category(self, obj):
        category_dic = {'id': obj.sub_category.id, 'name': obj.sub_category.name}
        return category_dic

    def get_degree_course(self, obj):
        degree_dic = {}
        if obj.degree_course is not None:
            degree_dic = {'id': obj.degree_course.id, 'name': obj.degree_course.name}
        return degree_dic




class CourseDetailSerializer(serializers.ModelSerializer):

    '''
    课程详情序列化
    '''
    title = serializers.CharField(source='course.name')
    img = serializers.CharField(source='course.course_img')
    level = serializers.CharField(source='course.get_level_display')

    # many to many
    recommends = serializers.SerializerMethodField()
    oftenAskedquestions = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    courseoutlines = serializers.SerializerMethodField()
    pricepolicy = serializers.SerializerMethodField()


    class Meta:
        model = models.CourseDetail
        # fields = ['course', 'title','hours', 'img', 'level', 'course_slogan',
        #           'why_study','what_to_study_brief','career_improvement',
        #           'prerequisite', 'recommends', 'chapter','video_brief_link',
        #           'teachers']
        # fields = "__all__"
        fields = ['title','img','level','hours','course_slogan','why_study',
                  'what_to_study_brief','career_improvement','prerequisite',
                  'recommends','teachers','courseoutlines','oftenAskedquestions','pricepolicy']
    def get_recommends(self,obj):
        # 获取推荐课程
        queryset = obj.recommend_courses.all()
        return [{'name': row.name} for row in queryset]


    def get_oftenAskedquestions(self,obj):
        #获取问题
        queryset = obj.course.asked_question.all()
        return [{'question': item.question, 'answer': item.answer} for item in queryset]

    def get_teachers(self, obj):
        # 获该课程章节,反向查询 查询方式：主表.子表_set()
        queryset = obj.teachers.all()

        return [{'name': item.name, 'title': item.title, 'signature': item.signature, 'image': item.image,
                 'brief': item.brief, 'role': item.get_role_display()} for item in queryset]

    def get_courseoutlines(self, obj):
        #获取该课的大纲
        queryset = obj.courseoutline_set.all()
        return [{'title': item.title, 'content': item.content} for item in queryset]

    def get_pricepolicy(self,obj):
        #获取价格政策
        queryset = obj.course.price_policy.all()
        return [{'price': item.price, 'valid_period': item.valid_period} for item in queryset]
