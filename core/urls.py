from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("set-language/", views.set_language, name="set_language"),
    path("", views.dashboard, name="dashboard"),
    path("assets/", views.asset_list, name="assets"),
    path("assets/add/", views.asset_create, name="asset_create"),
    path("assets/<int:pk>/edit/", views.asset_edit, name="asset_edit"),
    path("assets/<int:pk>/delete/", views.asset_delete, name="asset_delete"),
    path("assessment/", views.assessment, name="assessment"),
    path("assessment/save/", views.assessment_save, name="assessment_save"),
    path("reports/", views.reports, name="reports"),
    path("reports/download/current/", views.download_current_report_pdf, name="download_current_report_pdf"),
    path("history/", views.history, name="history"),
    path("reports/<int:pk>/", views.report_detail, name="report_detail"),
    path("reports/<int:pk>/download/", views.report_download_pdf, name="report_download_pdf"),
    path("reports/<int:pk>/delete/", views.report_delete, name="report_delete"),
    path("education/", views.education, name="education"),
    path("settings/", views.settings_view, name="settings"),
]
