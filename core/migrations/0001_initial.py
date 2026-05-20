# Generated manually for the Barangay San Isidro Information Management System.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("event", "Event"),
                            ("emergency", "Emergency"),
                            ("meeting", "Barangay Meeting"),
                            ("program", "Program"),
                        ],
                        max_length=30,
                    ),
                ),
                ("message", models.TextField()),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                ("is_published", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_name", models.CharField(max_length=150)),
                ("action", models.CharField(max_length=255)),
                ("record_name", models.CharField(blank=True, max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Household",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("house_number", models.CharField(max_length=50, unique=True)),
                ("purok", models.CharField(max_length=80)),
                ("family_head", models.CharField(max_length=150)),
                ("address", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "rating",
                    models.CharField(
                        choices=[("excellent", "Excellent"), ("good", "Good"), ("poor", "Poor")],
                        max_length=20,
                    ),
                ),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Resident",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=80)),
                ("middle_name", models.CharField(blank=True, max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("birthdate", models.DateField()),
                ("address", models.CharField(max_length=255)),
                ("purok", models.CharField(max_length=80)),
                (
                    "civil_status",
                    models.CharField(
                        choices=[
                            ("single", "Single"),
                            ("married", "Married"),
                            ("widowed", "Widowed"),
                            ("separated", "Separated"),
                        ],
                        max_length=20,
                    ),
                ),
                ("occupation", models.CharField(blank=True, max_length=120)),
                ("contact_number", models.CharField(blank=True, max_length=30)),
                ("is_male", models.BooleanField(default=True)),
                ("is_senior_citizen", models.BooleanField(default=False)),
                ("is_pwd", models.BooleanField(default=False)),
                ("is_registered_voter", models.BooleanField(default=False)),
                ("photo", models.FileField(blank=True, null=True, upload_to="resident_photos/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "household",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="members",
                        to="core.household",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Complaint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("incident_location", models.CharField(max_length=180)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "Submitted"),
                            ("review", "Under review"),
                            ("hearing", "Scheduled hearing"),
                            ("resolved", "Resolved"),
                        ],
                        default="submitted",
                        max_length=20,
                    ),
                ),
                ("hearing_date", models.DateTimeField(blank=True, null=True)),
                ("evidence", models.FileField(blank=True, null=True, upload_to="complaint_evidence/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "complainant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="complaints",
                        to="core.resident",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CertificateRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("clearance", "Barangay Clearance"),
                            ("residency", "Certificate of Residency"),
                            ("indigency", "Indigency Certificate"),
                        ],
                        max_length=30,
                    ),
                ),
                ("purpose", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("ready", "Ready to claim"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("remarks", models.CharField(blank=True, max_length=255)),
                ("digital_signature", models.FileField(blank=True, null=True, upload_to="signatures/")),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "resident",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificate_requests",
                        to="core.resident",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="feedback",
            name="resident",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.resident"),
        ),
    ]
