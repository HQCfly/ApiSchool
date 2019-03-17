import redis
import json

conn = redis.Redis(host='127.0.0.1',port=6379,password='')
# conn.flushall()

from django.core.cache import cache
print(conn.keys())
# print(conn.hgetall('shopping_car_1_1'))