from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

User = get_user_model()

class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей и по одному рецепту для каждого'

    def handle(self, *args, **options):
        # Создаём двух пользователей
        users = []
        for username in ('alice', 'bob'):
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            user.set_password('password123')
            user.save()
            users.append(user)

        # Берём первый тег и первый ингредиент из БД
        tag = Tag.objects.first()
        ingr = Ingredient.objects.first()
        if not tag or not ingr:
            self.stdout.write(self.style.ERROR(
                'Требуется предварительно загрузить теги и ингредиенты'
            ))
            return

        # Создаём по рецепту на каждого
        for user in users:
            recipe, _ = Recipe.objects.get_or_create(
                author=user,
                name=f'{user.username}\'s Recipe',
                defaults={
                    'text': 'Тестовое описание блюда.',
                    'cooking_time': 15,
                    'image': 'recipes/images/default.jpg'
                }
            )
            recipe.tags.set([tag])
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingr,
                defaults={'amount': 100}
            )

        self.stdout.write(self.style.SUCCESS(
            f'Создано пользователей: {len(users)}, рецептов: {len(users)}'
        ))
