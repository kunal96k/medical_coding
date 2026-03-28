import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Question   # ✅ make sure your app is called 'main'

class Command(BaseCommand):
    help = "Import questions from a CSV file into the Question model"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the CSV file',
            default=os.path.join(settings.BASE_DIR, 'fixtures', 'ICD PART A.csv')  # default path
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        with open(file_path, newline='', encoding='utf-8-sig', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)

            count = 0
            for row in reader:
                Question.objects.create(
                    question_text=row['question'],
                    option1=row['option1'],
                    option2=row['option2'],
                    option3=row['option3'],
                    option4=row['option4'],
                    correct_answer=row['correct_answer']
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {count} questions"))
