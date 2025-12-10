from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        }
        if request.user.company:
            data['company'] = {
                'name': request.user.company.name,
                'status': request.user.company.status,
                'is_active': request.user.company.is_active,
            }

        return Response(data)
