from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.employer_serializers import EmployerUpdateSerializer


class EmployerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        if not hasattr(request.user, "employer"):
            return Response(
                {"error": "Only employers can update this information"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmployerUpdateSerializer(
            request.user.employer, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
