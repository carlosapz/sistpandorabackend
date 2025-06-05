from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class DashboardView(APIView):
    """
    Vista simple para el dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Bienvenido al Dashboard"},
            status=status.HTTP_200_OK
        )
