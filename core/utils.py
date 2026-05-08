from datetime import date
from io import BytesIO
import os
import re

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from locale_or_translations.translations import get_translations
from .models import Asset, AssessmentReport, PatchAssessment

SUPPORTED_LANGUAGES = ("en", "ru", "tk")

CRITICALITY_WEIGHT = {
    "Low": 0.65,
    "Medium": 1.0,
    "High": 1.3,
    "Critical": 1.65,
}

STATUS_BASE_RISK = {
    "Patched": 8,
    "Outdated": 46,
    "Missing Patch": 62,
    "Unknown": 38,
}

ASSET_TYPE_WEIGHT = {
    "Server": 10,
    "Database": 12,
    "Web Application": 11,
    "Network Device": 9,
    "Security Tool": 8,
    "Workstation": 4,
}

DEMO_ASSETS = [
    {
        "name": "Main Web Server",
        "asset_type": "Server",
        "operating_system": "Ubuntu 20.04",
        "software_name": "Apache",
        "current_version": "2.4.49",
        "latest_version": "2.4.58",
        "patch_status": "Outdated",
        "criticality": "Critical",
        "notes": "Public-facing service used for coursework demonstration.",
    },
    {
        "name": "Database Server",
        "asset_type": "Database",
        "operating_system": "Windows Server 2019",
        "software_name": "MySQL",
        "current_version": "8.0.21",
        "latest_version": "8.0.36",
        "patch_status": "Outdated",
        "criticality": "High",
        "notes": "Stores important infrastructure records.",
    },
    {
        "name": "Office Computer 01",
        "asset_type": "Workstation",
        "operating_system": "Windows 10",
        "software_name": "Google Chrome",
        "current_version": "120",
        "latest_version": "125",
        "patch_status": "Missing Patch",
        "criticality": "Medium",
        "notes": "Employee endpoint with browser security updates required.",
    },
    {
        "name": "Backup Server",
        "asset_type": "Server",
        "operating_system": "Debian 12",
        "software_name": "OpenSSH",
        "current_version": "9.6",
        "latest_version": "9.6",
        "patch_status": "Patched",
        "criticality": "High",
        "notes": "Backup access service is currently patched.",
    },
]


def get_language(request):
    language = request.GET.get("lang") or request.session.get("language") or request.COOKIES.get("patchguard_language") or "en"
    return language if language in SUPPORTED_LANGUAGES else "en"


def get_ui_context(request):
    lang = get_language(request)
    return {"tr": get_translations(lang), "lang": lang, "supported_languages": SUPPORTED_LANGUAGES}


def ensure_demo_user():
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(username="admin", email="admin@example.local", password="admin12345")


def create_demo_data():
    if Asset.objects.exists():
        return
    today = date.today()
    for asset in DEMO_ASSETS:
        Asset.objects.create(last_update=today, **asset)


def version_parts(version):
    parts = []
    for part in str(version).split("."):
        match = re.search(r"\d+", part)
        parts.append(int(match.group(0)) if match else 0)
    return parts or [0]


def is_version_outdated(current_version, latest_version):
    current = version_parts(current_version)
    latest = version_parts(latest_version)
    max_length = max(len(current), len(latest))
    current += [0] * (max_length - len(current))
    latest += [0] * (max_length - len(latest))
    return current < latest


def effective_patch_status(asset):
    if asset.patch_status in ("Missing Patch", "Unknown"):
        return asset.patch_status
    if is_version_outdated(asset.current_version, asset.latest_version):
        return "Outdated"
    return "Patched"


def risk_level_from_score(score):
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Medium"
    if score <= 80:
        return "High"
    return "Critical"


def risk_level_label(score, tr):
    level = risk_level_from_score(score)
    return tr[f"{level.lower()}_risk"]


def translated_choice(prefix, value, tr):
    key = f"{prefix}_{value.lower().replace(' ', '_')}"
    return tr.get(key, value)


def last_update_risk(asset):
    if not asset.last_update:
        return 12
    days_old = (date.today() - asset.last_update).days
    if days_old > 180:
        return 20
    if days_old > 90:
        return 12
    if days_old > 30:
        return 5
    return 0


def analyze_asset(asset, lang="en"):
    tr = get_translations(lang)
    status = effective_patch_status(asset)
    base = STATUS_BASE_RISK.get(status, 35)
    criticality_factor = CRITICALITY_WEIGHT.get(asset.criticality, 1.0)
    type_bonus = ASSET_TYPE_WEIGHT.get(asset.asset_type, 5)
    age_bonus = last_update_risk(asset)

    raw_score = int(base * criticality_factor + type_bonus + age_bonus)
    if status == "Patched":
        raw_score = max(4, min(24, raw_score))
    score = max(0, min(100, raw_score))
    level = risk_level_from_score(score)

    if score >= 81:
        priority = "Immediate"
    elif score >= 61:
        priority = "High Priority"
    elif score >= 31:
        priority = "Normal Priority"
    else:
        priority = "Low Priority"

    if status == "Patched":
        problem_key = "problem_patched"
        recommendation_key = "recommend_patched"
    elif status == "Missing Patch":
        problem_key = "problem_missing"
        recommendation_key = "recommend_missing"
    elif status == "Unknown":
        problem_key = "problem_unknown"
        recommendation_key = "recommend_unknown"
    else:
        problem_key = "problem_outdated"
        recommendation_key = "recommend_outdated"

    return {
        "asset": asset,
        "effective_status": status,
        "status_label": translated_choice("status", status, tr),
        "criticality_label": translated_choice("criticality", asset.criticality, tr),
        "asset_type_label": translated_choice("asset_type", asset.asset_type, tr),
        "risk_score": score,
        "risk_level": level,
        "risk_level_label": risk_level_label(score, tr),
        "priority": priority,
        "priority_label": translated_choice("priority", priority, tr),
        "problem": tr[problem_key],
        "recommendation": tr[recommendation_key],
    }


def calculate_assessment(lang="en"):
    assets = list(Asset.objects.all())
    analyses = [analyze_asset(asset, lang) for asset in assets]
    total = len(assets)
    patched = sum(1 for item in analyses if item["effective_status"] == "Patched")
    outdated = sum(1 for item in analyses if item["effective_status"] == "Outdated")
    missing = sum(1 for item in analyses if item["effective_status"] == "Missing Patch")
    critical_assets = sum(1 for item in analyses if item["risk_level"] == "Critical")

    compliance = round((patched / total) * 100, 1) if total else 100.0
    average_risk = round(sum(item["risk_score"] for item in analyses) / total) if total else 0

    if missing:
        average_risk += min(10, missing * 2)
    if critical_assets:
        average_risk += min(10, critical_assets * 3)

    risk_score = max(0, min(100, average_risk))
    risk_level = risk_level_from_score(risk_score)

    summary = {
        "total_assets": total,
        "patched_assets": patched,
        "outdated_assets": outdated,
        "missing_patch_assets": missing,
        "critical_assets": critical_assets,
        "compliance_percentage": compliance,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_level_label": risk_level_label(risk_score, get_translations(lang)),
    }
    return summary, analyses


def save_assessment_report(lang="en"):
    tr = get_translations(lang)
    summary, analyses = calculate_assessment(lang)
    assessment_data = {key: value for key, value in summary.items() if key != "risk_level_label"}
    assessment = PatchAssessment.objects.create(**assessment_data)
    report_text, recommendations = build_report_text(summary, analyses, tr)
    report = AssessmentReport.objects.create(
        assessment=assessment,
        report_text=report_text,
        recommendations=recommendations,
    )
    return report


def build_report_text(summary, analyses, tr):
    now = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")
    lines = [
        "PatchGuard Manager - Security Report",
        tr["coursework_topic"],
        f"{tr['report_date']}: {now}",
        "",
        tr["assessment_summary"],
        f"{tr['total_assets']}: {summary['total_assets']}",
        f"{tr['patched_systems']}: {summary['patched_assets']}",
        f"{tr['outdated_systems']}: {summary['outdated_assets']}",
        f"{tr['missing_patches']}: {summary['missing_patch_assets']}",
        f"{tr['critical_assets']}: {summary['critical_assets']}",
        f"{tr['patch_compliance']}: {summary['compliance_percentage']}%",
        f"{tr['overall_risk_score']}: {summary['risk_score']}",
        f"{tr['risk_level']}: {summary['risk_level_label']}",
        "",
        tr["asset_inventory"],
    ]

    recommendation_lines = []
    for index, item in enumerate(analyses, start=1):
        asset = item["asset"]
        lines.extend([
            "",
            f"{index}. {asset.name}",
            f"{tr['asset_type']}: {item['asset_type_label']}",
            f"{tr['operating_system']}: {asset.operating_system}",
            f"{tr['software_name']}: {asset.software_name}",
            f"{tr['current_version']}: {asset.current_version}",
            f"{tr['latest_version']}: {asset.latest_version}",
            f"{tr['status']}: {item['status_label']}",
            f"{tr['criticality']}: {item['criticality_label']}",
            f"{tr['risk_score']}: {item['risk_score']}",
            f"{tr['risk_level']}: {item['risk_level_label']}",
            f"{tr['priority']}: {item['priority_label']}",
            f"{tr['detected_problem']}: {item['problem']}",
            f"{tr['recommendation']}: {item['recommendation']}",
        ])
        recommendation_lines.append(f"{asset.name}: {item['priority_label']} - {item['recommendation']}")

    lines.extend(["", tr["conclusion"], tr["report_conclusion"]])
    return "\n".join(lines), "\n".join(recommendation_lines)


def register_pdf_font():
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("PatchGuardFont", path))
                return "PatchGuardFont"
            except Exception:
                continue
    return "Helvetica"


def pdf_response_from_report(report_text, filename="PatchGuard_Report.pdf"):
    font_name = register_pdf_font()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("PatchGuardNormal", parent=styles["Normal"], fontName=font_name, fontSize=9, leading=13)
    title = ParagraphStyle("PatchGuardTitle", parent=styles["Title"], fontName=font_name, fontSize=16, leading=20)

    story = [Paragraph("PatchGuard Manager", title), Spacer(1, 0.4 * cm)]
    for line in report_text.splitlines():
        if not line.strip():
            story.append(Spacer(1, 0.15 * cm))
        elif line.startswith("PatchGuard Manager"):
            continue
        else:
            story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), normal))

    document.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
