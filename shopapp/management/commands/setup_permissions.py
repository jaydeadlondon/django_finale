from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from shopapp.models import Product


class Command(BaseCommand):
    help = 'Настройка прав доступа для пользователей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Имя пользователя для назначения прав'
        )

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            try:
                user = User.objects.get(username=username)
                self.setup_user_permissions(user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Пользователь {username} не найден')
                )
        else:
            self.stdout.write('Настройка прав для всех пользователей...')
            for user in User.objects.all():
                if not user.is_superuser:
                    self.setup_user_permissions(user)

    def setup_user_permissions(self, user):
        """Настройка базовых прав для пользователя"""
        content_type = ContentType.objects.get_for_model(Product)

        add_permission = Permission.objects.get(
            codename='add_product',
            content_type=content_type,
        )
        change_permission = Permission.objects.get(
            codename='change_product',
            content_type=content_type,
        )

        user.user_permissions.add(add_permission)

        if user.created_products.exists():
            user.user_permissions.add(change_permission)

        self.stdout.write(
            self.style.SUCCESS(f'Права настроены для пользователя {user.username}')
        )