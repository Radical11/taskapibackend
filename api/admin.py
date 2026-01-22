from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'owner', 
        'status', 
        'priority', 
        'deadline', 
        'is_recurring'
    )

    list_filter = ('status', 'priority', 'is_recurring', 'recurrence_interval')


    search_fields = ('title', 'description', 'owner__username')

    readonly_fields = ('created_at',)


    ordering = ('deadline',)

    list_per_page = 20