# Generated manually for PatchGuard Manager deployment.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("asset_type", models.CharField(choices=[("Server", "Server"), ("Workstation", "Workstation"), ("Network Device", "Network Device"), ("Database", "Database"), ("Web Application", "Web Application"), ("Security Tool", "Security Tool")], max_length=40)),
                ("operating_system", models.CharField(max_length=120)),
                ("software_name", models.CharField(max_length=120)),
                ("current_version", models.CharField(max_length=40)),
                ("latest_version", models.CharField(max_length=40)),
                ("patch_status", models.CharField(choices=[("Patched", "Patched"), ("Outdated", "Outdated"), ("Missing Patch", "Missing Patch"), ("Unknown", "Unknown")], default="Unknown", max_length=30)),
                ("criticality", models.CharField(choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Critical", "Critical")], default="Medium", max_length=20)),
                ("last_update", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-updated_at", "name"]},
        ),
        migrations.CreateModel(
            name="PatchAssessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_assets", models.PositiveIntegerField(default=0)),
                ("patched_assets", models.PositiveIntegerField(default=0)),
                ("outdated_assets", models.PositiveIntegerField(default=0)),
                ("missing_patch_assets", models.PositiveIntegerField(default=0)),
                ("critical_assets", models.PositiveIntegerField(default=0)),
                ("compliance_percentage", models.FloatField(default=0)),
                ("risk_score", models.PositiveIntegerField(default=0)),
                ("risk_level", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AssessmentReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("report_text", models.TextField()),
                ("recommendations", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="core.patchassessment")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
