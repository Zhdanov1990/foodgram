#recipes/management/commands/load_ingrs.py
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Загружает стандартные ингредиенты'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Молоко', 'measurement_unit': 'мл'},
            {'name': 'Сахар', 'measurement_unit': 'г'},
            {'name': 'Яйцо', 'measurement_unit': 'шт'},
            {'name': 'Соль', 'measurement_unit': 'г'},
            {'name': 'Мука', 'measurement_unit': 'г'},
        ]
        Ingredient.objects.bulk_create(
            [Ingredient(**item) for item in data],
            ignore_conflicts=True
        )
        self.stdout.write(self.style.SUCCESS('Ингредиенты успешно загружены.'))
