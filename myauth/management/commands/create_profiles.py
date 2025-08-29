from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myauth.models import Profile


class Command(BaseCommand):
    help = 'Создаёт профили для всех пользователей, у которых их нет'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0

        for user in users_without_profile:
            Profile.objects.create(user=user)
            created_count += 1
            self.stdout.write(f'Создан профиль для пользователя {user.username}')

        if created_count:
            self.stdout.write(
                self.style.SUCCESS(f'Успешно создано {created_count} профилей')
            )
        else:
            self.stdout.write('Все пользователи уже имеют профили')