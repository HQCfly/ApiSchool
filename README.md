# rest framework + vue projection
# 1. 渲染器
规定页面显示的效果
# 2. 版本 
原理：要了解使用：
## 2.1. 添加配置
### 2.1.1. 添加配置
				REST_FRAMEWORK = {
					
					.... 
					
					'DEFAULT_VERSIONING_CLASS':'rest_framework.versioning.URLPathVersioning',
					'ALLOWED_VERSIONS':['v1','v2'], # 允许的版本
					'VERSION_PARAM':'version', # 参数
					'DEFAULT_VERSION':'v1', # 默认版本
					....
				}
### 2.1.2 设置路由 
urls.py:

	urlpatterns = [
	    #url(r'^admin/', admin.site.urls),
		    url(r'^api/(?P<version>\w+)/', include('api.urls')),
		]
				
api/urls.py :

		urlpatterns = [
		    url(r'^course/$', course.CourseView.as_view()),
			]
			
### 2.1.3. 获取版本 
request.version 获取版本  
			
	
# 3. vue+rest framework
## 3.1 vue: 
- 路由 + 组件 
- axios发送ajax请求
- that 
## 3.2 api:
- 跨域: 
(1)域名不同
(2)端口不同 
- cors:
本质设置响应头

			#允许你的域名来获取我的数据
			response['Access-Control-Allow-Origin'] = "*"

			# 允许你携带Content-Type请求头
			response['Access-Control-Allow-Headers'] = "Content-Type"

			# 允许你发送DELETE,PUT
			response['Access-Control-Allow-Methods'] = "DELETE,PUT"
			
			
			
# 4. 序列化
	- source
	- method 
# 5.推荐课程，用户拦截,拦截器
## 5.1 VUE:
- 课程列表：this.$axios + this 
- 课程详细：this.$axios + this 
- 用户登录：
    - this.$axios
	- this 
	- 跨域简单和复杂请求
	- vuex做全局变量
	- vuex-cookies 
- 微职位 
	- 拦截器
	- 携带token 
			
PS: api可以同一放在store中保存
			
## 5.2 API:
- 课程列表 
    - 序列化：source='get_level_display'
- 课程详细：
    - 序列化：source='get_level_display'
    - 序列化：method
- 用户登录 
    - update_or_create
- 微职位 
    - 认证组件 
			
- 关联组件：
    - 版本
    - 解析器
    - 渲染器
    - 序列化 
    - 认证组件 
    - 视图 
    - 路由 
    
# 6.加入购物车，保存到redis：
a. 临时状态
b. 修改购物信息
结构：
    

    redis->{
        	#后面两个数字代表：第一个是用户id，第二个是课程id
            shopping_car_6_11:{
                'title':'法务',
                'src':'xxx.png',
                'policy':{
                    1:{id:'xx'.....},
                    2:{id:'xx'.....},
                    3:{id:'xx'.....},
                    4:{id:'xx'.....},
                },
                'default_policy':3
            },
            shopping_car_6_13:{
                ...
            }
    }
# 7.结算中心
请求体：

	{
		courseids:[1,2]
	}
## 7.1业务处理（POST）：
1. 检测课程ID是否已经加入到购物车
2. 获取指定价格策略信息
3. 获取优惠券信息
4. 构造结构放入redis	
## 7.2业务处理（GET）：
1. 获取结算中心里的课程信息（绑定课程优惠券）
2. 获取全局优惠券
## 7.3PATCH请求
请求体：

        {
            courseid:0
            couponid:12
        }
业务处理：
1. 校验结算中心是否存在该课程
2. 校验优惠券是否可用
					
注意： 
1. 优惠券状态
2. 优惠券使用时间
## 7.4构建目标数据结构
结算数据结构：

			payment_dict = {
				'2': {
					course_id:2,
					'title': '法务一', 
					'img': '1.jpg', 'policy_id': '4', 
					'coupon': {}, 
					'default_coupon': 0, 
					'period': 210, 'period_display': '12个月', 'price': 122.0}, 
				'1': {
					course_id:2,
					'title': '法务2', 
					'img': '2.jpg', 
					'policy_id': '2', 
					'coupon': {
						4: {'coupon_type': 0, 'coupon_display': '立减券', 'money_equivalent_value': 40}, 
						6: {'coupon_type': 1, 'coupon_display': '满减券', 'money_equivalent_value': 60, 'minimum_consume': 100}
					}, 
					'default_coupon': 0, 
					'period': 60, 
					'period_display': '2个月', 
					'price': 599.0}
			}

			global_coupon_dict = {
				'coupon': {
					2: {'coupon_type': 1, 'coupon_display': '满减券', 'money_equivalent_value': 200, 'minimum_consume': 500}
				}, 
				'default_coupon': 0
			}
			
========================== redis ==============================

			redis = {
				payment_1_2:{
					course_id:2,
					'title': '法务1', 
					'img': '1.jpg', 'policy_id': '4', 
					'coupon': {}, 
					'default_coupon': 0, 
					'period': 210, 'period_display': '12个月', 'price': 122.0}, 
				},
				payment_1_1:{
					course_id:1,
					'title': '法务2', 
					'img': '2.jpg', 
					'policy_id': '2', 
					'coupon': {
						4: {'coupon_type': 0, 'coupon_display': '立减券', 'money_equivalent_value': 40}, 
						6: {'coupon_type': 1, 'coupon_display': '满减券', 'money_equivalent_value': 60, 'minimum_consume': 100}
					}, 
					'default_coupon': 0, 
					'period': 60, 
					'period_display': '2个月', 
					'price': 599.0}
				},
				payment_global_coupon_1:{
					'coupon': {
						2: {'coupon_type': 1, 'coupon_display': '满减券', 'money_equivalent_value': 200, 'minimum_consume': 500}
					}, 
					'default_coupon': 0
				}
			}



