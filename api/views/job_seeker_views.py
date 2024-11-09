from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.job_seeker_serializers import JobSeekerUpdateSerializer


class JobSeekerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        if not hasattr(request.user, "jobseeker"):
            return Response(
                {"error": "Only job seekers can update this information"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = JobSeekerUpdateSerializer(
            request.user.jobseeker, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
