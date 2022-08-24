import json
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Product, UserProductRelation
from store.serializers import ProductSerializer


class ProductsApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.product_1 = Product.objects.create(
            name='Test product 1',
            price=1500,
            author_name='Маша',
            owner=self.user
        )
        self.product_2 = Product.objects.create(
            name='Test product 2',
            price=2500,
            author_name='Даша',
            owner=self.user
        )
        self.product_3 = Product.objects.create(
            name='Test product 2',
            price=2500,
            author_name='Маша',
            owner=self.user
        )

        UserProductRelation.objects.create(user=self.user, product=self.product_1, like=True, rate=5)

    def test_get(self):
        url = reverse('product-list')
        response = self.client.get(url)
        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        )
        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'price': 1500})
        products = Product.objects.filter(id__in=[self.product_1.id]).annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        )
        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_search(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'search': 'Test product 2'})
        products = Product.objects.filter(id__in=[self.product_2.id, self.product_3.id]).annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        )
        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_ordering(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'price': 2500})
        products = Product.objects.filter(id__in=[self.product_2.id, self.product_3.id]).annotate(
            annotated_likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        )
        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-list')
        data = {
            'name': 'Краснодар',
            'price': 2854,
            'author_name': 'Синица Виктория'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Product.objects.all().count())
        self.assertEqual(self.user, Product.objects.last().owner)

    def test_update(self):
        url = reverse('product-detail', args=(self.product_1.id,))
        data = {
            'name': self.product_1.id,
            'price': 900,
            'author_name': self.product_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.product_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(900, self.product_1.price)

    def test_delete(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-detail', args=(self.product_1.id,))
        data = {
            'name': self.product_1.id,
            'price': self.product_1.price,
            'author_name': self.product_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Product.objects.all().count())

    def test_delete_note_owner(self):
        self.user2 = User.objects.create(username='test_user2')
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-detail', args=(self.product_1.id,))
        data = {
            'name': self.product_1.id,
            'price': self.product_1.price,
            'author_name': self.product_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Product.objects.all().count())

    def test_update_not_owner(self):
        self.user1 = User.objects.create(username='test_user1')
        url = reverse('product-detail', args=(self.product_1.id,))
        data = {
            'name': self.product_1.name,
            'price': 550,
            'author_name': self.product_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual({'detail': ErrorDetail(string='У вас недостаточно прав для выполнения данного действия.',
                                                code='permission_denied')}, response.data)
        self.product_1.refresh_from_db()
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1500, self.product_1.price)

    def test_update_not_owner_but_staff(self):
        self.user3 = User.objects.create(username='test_user3',
                                         is_staff=True)
        url = reverse('product-detail', args=(self.product_1.id,))
        data = {
            'name': self.product_1.name,
            'price': 3500,
            'author_name': self.product_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user3)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.product_1.refresh_from_db()
        self.assertEqual(3500, self.product_1.price)


class UserProductRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user1 = User.objects.create(username='test_username1')
        self.product_1 = Product.objects.create(
            name='Test product 1',
            price=1500,
            author_name='Маша',
            owner=self.user
        )
        self.product_2 = Product.objects.create(
            name='Test product 2',
            price=2500,
            author_name='Даша',
            owner=self.user
        )

    def test_like(self):
        url = reverse('userproductrelation-detail', args=(self.product_1.id,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserProductRelation.objects.get(user=self.user,
                                                product=self.product_1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('userproductrelation-detail', args=(self.product_1.id,))
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserProductRelation.objects.get(user=self.user,
                                                product=self.product_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userproductrelation-detail', args=(self.product_1.id,))
        data = {
            'rate': 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserProductRelation.objects.get(user=self.user,
                                                product=self.product_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userproductrelation-detail', args=(self.product_1.id,))
        data = {
            'rate': 8,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
