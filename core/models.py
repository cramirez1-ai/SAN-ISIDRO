from django.db import models


class Household(models.Model):
    house_number = models.CharField(max_length=50, unique=True)
    purok = models.CharField(max_length=80)
    family_head = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.house_number} - {self.family_head}"


class Resident(models.Model):
    CIVIL_STATUS_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
    ]

    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80)
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    purok = models.CharField(max_length=80)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES)
    occupation = models.CharField(max_length=120, blank=True)
    contact_number = models.CharField(max_length=30, blank=True)
    is_male = models.BooleanField(default=True)
    is_senior_citizen = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    is_registered_voter = models.BooleanField(default=False)
    photo = models.FileField(upload_to="resident_photos/", blank=True, null=True)
    household = models.ForeignKey(Household, on_delete=models.SET_NULL, blank=True, null=True, related_name="members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join(name for name in names if name)

    def __str__(self):
        return self.full_name


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ("event", "Event"),
        ("emergency", "Emergency"),
        ("meeting", "Barangay Meeting"),
        ("program", "Program"),
    ]

    title = models.CharField(max_length=180)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class CertificateRequest(models.Model):
    DOCUMENT_CHOICES = [
        ("clearance", "Barangay Clearance"),
        ("residency", "Certificate of Residency"),
        ("indigency", "Indigency Certificate"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("ready", "Ready to claim"),
    ]

    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name="certificate_requests")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_CHOICES)
    purpose = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    remarks = models.CharField(max_length=255, blank=True)
    digital_signature = models.FileField(upload_to="signatures/", blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.resident}"


class Complaint(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("review", "Under review"),
        ("hearing", "Scheduled hearing"),
        ("resolved", "Resolved"),
    ]

    complainant = models.ForeignKey(Resident, on_delete=models.SET_NULL, blank=True, null=True, related_name="complaints")
    title = models.CharField(max_length=180)
    incident_location = models.CharField(max_length=180)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    hearing_date = models.DateTimeField(blank=True, null=True)
    evidence = models.FileField(upload_to="complaint_evidence/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    RATING_CHOICES = [
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("poor", "Poor"),
    ]

    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, blank=True, null=True)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_rating_display()


class AuditLog(models.Model):
    user_name = models.CharField(max_length=150)
    action = models.CharField(max_length=255)
    record_name = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.action}"
