import re

from rest_framework import generics, permissions

from project.api import serializers
from project.api.models import ApprovedImage


class ApprovedImages(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(), )
        return list()

    def get_serializer_class(self):
        return serializers.ApprovedImageSerializer

    def get_queryset(self):
        result = ApprovedImage.objects.all()
        return result

    def perform_create(self, serializer):
        clean_url = re.match('^https:\/\/(www\.)?instagram.com\/p\/.+\/', serializer.validated_data['url']).group(0).replace('https://www.', 'https://') + 'media/?size=l'
        if not ApprovedImage.objects.filter(url=clean_url).exists():
            serializer.save(url=clean_url)
