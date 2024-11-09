from rest_framework import serializers

from api.models import JobSeeker


class JobSeekerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeeker
        fields = ["first_name", "last_name", "skills"]
