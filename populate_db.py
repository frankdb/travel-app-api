import os
import random
import uuid

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_board.settings")
django.setup()

from django.contrib.auth import get_user_model
from faker import Faker

from api.models import Application, Employer, Job, JobSeeker

User = get_user_model()
fake = Faker()


def create_users():
    for i in range(100):
        email = fake.email()
        user_type = "EM" if i < 50 else "JS"
        user = User.objects.create_user(
            email=email, password="password", user_type=user_type
        )
        if user_type == "EM":
            Employer.objects.create(
                user=user,
                company_name=fake.company(),
                description=fake.text(),
                website=fake.url(),
                location=fake.city(),
            )
        else:
            JobSeeker.objects.create(
                user=user,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                skills=", ".join(fake.words(nb=5)),
            )


def create_jobs():
    employers = Employer.objects.all()
    status_choices = [
        Job.Status.DRAFT,
        Job.Status.ARCHIVED,
    ]

    # Calculate date range
    end_date = django.utils.timezone.now()
    start_date = end_date - django.utils.timezone.timedelta(days=60)

    for employer in employers:
        num_jobs = random.randint(11, 15)
        for _ in range(num_jobs):
            # 80% chance of being active (simulating paid posts)
            status = (
                Job.Status.ACTIVE
                if random.random() < 0.8
                else random.choice(status_choices)
            )

            # Generate random datetime between start_date and end_date
            random_date = start_date + django.utils.timezone.timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )

            Job.objects.create(
                title=fake.job(),
                employer=employer,
                description=fake.text(),
                requirements=fake.text(),
                salary=f"${random.randint(30000, 150000)} per year",
                location=fake.city(),
                employment_type=random.choice(["FT", "PT", "CT", "IN"]),
                status=status,
                posted_date=random_date,
                # 50% chance of having an application URL. application url should be google.com if it exists
                application_url="https://google.com" if random.random() < 0.5 else None,
            )


def create_applications():
    job_seekers = JobSeeker.objects.all()
    # Only allow applications to ACTIVE jobs
    active_jobs = Job.objects.filter(status=Job.Status.ACTIVE)

    for job_seeker in job_seekers:
        num_applications = random.randint(2, 5)
        applied_jobs = random.sample(list(active_jobs), num_applications)
        for job in applied_jobs:
            Application.objects.create(
                job=job,
                applicant=job_seeker,
                cover_letter=fake.text(),
                status=random.choice(["P", "R", "I", "A", "D"]),
            )


if __name__ == "__main__":
    print("Creating users...")
    create_users()
    print("Creating jobs...")
    create_jobs()
    print("Creating applications...")
    create_applications()
    print("Database population completed!")
