import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from api.models.user import CustomUser


class JobSeeker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    resume = models.URLField(max_length=2000, null=True, blank=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        name_parts = [part for part in (self.first_name, self.last_name) if part]
        return " ".join(name_parts) if name_parts else self.user.email


class Employer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(max_length=2000, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.company_name or self.user.email


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    EMPLOYMENT_TYPE_CHOICES = [
        ("FT", "Full-time"),
        ("PT", "Part-time"),
        ("CT", "Contract"),
        ("IN", "Internship"),
    ]

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField()
    salary = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True, default="Remote")
    employment_type = models.CharField(max_length=2, choices=EMPLOYMENT_TYPE_CHOICES)
    posted_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    application_url = models.URLField(
        max_length=2000,
        null=True,
        blank=True,
        help_text="URL for external applications",
    )

    def is_active(self):
        return self.status == self.Status.ACTIVE

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    def generate_slug(self):
        base_slug = slugify(self.title)
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_slug}-{unique_id}"

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ("P", "Pending"),
        ("R", "Reviewed"),
        ("I", "Interviewed"),
        ("A", "Accepted"),
        ("D", "Declined"),
    ]

    class Meta:
        unique_together = ("job", "applicant")

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    cover_letter = models.TextField()

    def __str__(self):
        return f"{self.applicant.user.email}'s application for {self.job.title}"
