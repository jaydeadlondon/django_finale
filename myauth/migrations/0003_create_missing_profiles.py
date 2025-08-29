from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('myauth', 'Profile')

    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('myauth', '0002_alter_profile_avatar'),
    ]

    operations = [
        migrations.RunPython(create_profiles, reverse_func),
    ]