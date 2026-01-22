from rest_framework import serializers
from django.utils import timezone
from .models import Task,Notification

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'status', 'deadline', 'is_recurring', 'recurrence_interval', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("The deadline cannot be in the past.")
        return value


    def validate(self, data):
        if data.get('is_recurring') and not data.get('recurrence_interval'):
            raise serializers.ValidationError({
                "recurrence_interval": "This field is required if 'is_recurring' is True."
            })
        return data
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']