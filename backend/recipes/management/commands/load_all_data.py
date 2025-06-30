import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.management.commands.load_ingrs import Command as LoadIngrs
from recipes.management.commands.load_tags import Command as LoadTags


class Command(BaseCommand):
    help = 'Загрузка всех данных из фикстур.'

    def handle(self, *args, **options):
        media_dir = os.path.join(settings.MEDIA_ROOT)
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
            self.stdout.write(
                f'Создана папка media: {media_dir}'
            )

        recipes_media_dir = os.path.join(media_dir, 'recipes')
        if not os.path.exists(recipes_media_dir):
            os.makedirs(recipes_media_dir)
            self.stdout.write(
                f'Создана папка для рецептов: {recipes_media_dir}'
            )

        avatars_media_dir = os.path.join(media_dir, 'avatars')
        if not os.path.exists(avatars_media_dir):
            os.makedirs(avatars_media_dir)
            self.stdout.write(
                f'Создана папка для аватаров: {avatars_media_dir}'
            )

        self.stdout.write(
            self.style.SUCCESS('Загрузка ингредиентов...')
        )
        LoadIngrs().handle()
        LoadTags().handle()
        self.stdout.write(self.style.SUCCESS('Готово!'))
