from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загружает стандартные теги (завтрак, обед, ужин)'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'dinner'},
            {'name': 'Напитки', 'color': '#FF6B6B', 'slug': 'drinks'},
            {'name': 'Закуски', 'color': '#4ECDC4', 'slug': 'appetizers'},
            {'name': 'Мороженое', 'color': '#45B7D1', 'slug': 'ice-cream'},
            {'name': 'Сладости', 'color': '#FFA07A', 'slug': 'desserts'},
        ]
        Tag.objects.bulk_create(
            [Tag(**tag) for tag in data],
            ignore_conflicts=True
        )
        self.stdout.write(self.style.SUCCESS('Теги успешно загружены.'))
