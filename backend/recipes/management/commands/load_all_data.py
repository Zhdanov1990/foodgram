from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Загружает все необходимые данные: теги, ингредиенты и тестовые данные'

    def handle(self, *args, **options):
        # Создаём папку media если её нет
        media_dir = os.path.join(settings.MEDIA_ROOT)
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            self.stdout.write(f'Создана папка media: {media_dir}')
        
        # Создаём папку для рецептов
        recipes_media_dir = os.path.join(media_dir, 'recipes')
        if not os.path.exists(recipes_media_dir):
            os.makedirs(recipes_media_dir)
            self.stdout.write(f'Создана папка для рецептов: {recipes_media_dir}')
        
        # Загружаем теги
        self.stdout.write('Загружаем теги...')
        call_command('load_tags')
        
        # Загружаем ингредиенты
        self.stdout.write('Загружаем ингредиенты...')
        call_command('load_ingrs')
        
        # Загружаем тестовые данные
        self.stdout.write('Загружаем тестовые данные...')
        call_command('load_test_data')
        
        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены!')) 