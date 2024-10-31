from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.response import Response


class CRUDWithoutPUT(viewsets.ModelViewSet):
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=HTTPStatus.METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
