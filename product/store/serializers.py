from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Product, UserProductRelation


class ProductSerializer(ModelSerializer):
    # likes_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'author_name', 'annotated_likes', 'rating')

    # def get_likes_count(self, instance):
    #     return UserProductRelation.objects.filter(product=instance, like=True).count()


class UserProductRelationSerializer(ModelSerializer):
    class Meta:
        model = UserProductRelation
        fields = ['product', 'like', 'in_bookmarks', 'rate']