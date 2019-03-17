from django.test import TestCase
from api import models
# Create your tests here.
def test(request):
    obj = models.Course.objects.filter(pk=1).first()
    print(obj)