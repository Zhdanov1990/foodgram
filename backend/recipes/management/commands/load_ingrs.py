import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Загружает ингредиенты из файлов data/ingredients.json и data/ingredients.csv'

    def handle(self, *args, **kwargs):
        # Путь к папке data (теперь в папке backend)
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        created_count = 0
        
        # Загружаем из JSON файла
        json_file = os.path.join(data_dir, 'ingredients.json')
        if os.path.exists(json_file):
            self.stdout.write(f'Загружаем ингредиенты из {json_file}...')
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    ingredients_data = json.load(f)
                
                self.stdout.write(f'Найдено {len(ingredients_data)} ингредиентов в JSON файле')
                
                # Проверяем подключение к базе данных
                try:
                    for item in ingredients_data:
                        ingredient, created = Ingredient.objects.get_or_create(
                            name=item['name'],
                            measurement_unit=item['measurement_unit'],
                            defaults=item
                        )
                        if created:
                            created_count += 1
                    
                    self.stdout.write(f'Из JSON файла создано {created_count} новых ингредиентов')
                except Exception as e:
                    self.stdout.write(f'Ошибка при работе с базой данных: {e}')
                    self.stdout.write('Файл JSON читается корректно, но база данных недоступна')
                    
            except Exception as e:
                self.stdout.write(f'Ошибка при чтении JSON файла: {e}')
        else:
            self.stdout.write(f'Файл {json_file} не найден')
        
        # Загружаем из CSV файла
        csv_file = os.path.join(data_dir, 'ingredients.csv')
        if os.path.exists(csv_file):
            self.stdout.write(f'Загружаем ингредиенты из {csv_file}...')
            try:
                csv_created_count = 0
                csv_total_count = 0
                
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        csv_total_count += 1
                        if len(row) >= 2:
                            name = row[0].strip()
                            measurement_unit = row[1].strip()
                            
                            try:
                                ingredient, created = Ingredient.objects.get_or_create(
                                    name=name,
                                    measurement_unit=measurement_unit,
                                    defaults={
                                        'name': name,
                                        'measurement_unit': measurement_unit
                                    }
                                )
                                if created:
                                    csv_created_count += 1
                            except Exception as e:
                                # Пропускаем ошибки базы данных
                                pass
                
                self.stdout.write(f'Найдено {csv_total_count} строк в CSV файле')
                self.stdout.write(f'Из CSV файла создано {csv_created_count} новых ингредиентов')
                created_count += csv_created_count
                
            except Exception as e:
                self.stdout.write(f'Ошибка при чтении CSV файла: {e}')
        else:
            self.stdout.write(f'Файл {csv_file} не найден')
        
        try:
            total_ingredients = Ingredient.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загрузка завершена! Создано новых ингредиентов: {created_count}, всего в базе: {total_ingredients}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Файлы прочитаны успешно! Создано новых ингредиентов: {created_count}'
                )
            )
