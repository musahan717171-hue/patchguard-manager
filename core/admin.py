from django.contrib import admin
from .models import Asset, AssessmentReport, PatchAssessment


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "asset_type",
        "software_name",
        "current_version",
        "latest_version",
        "patch_status",
        "criticality",
        "last_update",
    )
    search_fields = ("name", "software_name", "operating_system")
    list_filter = ("asset_type", "patch_status", "criticality")


@admin.register(PatchAssessment)
class PatchAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "total_assets",
        "patched_assets",
        "outdated_assets",
        "missing_patch_assets",
        "critical_assets",
        "compliance_percentage",
        "risk_score",
        "risk_level",
    )


@admin.register(AssessmentReport)
class AssessmentReportAdmin(admin.ModelAdmin):
    list_display = ("created_at", "assessment")
    search_fields = ("report_text", "recommendations")
