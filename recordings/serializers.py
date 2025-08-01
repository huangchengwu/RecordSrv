from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers

class RecordingSerializer(ModelSerializer):
    class Meta:
        model = Recording
        fields = '__all__'


