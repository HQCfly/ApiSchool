import uuid
from django.shortcuts import render, redirect, HttpResponse

from ApiSchool import settings
from utils.pay import AliPay
from api import models

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


def ordercheck(request):
    """POST请求,支付宝通知支付信息,我们修改订单状态"""
    if request.method == "POST":
        alipay = AliPay()
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        if status:
            # 支付成功, 获取订单号将订单状态更新
            out_trade_no = post_dict['out_trade_no']
            models.Order.objects.filter(no=out_trade_no).update(status=2)
            return HttpResponse('success')
        else:
            return HttpResponse('支付失败')
    else:
        return HttpResponse('只支持POST请求')


def ordershow(request):
    """回到我们的页面"""
    if request.method == "GET":
        alipay = AliPay()
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        if status:
            return HttpResponse('支付成功')
        else:
            return HttpResponse('支付失败')
    else:
        return HttpResponse("只支持GET请求")

