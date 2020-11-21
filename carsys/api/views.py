import os
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from search.models import Record, Car
from search.serializers import RecordSerializer, CarDetailSerializer

# 如果要设计只读的设计接口设计为ReadOnlyModelViewSet
class CarViewSet(ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer


# FBV - 基于函数的视图 - 最灵活高度定制
# CBV - 基于类的视图 - 代码及其简单
@api_view(('GET',))
@cache_page(timeout=60)
def search(request: HttpRequest) -> HttpResponse:
    queryset = Record.objects.filter(is_deleted=False) \
        .defer('is_deleted', 'deleted_time', 'updated_time') \
        .select_related('car').order_by('-makedate')
    carinfo = request.GET.get('carinfo', '')
    if carinfo:
        queryset = queryset.filter(
            Q(car__carno__startswith=carinfo) | Q(car__owner__contains=carinfo)
        )
    serl = RecordSerializer(queryset, many=True)  # 返回数组对象
    return Response({'records': serl.data})
