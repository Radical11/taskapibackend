from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from api.models import Task, Notification # <--- Added Notification import
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process recurring tasks and send reminders safely'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Daily Job...")
        now = timezone.now()
        
        try:
            with transaction.atomic():
                # --- PART 1: Recurring Tasks ---
                recurring_tasks = Task.objects.select_related('owner').filter(
                    is_recurring=True, 
                    status='Completed'
                )
                
                tasks_created = 0
                for task in recurring_tasks:
                    duplicate_exists = Task.objects.filter(
                        title=task.title, 
                        owner=task.owner,
                        created_at__date=now.date()
                    ).exists()

                    if not duplicate_exists:
                        days_to_add = 7 if task.recurrence_interval == 'Weekly' else 1
                        
                        Task.objects.create(
                            title=task.title,
                            description=task.description,
                            priority=task.priority,
                            owner=task.owner,
                            deadline=now + timedelta(days=days_to_add),
                            status='Pending',
                            is_recurring=True,
                            recurrence_interval=task.recurrence_interval
                        )
                        tasks_created += 1

                self.stdout.write(self.style.SUCCESS(f"Successfully generated {tasks_created} new tasks."))

                overdue_tasks = Task.objects.select_related('owner').filter(
                    deadline__lt=now, 
                    status__in=['Pending', 'In Progress']
                )
                
                alerts_created = 0
                for task in overdue_tasks:
                    msg = f"Overdue: '{task.title}' was due on {task.deadline.strftime('%Y-%m-%d')}"
                    
                    already_notified = Notification.objects.filter(
                        user=task.owner,
                        message=msg,
                        created_at__date=now.date()
                    ).exists()
                    
                    if not already_notified:
                        Notification.objects.create(user=task.owner, message=msg)
                        alerts_created += 1
                        self.stdout.write(f"Alert generated for {task.title}")

                self.stdout.write(self.style.SUCCESS(f"Done. Generated {alerts_created} in-app notifications."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Job Failed: {str(e)}"))

        self.stdout.write("Job Complete.")