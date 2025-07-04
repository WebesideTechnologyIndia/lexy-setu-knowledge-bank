# serializers.py
from rest_framework import serializers
from .models import Notification, NotificationCategory

class NotificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCategory
        fields = ['id', 'name', 'description']

class NotificationSerializer(serializers.ModelSerializer):
    category = NotificationCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'category', 'category_id', 
            'created_at', 'updated_at', 'is_active', 'priority'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'content', 'category', 'priority']