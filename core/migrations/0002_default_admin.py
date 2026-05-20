from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@sanisidro.gov.ph",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "password": make_password("Admin@12345"),
        },
    )
    if not created:
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.password = make_password("Admin@12345")
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_default_admin, migrations.RunPython.noop),
    ]
