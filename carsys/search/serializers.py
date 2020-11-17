"""
自定义序列化器（把模型对象处理成字典）
"""
from rest_framework import serializers

from search.models import Record, Car


class CarSerializer(serializers.ModelSerializer):
    """车序列化器"""
    class Meta:
        model = Car
        fields =  ('carno', 'owner')

class RecordSerializer(serializers.ModelSerializer):
    """违章记录序列化器"""
    car = serializers.SerializerMethodField()

    @staticmethod
    def get_car(record):
        return CarSerializer(record.car).data

    class Meta:
        model = Record
        # 指定需要序列化所有字段
        # fields = '__all__'
        # 通过元组指定需要序列化的字典
        # fields = ('no', 'reason', 'punish', 'makedate', 'dealt', 'car')
        # 通过元组指定不需要序列化的字段
        exclude = ('is_deleted', 'deleted_time', 'updated_time')
