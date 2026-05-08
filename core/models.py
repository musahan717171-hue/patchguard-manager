from django.db import models


class Asset(models.Model):
    class AssetType(models.TextChoices):
        SERVER = "Server", "Server"
        WORKSTATION = "Workstation", "Workstation"
        NETWORK_DEVICE = "Network Device", "Network Device"
        DATABASE = "Database", "Database"
        WEB_APPLICATION = "Web Application", "Web Application"
        SECURITY_TOOL = "Security Tool", "Security Tool"

    class PatchStatus(models.TextChoices):
        PATCHED = "Patched", "Patched"
        OUTDATED = "Outdated", "Outdated"
        MISSING_PATCH = "Missing Patch", "Missing Patch"
        UNKNOWN = "Unknown", "Unknown"

    class Criticality(models.TextChoices):
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"
        CRITICAL = "Critical", "Critical"

    name = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=40, choices=AssetType.choices)
    operating_system = models.CharField(max_length=120)
    software_name = models.CharField(max_length=120)
    current_version = models.CharField(max_length=40)
    latest_version = models.CharField(max_length=40)
    patch_status = models.CharField(max_length=30, choices=PatchStatus.choices, default=PatchStatus.UNKNOWN)
    criticality = models.CharField(max_length=20, choices=Criticality.choices, default=Criticality.MEDIUM)
    last_update = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "name"]

    def __str__(self):
        return f"{self.name} - {self.software_name}"


class PatchAssessment(models.Model):
    total_assets = models.PositiveIntegerField(default=0)
    patched_assets = models.PositiveIntegerField(default=0)
    outdated_assets = models.PositiveIntegerField(default=0)
    missing_patch_assets = models.PositiveIntegerField(default=0)
    critical_assets = models.PositiveIntegerField(default=0)
    compliance_percentage = models.FloatField(default=0)
    risk_score = models.PositiveIntegerField(default=0)
    risk_level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} - {self.risk_level} ({self.risk_score})"


class AssessmentReport(models.Model):
    assessment = models.ForeignKey(PatchAssessment, on_delete=models.CASCADE, related_name="reports")
    report_text = models.TextField()
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.created_at:%Y-%m-%d %H:%M}"
