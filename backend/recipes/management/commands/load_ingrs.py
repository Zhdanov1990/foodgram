import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = (
        'Загружает ингредиенты из файлов '
        'data/ingredients.json и data/ingredients.csv'
    )

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        created_count = 0

        # Загрузка из JSON
        json_file = os.path.join(data_dir, 'ingredients.json')
        if os.path.exists(json_file):
            self.stdout.write(f'Загружаем ингредиенты из {json_file}...')
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    ingredients_data = json.load(f)

                self.stdout.write(
                    f'Найдено {len(ingredients_data)} '
                    'ингредиентов в JSON-файле'
                )

                try:
                    for item in ingredients_data:
                        ingredient, created = Ingredient.objects.get_or_create(
                            name=item['name'],
                            measurement_unit=item['measurement_unit'],
                            defaults=item
                        )
                        if created:
                            created_count += 1

                    self.stdout.write(
                        f'Из JSON-файла создано '
                        f'{created_count} новых ингредиентов'
                    )
                except Exception as err:
                    self.stdout.write(
                        f'Ошибка при работе с базой данных: {err}'
                    )
                    self.stdout.write(
                        'Файл JSON читается корректно, '
                        'но база данных недоступна'
                    )

            except Exception as err:
                self.stdout.write(
                    f'Ошибка при чтении JSON-файла: {err}'
                )
        else:
            self.stdout.write(f'Файл {json_file} не найден')

        # Загрузка из CSV
        csv_file = os.path.join(data_dir, 'ingredients.csv')
        if os.path.exists(csv_file):
            self.stdout.write(f'Загружаем ингредиенты из {csv_file}...')
            try:
                csv_created = 0
                csv_total = 0

                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        csv_total += 1
                        if len(row) < 2:
                            continue

                        name = row[0].strip()
                        unit = row[1].strip()

                        try:
                            _, created = Ingredient.objects.get_or_create(
                                name=name,
                                measurement_unit=unit,
                                defaults={
                                    'name': name,
                                    'measurement_unit': unit,
                                }
                            )
                            if created:
                                csv_created += 1
                        except Exception:
                            continue

                self.stdout.write(
                    f'Найдено {csv_total} '
                    'строк в CSV-файле'
                )
                self.stdout.write(
                    f'Из CSV-файла создано '
                    f'{csv_created} новых ингредиентов'
                )
                created_count += csv_created

            except Exception as err:
                self.stdout.write(
                    f'Ошибка при чтении CSV-файла: {err}'
                )
        else:
            self.stdout.write(f'Файл {csv_file} не найден')

        # Итоговый отчёт
        try:
            total = Ingredient.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загрузка завершена! '
                    f'Создано новых ингредиентов: {created_count}, '
                    f'всего в базе: {total}'
                )
            )
        except Exception:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Файлы прочитаны успешно! '
                    f'Создано новых ингредиентов: {created_count}'
                )
            )
