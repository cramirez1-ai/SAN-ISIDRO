from django.contrib import admin

from .models import (
    Announcement,
    AuditLog,
    CertificateRequest,
    Complaint,
    Feedback,
    Household,
    Resident,
)


admin.site.site_header = "San Isidro Information System Administration"
admin.site.site_title = "San Isidro Admin"
admin.site.index_title = "Brgy San Isidro Records Management"


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "purok", "civil_status", "occupation", "contact_number", "is_senior_citizen", "is_pwd")
    list_filter = ("purok", "civil_status", "is_male", "is_senior_citizen", "is_pwd", "is_registered_voter")
    search_fields = ("first_name", "middle_name", "last_name", "address", "contact_number")
    date_hierarchy = "created_at"
    list_per_page = 25


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("house_number", "family_head", "purok", "address", "member_count")
    search_fields = ("house_number", "family_head", "purok", "address")
    list_filter = ("purok",)
    date_hierarchy = "created_at"

    def member_count(self, obj):
        return obj.members.count()


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ("resident", "document_type", "purpose", "status", "requested_at")
    list_filter = ("document_type", "status", "requested_at")
    search_fields = ("resident__first_name", "resident__last_name", "purpose", "remarks")
    date_hierarchy = "requested_at"
    actions = ("approve_requests", "mark_ready_to_claim")

    @admin.action(description="Approve selected requests")
    def approve_requests(self, request, queryset):
        queryset.update(status="approved")

    @admin.action(description="Mark selected requests as ready to claim")
    def mark_ready_to_claim(self, request, queryset):
        queryset.update(status="ready")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "posted_at")
    list_filter = ("category", "is_published", "posted_at")
    search_fields = ("title", "message")
    date_hierarchy = "posted_at"


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("title", "complainant", "incident_location", "status", "hearing_date", "created_at")
    list_filter = ("status", "created_at", "hearing_date")
    search_fields = ("title", "description", "incident_location", "complainant__first_name", "complainant__last_name")
    date_hierarchy = "created_at"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("resident", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("message", "resident__first_name", "resident__last_name")
    date_hierarchy = "created_at"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user_name", "action", "record_name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user_name", "action", "record_name")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
