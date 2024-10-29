from django.core.management.base import BaseCommand
from courses.models import Category
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Creates initial course categories'

    def handle(self, *args, **kwargs):
        categories = [
            'Programming',
            'Web Development',
            'Mobile Development',
            'Data Science',
            'Machine Learning',
            'DevOps',
            'Database',
            'Cloud Computing'
        ]

        for cat_name in categories:
            try:
                category, created = Category.objects.get_or_create(name=cat_name)
                status = "Created" if created else "Already exists"
                self.stdout.write(self.style.SUCCESS(f'{status}: "{cat_name}"'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Error creating "{cat_name}": {str(e)}'))
