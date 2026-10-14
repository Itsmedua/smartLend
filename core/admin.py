from django.contrib import admin

from .models import Applicant


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "risk_label", "risk_probability", "decision",
                    "created_by", "created_at")
    list_filter = ("risk_label", "decision")
    search_fields = ("full_name",)
