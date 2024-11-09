from rest_framework import serializers

from api.models import Employer


class EmployerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ["company_name", "description", "website", "location"]
