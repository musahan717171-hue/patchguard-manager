from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import AssetForm, LoginForm
from .models import AssessmentReport, Asset
from .utils import (
    calculate_assessment,
    create_demo_data,
    get_language,
    get_translations,
    get_ui_context,
    ensure_demo_user,
    pdf_response_from_report,
    save_assessment_report,
    build_report_text,
    risk_level_label,
)


def context(request, extra=None):
    data = get_ui_context(request)
    if extra:
        data.update(extra)
    return data


def set_language(request):
    lang = request.GET.get("lang", "en")
    if lang not in ("en", "ru", "tk"):
        lang = "en"
    next_url = request.GET.get("next") or reverse("dashboard")
    request.session["language"] = lang
    response = redirect(next_url)
    response.set_cookie("patchguard_language", lang, max_age=60 * 60 * 24 * 365)
    return response


def login_view(request):
    ensure_demo_user()
    lang = get_language(request)
    tr = get_translations(lang)

    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request.POST or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            create_demo_data()
            return redirect("dashboard")
        messages.error(request, tr["incorrect_credentials"])

    return render(request, "login.html", context(request, {"form": form}))


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    create_demo_data()
    lang = get_language(request)
    summary, analyses = calculate_assessment(lang)
    return render(request, "dashboard.html", context(request, {"summary": summary, "analyses": analyses[:6]}))


@login_required
def asset_list(request):
    lang = get_language(request)
    summary, analyses = calculate_assessment(lang)
    search = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "All")

    if search:
        analyses = [
            item for item in analyses
            if search in item["asset"].name.lower()
            or search in item["asset"].operating_system.lower()
            or search in item["asset"].software_name.lower()
        ]

    if status_filter != "All":
        analyses = [item for item in analyses if item["effective_status"] == status_filter]

    return render(
        request,
        "assets.html",
        context(request, {"summary": summary, "analyses": analyses, "search": request.GET.get("q", ""), "status_filter": status_filter}),
    )


@login_required
def asset_create(request):
    lang = get_language(request)
    tr = get_translations(lang)
    form = AssetForm(request.POST or None, lang=lang)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, tr["asset_saved"])
        return redirect("assets")
    return render(request, "asset_form.html", context(request, {"form": form, "title": tr["add_asset"]}))


@login_required
def asset_edit(request, pk):
    lang = get_language(request)
    tr = get_translations(lang)
    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, instance=asset, lang=lang)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, tr["asset_saved"])
        return redirect("assets")
    return render(request, "asset_form.html", context(request, {"form": form, "title": tr["edit_asset"]}))


@login_required
@require_POST
def asset_delete(request, pk):
    tr = get_translations(get_language(request))
    asset = get_object_or_404(Asset, pk=pk)
    asset.delete()
    messages.success(request, tr["asset_deleted"])
    return redirect("assets")


@login_required
def assessment(request):
    lang = get_language(request)
    summary, analyses = calculate_assessment(lang)
    return render(request, "assessment.html", context(request, {"summary": summary, "analyses": analyses}))


@login_required
@require_POST
def assessment_save(request):
    tr = get_translations(get_language(request))
    report = save_assessment_report(get_language(request))
    messages.success(request, tr["report_saved"])
    return redirect("report_detail", pk=report.pk)


@login_required
def reports(request):
    lang = get_language(request)
    tr = get_translations(lang)
    summary, analyses = calculate_assessment(lang)
    report_text, recommendations = build_report_text(summary, analyses, tr)
    return render(
        request,
        "reports.html",
        context(request, {"summary": summary, "analyses": analyses, "report_text": report_text, "recommendations": recommendations}),
    )


@login_required
def download_current_report_pdf(request):
    lang = get_language(request)
    tr = get_translations(lang)
    summary, analyses = calculate_assessment(lang)
    report_text, _ = build_report_text(summary, analyses, tr)
    return pdf_response_from_report(report_text)


@login_required
def history(request):
    lang = get_language(request)
    tr = get_translations(lang)
    reports_list = []
    for report in AssessmentReport.objects.select_related("assessment").all():
        reports_list.append({
            "report": report,
            "risk_level_label": risk_level_label(report.assessment.risk_score, tr),
        })
    return render(request, "history.html", context(request, {"reports_list": reports_list}))


@login_required
def report_detail(request, pk):
    lang = get_language(request)
    tr = get_translations(lang)
    report = get_object_or_404(AssessmentReport.objects.select_related("assessment"), pk=pk)
    risk_label = risk_level_label(report.assessment.risk_score, tr)
    return render(request, "report_detail.html", context(request, {"report": report, "risk_label": risk_label}))


@login_required
def report_download_pdf(request, pk):
    report = get_object_or_404(AssessmentReport, pk=pk)
    return pdf_response_from_report(report.report_text, filename=f"PatchGuard_Report_{pk}.pdf")


@login_required
@require_POST
def report_delete(request, pk):
    tr = get_translations(get_language(request))
    report = get_object_or_404(AssessmentReport, pk=pk)
    report.assessment.delete()
    messages.success(request, tr["report_deleted"])
    return redirect("history")


@login_required
def education(request):
    return render(request, "education.html", context(request))


@login_required
def settings_view(request):
    return render(request, "settings.html", context(request))
