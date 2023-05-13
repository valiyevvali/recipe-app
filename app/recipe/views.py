from rest_framework import (viewsets, mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from . import serializers
from core.models import Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user). \
            order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        """filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user). \
            order_by('-name')
