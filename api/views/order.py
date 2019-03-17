import random

from django.db.models import F
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from api.auth.auth import ApiAuth
from django.conf import settings
from django_redis import get_redis_connection
import json

from api.models import Course, Coupon
from utils.response import BaseResponse
from api import models
import datetime
import time
from django.utils.timezone import now
from django.db import transaction
from utils.pay import AliPay


def aliPay():
    obj = AliPay(
        appid=settings.APPID,
        app_notify_url=settings.NOTIFY_URL,  # 如果支付成功，支付宝会向这个地址发送POST请求（校验是否支付已经完成）
        return_url=settings.RETURN_URL,  # 如果支付成功，重定向回到你的网站的地址。
        alipay_public_key_path=settings.PUB_KEY_PATH,  # 支付宝公钥
        app_private_key_path=settings.PRI_KEY_PATH,  # 应用私钥
        debug=True,  # 默认False,
    )
    return obj


def generate_order_num():
    """
    生成订单编号，且必须唯一
    :return:
    """
    order_num = time.strftime('%Y%m%h%H%M%S', time.localtime() + str(random.randint(111, 999)))
    return order_num
    # while True:
    #     order_num = time.strftime('%Y%m%h%H%M%S', time.localtime() + str(random.randint(111, 999)))
    #     if not models.Order.objects.filter(order_number=order_num).exists():
    #         break
    #     return order_num


def generate_transaction_num():
    """
    生成流水编号，且必须唯一
    :return:
    """
    transaction_number = time.strftime('%Y%m%h%H%M%S', time.localtime() + str(random.randint(111, 999)))
    return transaction_number
    # while True:
    #     transaction_number = time.strftime('%Y%m%h%H%M%S', time.localtime() + str(random.randint(111, 999)))
    #     if not models.TransactionRecord.objects.filter(transaction_number=transaction_number).exists():
    #         break
    #     return transaction_number


class OrdersViewSet(APIView):
    authentication_classes = [ApiAuth]
    conn = get_redis_connection("default")

    def post(self, request, *args, **kwargs):
        """
        立即支付
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        res = BaseResponse()

        try:

            web_price = float(request.data.get('price', ''))
            balance = float(request.data.get('balance', ''))
            user_id = request.auth.user_id

            # 校验数据合法性
            """
            2.1根据user_id获取用户数据库中的网站金币与前端1：1
            """
            user_balance = request.auth.user.balance
            print(user_balance)
            if balance > float(user_balance):
                res.code = 1040
                res.error = '账号余额不足'
                return Response(res.dict)
            settment_key = settings.PAYMENT_KEY % (user_id, '*')
            print(settment_key)
            all_key = self.conn.scan_iter(settment_key)
            course_all_price = 0
            # print(all_key)
            # 带限制的优惠券课程列表
            # [
            #     {
            #         'period_display': '24个月',
            #         'img': 'quanzhan.png',
            #         'policy_id': '2',
            #         'course_id': '1',
            #         'title': 'Python全栈',
            #         'default_coupon': '0',
            #         'coupon':
            #             {
            #                 '1':
            #                     {
            #                         'coupon_type': 1,
            #                         'coupon_display': '满减券',
            #                         'money_equivalent_value': 60,
            #                         'minimum_consume': 100},
            #                 '4':
            #                     {
            #                         'coupon_type': 1,
            #                         'coupon_display': '满减券',
            #                         'money_equivalent_value': 60,
            #                         'minimum_consume': 100
            #                     },
            #                 '5':
            #                     {
            #                         'coupon_type': 0,
            #                         'coupon_display': '通用券',
            #                         'money_equivalent_value': 40
            #                     }
            #             },
            #         'period': '720',
            #         'price': '3000.0'
            #
            #     },
            #     {
            #         'course_id': '2',
            #         'title': '金融分析',
            #         'img': 'jinrongfenxi.png',
            #         'policy_id': '4',
            #         'coupon': {},
            #         'default_coupon': '0',
            #         'period': '14',
            #         'period_display': '2周',
            #         'price': '12331.0'
            #
            #     }
            # ]
            course_list = []
            for key in all_key:
                print(key)
                info = {}
                data = self.conn.hgetall(key)
                print(data)
                for k, v in data.items():
                    kk = k.decode('utf-8')
                    if kk == "coupon":
                        info[kk] = json.loads(v.decode('utf-8'))
                    else:
                        info[kk] = v.decode('utf-8')
                course_list.append(info)
            print("course_list:", course_list)
            # 存放使用优惠券id列表
            use_coupon_record_id_list = []
            for i in course_list:
                course_id = i.get('course_id')
                # coupon_id = int(i.get('default_coupon'))
                coupon_id = 1
                course_obj = Course.objects.get(id=course_id)
                use_coupon_record_id_list.append(coupon_id)

                if course_obj.status == 1:
                    res.code = 1041
                    res.error = '课程已经下线'
                    return Response(res.dict)

                if coupon_id != 0:

                    coupon_dict = Coupon.objects.filter(
                        id=coupon_id,
                        couponrecord__account_id=user_id,
                        couponrecord__status=0,
                    ).values("coupon_type", "money_equivalent_value", "minimum_consume", "off_percent")
                    print("coupon_dict:", coupon_dict)
                    if not coupon_dict:
                        res.code = 1042
                        res.error = '优惠券已过期'
                    coupon_dict = coupon_dict[0]

                    print("coupon_dict【0】:", coupon_dict)
                    price = float(i['price'])
                    # print("price:", price)
                    rebate_price = self.rebate(price, coupon_dict)

                    print("使用课程优惠券的rebate_price:", rebate_price)
                    i["rebate_price"] = rebate_price
                    # 此时的course_list结构
                    # {
                    #     'policy_id': '2',
                    #     'img': 'quanzhan.png',
                    #     'period_display': '24个月',
                    #     'coupon':
                    #         {
                    #             '1':
                    #                 {
                    #                     'coupon_type': 1,
                    #                     'coupon_display': '满减券',
                    #                     'money_equivalent_value': 60,
                    #                     'minimum_consume': 100
                    #
                    #                 },
                    #             '4':
                    #                 {
                    #                     'coupon_type': 1,
                    #                     'coupon_display': '满减券',
                    #                     'money_equivalent_value': 60,
                    #                     'minimum_consume': 100
                    #
                    #                 },
                    #             '5':
                    #                 {
                    #                     'coupon_type': 0,
                    #                     'coupon_display': '通用券',
                    #                     'money_equivalent_value': 40
                    #                 }
                    #         },
                    #     'default_coupon': '0',
                    #     'course_id': '1',
                    #     'title': 'Python全栈',
                    #     'period': '720',
                    #     'price': '3000.0',
                    #     'rebate_price': 2940.0
                    #
                    # }

                else:
                    coupon_dict = {}
                    rebate_price = float(i['price'])
                    print("无课程优惠券的rebate_price:", rebate_price)
                    pass
                if rebate_price == -1:
                    res.code = 1043
                    res.error = "优惠券不满足需求"
                    return Response(res.dict)
                # -- 8 得到所有课程折后价格的总和
                course_all_price += rebate_price
            # print("use_coupon_record_id_list:",use_coupon_record_id_list)
            # print("course_all_price:", course_all_price)
            # print("使用优惠券的course_list:",course_list)
            # 全局满减券
            global_coupon_dict = []

            global_coupon_key = settings.PAYMENT_COUPON_KEY % user_id
            # print("global_coupon_key:",global_coupon_key)
            # 2.全局优惠券
            global_coupon_dict = {
                'coupon': json.loads(self.conn.hget(global_coupon_key, 'coupon').decode('utf-8')),
                'default_coupon': self.conn.hget(global_coupon_key, 'default_coupon').decode('utf-8')
            }
            # print("全局优惠券:",global_coupon_dict)
            global_coupon_id = int(self.conn.hget(global_coupon_key, 'default_coupon').decode('utf-8'))

            print("全局优惠券id：", global_coupon_id)
            use_coupon_record_id_list.append(global_coupon_id)
            print("use_coupon_record_id_list", use_coupon_record_id_list)
            # global_coupon_id = 1
            if global_coupon_id != 0:

                # print("global_coupon_dict:", global_coupon_dict)
                # -- 去数据库校验
                global_coupon_dict = Coupon.objects.filter(
                    id=global_coupon_id,
                    couponrecord__account_id=user_id,
                    couponrecord__status=0,
                    valid_begin_date__lte=now(),
                    valid_end_date__gte=now()
                ).values("coupon_type", "money_equivalent_value", "minimum_consume", "off_percent")[0]
                print("global_coupon_dict[0]:", global_coupon_dict)
                # -- 全局优惠券合法 去做计算
                global_rebate_price = self.rebate(course_all_price, global_coupon_dict)
                if global_rebate_price == -1:
                    res.code = 1044
                    res.error = "全局优惠券不满足需求"
                    return Response(res.dict)
                print("global_rebate_price:", global_rebate_price)

            else:
                global_coupon_dict = {}

                global_rebate_price = float(course_all_price)
                print("无全局优惠券价格：", global_rebate_price)

            # 抵扣账号余额 得到最终价格
            if global_rebate_price > balance:
                final_price = global_rebate_price - balance
                user_balance = user_balance - balance
            else:
                final_price = 0
                vir_price = global_rebate_price
                user_balance = user_balance - global_rebate_price
            print('final_price:', final_price)
            # 跟前端传过来的价格做校验
            if final_price != web_price:
                res.code = 1045
                res.error = "价格不合法"
                return Response(res.dict)
            # 创建订单 + 支付宝支付
            # 创建订单详细
            # 账号金额抵扣 + 账号金额记录
            # 优惠券状态更新
            # 当前时间

            current_date = datetime.datetime.now().date()
            current_datetime = datetime.datetime.now()
            actual_amount = 0
            if final_price != 0:
                payment_type = 1  # 支付宝
                actual_amount = final_price
            elif balance:
                payment_type = 3  # 账号余额支付
                actual_amount = global_rebate_price
            else:
                payment_type = 2  # 优惠码
                actual_amount = global_rebate_price
            # 购买课程列表course_list:
            #  course_list:
            # [
            # 	{
            # 		'course_id': '2',
            # 		'title': '金融分析',
            # 		'img': 'jinrongfenxi.png',
            # 		'policy_id': '4',
            # 		'coupon': {},
            # 		'default_coupon': '0',
            # 		'period': '14',
            # 		'period_display': '2周',
            # 		'price': '12331.0'
            #
            # 	},
            # 	{
            # 		'course_id': '1',
            # 		'title': 'Python全栈',
            # 		'period': '720',
            # 		'price': '3000.0'
            # 		'policy_id': '2',
            # 		'img': 'quanzhan.png',
            # 		'period_display': '24个月',
            # 		'default_coupon': '0',
            # 		'coupon':
            # 		{
            # 			'1':
            # 			{
            # 				'coupon_type': 1,
            # 				'coupon_display': '满减券',
            # 				'money_equivalent_value': 60,
            # 				'minimum_consume': 100
            #
            # 			},
            # 			'4':
            # 			{
            # 				'coupon_type': 1,
            # 				'coupon_display': '满减券',
            # 				'money_equivalent_value': 60,
            # 				'minimum_consume': 100
            #
            # 			},
            # 			'5':
            # 			{
            # 				'coupon_type': 0,
            # 				'coupon_display': '通用券',
            # 				'money_equivalent_value': 40
            # 			}
            # 		},
            #
            #
            #
            # 	}
            # ]
            print("payment_type", payment_type)
            with transaction.atomic():
                order_num = generate_order_num()
                print(order_num)
                if payment_type == 1:
                    order_object = models.Order.objects.create(
                        payment_type=payment_type,
                        order_number=order_num,
                        account=user_id,
                        actual_amount=actual_amount,
                        status=1,  # 待支付
                    )

                else:
                    order_object = models.Order.objects.create(
                        payment_type=payment_type,
                        order_number=order_num,
                        account=request.user,
                        actual_amount=actual_amount,
                        status=0,  # 支付成功，优惠券和贝里已够支付
                        pay_time=current_datetime
                    )

                for item in course_list:
                    detail = models.OrderDetail.objects.create(
                        order=order_object,
                        content_object=models.Course.objects.get(id=item['course_id']),
                        original_price=item['price'],
                        price=item['rebate_price'],
                        valid_period_display=item['period_display'],
                        valid_period=item['period']
                    )
                user_balance = models.Account.objects.filter(id=user_id).update(balance=user_balance)
                models.TransactionRecord.objects.create(
                    account=user_id,
                    amount=actual_amount,
                    transaction_type=1,
                    content_object=order_object,
                    transaction_number=generate_transaction_num()
                )
                effect_row = models.CouponRecord.objects.filter(id__in=use_coupon_record_id_list).update(
                    order=order_object,
                    used_time=current_datetime)
                if effect_row != len(use_coupon_record_id_list):
                    raise Exception('优惠券使用失败')

                res.data = {
                    'payment_type': payment_type
                }
                # 生成支付宝URL地址
                if payment_type == 1:
                    pay = AliPay()
                    query_params = pay.direct_pay(
                        subject="Twiss",  # 商品简单描述
                        out_trade_no=order_num,  # 商户订单号
                        total_amount=actual_amount,  # 交易金额(单位: 元 保留俩位小数)
                    )
                    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)

                    res.data = {
                        'pay_url': pay_url
                    }


        except Exception as e:
            res.code = 1002
            res.error = "支付失败"
        return Response(res.dict)

    def rebate(self, price, coupon_dict):
        coupon_type = coupon_dict.get('coupon_type', '')
        if coupon_type == 0:  # 通用优惠券
            rebate_price = price - int(coupon_dict['money_equivalent_value'])
            if rebate_price < 0:
                rebate_price = 0
        elif coupon_type == 1:
            # 满减型优惠券
            rebate_price = price - int(coupon_dict['money_equivalent_value'])
            # if price<coupon_dict['minimum_consume']:
            #     rebate_price=-1
        else:  # 折扣型
            rebate_price = price * int(coupon_dict['off_percent']) / 100
            if price < coupon_dict['minimum_consume']:
                rebate_price = -1
        return rebate_price

