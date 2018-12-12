from rest_framework import serializers
from project.api.models import ApprovedImage
import re


class ApprovedImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApprovedImage
        fields = ['id', 'url']
