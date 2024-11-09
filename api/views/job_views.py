from django.db.models import Q
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Job
from api.permissions import IsEmployerOrReadOnly
from api.serializers.job_serializers import JobSerializer


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EmployerJobListPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.select_related("employer").all()
    serializer_class = JobSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = (
            Job.objects.select_related("employer")
            .filter(status=Job.Status.ACTIVE)
            .order_by("-posted_date")
        )

        # Add search functionality
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # Add filter functionality
        employment_type = self.request.query_params.get("employment_type", None)
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsEmployerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user.employer)


class JobDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsEmployerOrReadOnly()]

    def get_object(self, pk):
        try:
            return Job.objects.select_related("employer").get(pk=pk)
        except Job.DoesNotExist:
            return None

    def get(self, request, pk):
        job = self.get_object(pk)
        if job is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, pk):
        job = self.get_object(pk)
        if job is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = JobSerializer(job, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job = self.get_object(pk)
        if job is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class JobDetailBySlugView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, slug):
        try:
            return Job.objects.select_related("employer").get(slug=slug)
        except Job.DoesNotExist:
            return None

    def get(self, request, slug):
        job = self.get_object(slug)
        if job is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = JobSerializer(job)
        return Response(serializer.data)


class EmployerJobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EmployerJobListPagination

    def get_queryset(self):
        return (
            Job.objects.select_related("employer")
            .filter(employer=self.request.user.employer)
            .order_by("-posted_date")
        )
