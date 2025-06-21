from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

User = get_user_model()

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
        tags_data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'dinner'},
        ]
        
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
            if created:
                self.stdout.write(f'Создан тег: {tag.name}')
        
        # Загружаем ингредиенты
        ingredients_data = [
            {'name': 'Молоко', 'measurement_unit': 'мл'},
            {'name': 'Сахар', 'measurement_unit': 'г'},
            {'name': 'Яйцо', 'measurement_unit': 'шт'},
            {'name': 'Соль', 'measurement_unit': 'г'},
            {'name': 'Мука', 'measurement_unit': 'г'},
            {'name': 'Масло сливочное', 'measurement_unit': 'г'},
            {'name': 'Томаты', 'measurement_unit': 'шт'},
            {'name': 'Лук', 'measurement_unit': 'шт'},
            {'name': 'Чеснок', 'measurement_unit': 'зубчик'},
            {'name': 'Перец черный', 'measurement_unit': 'г'},
        ]
        
        for ingr_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingr_data['name'],
                measurement_unit=ingr_data['measurement_unit'],
                defaults=ingr_data
            )
            if created:
                self.stdout.write(f'Создан ингредиент: {ingredient.name}')
        
        # Создаём тестового пользователя если его нет
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('Создан тестовый пользователь: testuser (пароль: testpass123)')
        
        # Создаём тестовый рецепт
        tag = Tag.objects.first()
        ingredient = Ingredient.objects.first()
        
        if tag and ingredient:
            recipe, created = Recipe.objects.get_or_create(
                author=test_user,
                name='Тестовый рецепт',
                defaults={
                    'text': 'Это тестовый рецепт для проверки работы сайта.',
                    'cooking_time': 30,
                }
            )
            
            if created:
                recipe.tags.add(tag)
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=100
                )
                self.stdout.write('Создан тестовый рецепт')
        
        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены!')) 