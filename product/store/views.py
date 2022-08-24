from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Product, UserProductRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import ProductSerializer, UserProductRelationSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
    )
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserProductRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserProductRelation.objects.all()
    serializer_class = UserProductRelationSerializer
    lookup_field = 'product'

    def get_object(self):
        obj, _ = UserProductRelation.objects.get_or_create(user=self.request.user,
                                                           product_id=self.kwargs['product'])
        return obj


def auth(request):
    return render(request, 'oauth.html')
