"""
Health check API views using Django REST Framework
"""
import sys
import platform
import django
from datetime import datetime, timezone
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .schemas import HealthCheckResponse, ErrorResponse, DatabaseResponse, SystemInfoResponse

class HealthCheckView(APIView):
    """
    Health check API endpoint that returns application status
    
    GET /healthz/
    Returns a comprehensive health check response including:
    - Application status
    - Database connectivity
    - System information
    - Timestamp
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def get(self, request):
        """
        Handle GET request for health check
        """
        try:
            database_status = self._check_database()
            system_info = self._get_system_info()
            
            health_dto = HealthCheckResponse(
                status="healthy" if database_status["connected"] else "unhealthy",
                timestamp=datetime.now(timezone.utc),
                version=getattr(settings, 'APP_VERSION', '1.0.0'),
                database="connected" if database_status["connected"] else "disconnected",
                environment=getattr(settings, 'ENVIRONMENT', 'development'),
                details={
                    "python_version": system_info["python_version"],
                    "django_version": system_info["django_version"],
                    "platform": system_info["platform"],
                    "database_type": database_status["type"],
                    "database_name": database_status["name"]
                }
            )
            response_data = health_dto.model_dump()
            return Response(
                response_data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            error_dto = ErrorResponse(
                error="Health check failed",
                code="HEALTH_CHECK_ERROR",
                timestamp=datetime.now(timezone.utc),
                details={
                    "error_message": str(e),
                    "error_type": type(e).__name__
                }
            )
            error_data = error_dto.model_dump()
            return Response(
                error_data,
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    def _check_database(self):
        """
        Check database connectivity
        
        Returns:
            DatabaseResponse: Database status information
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return DatabaseResponse(
                    connected=True,
                    type=connection.vendor,
                    name=connection.settings_dict.get('NAME', 'unknown')
                )
        except Exception:
            return DatabaseResponse(
                connected=False,
                type=connection.vendor,
                name=connection.settings_dict.get('NAME', 'unknown')
            )

    def _get_system_info(self):
        """
        Get system information
        
        Returns:
            dict: System information
        """
        
        return SystemInfoResponse(
            python_version= f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            django_version= django.get_version(),
            platform= platform.platform()
        )
