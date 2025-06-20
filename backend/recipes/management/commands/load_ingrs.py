#recipes/management/commands/load_ingrs.py
import json
import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Загружает ингредиенты из файлов data/ingredients.json или data/ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            choices=['json', 'csv', 'default'],
            default='json',
            help='Тип файла для загрузки: json, csv или default (базовые ингредиенты)'
        )

    def handle(self, *args, **options):
        file_type = options['file']
        
        if file_type == 'default':
            # Загружаем базовые ингредиенты
            data = [
                {'name': 'Молоко', 'measurement_unit': 'мл'},
                {'name': 'Сахар', 'measurement_unit': 'г'},
                {'name': 'Яйцо', 'measurement_unit': 'шт'},
                {'name': 'Соль', 'measurement_unit': 'г'},
                {'name': 'Мука', 'measurement_unit': 'г'},
            ]
            self._load_from_data(data)
            
        elif file_type == 'json':
            # Загружаем из JSON файла
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'ingredients.json')
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    self._load_from_data(data)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка при загрузке JSON: {e}'))
            else:
                self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден!'))
                
        elif file_type == 'csv':
            # Загружаем из CSV файла
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'ingredients.csv')
            if os.path.exists(file_path):
                try:
                    data = []
                    with open(file_path, 'r', encoding='utf-8') as file:
                        csv_reader = csv.reader(file)
                        for row in csv_reader:
                            if len(row) >= 2:
                                name = row[0].strip()
                                measurement_unit = row[1].strip()
                                if name and measurement_unit:
                                    data.append({
                                        'name': name,
                                        'measurement_unit': measurement_unit
                                    })
                    self._load_from_data(data)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка при загрузке CSV: {e}'))
            else:
                self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден!'))

    def _load_from_data(self, data):
        """Загружает ингредиенты из списка данных"""
        created_count = 0
        for item in data:
            _, created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit'],
                defaults=item
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно загружено {created_count} новых ингредиентов из {len(data)} записей.'
            )
        )
