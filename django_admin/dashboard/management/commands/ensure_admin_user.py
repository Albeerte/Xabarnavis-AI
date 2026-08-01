from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a local Django admin superuser."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@xabarnavis.local")
        parser.add_argument("--password", default="admin12345")

    def handle(self, *args, **options) -> None:
        user_model = get_user_model()
        username = options["username"]
        email = options["email"]
        password = options["password"]
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} Django admin user: {username}"))
