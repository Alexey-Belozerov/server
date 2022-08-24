from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Product, UserProductRelation
from store.serializers import ProductSerializer


class ProductSerializersTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')
        product_1 = Product.objects.create(name='Test product 1', price=50, author_name='Author 1')
        product_2 = Product.objects.create(name='Test product 2', price=120, author_name='Author 2')

        UserProductRelation.objects.create(user=user1, product=product_1, like=True, rate=5)
        UserProductRelation.objects.create(user=user2, product=product_1, like=True, rate=5)
        UserProductRelation.objects.create(user=user3, product=product_1, like=True, rate=4)

        UserProductRelation.objects.create(user=user1, product=product_2, like=True, rate=3)
        UserProductRelation.objects.create(user=user2, product=product_2, like=True, rate=4)
        UserProductRelation.objects.create(user=user3, product=product_2, like=False)

        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        ).order_by('id')
        data = ProductSerializer(products, many=True).data
        expected_data = [
            {
                'id': product_1.id,
                'name': 'Test product 1',
                'price': '50.00',
                'author_name': 'Author 1',
                'likes_count': 3,
                'annotated_likes': 3,
                'rating': '4.67'
            },
            {
                'id': product_2.id,
                'name': 'Test product 2',
                'price': '120.00',
                'author_name': 'Author 2',
                'likes_count': 2,
                'annotated_likes': 2,
                'rating': '3.50'
            },
        ]
        self.assertEqual(expected_data, data)
