from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    name = models.CharField('Наименование', max_length=255)
    price = models.DecimalField('Цена', max_digits=7, decimal_places=2)
    author_name = models.CharField('Автор', max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_products')
    readers = models.ManyToManyField(User, through='UserProductRelation', related_name='products')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f"Наименование: {self.name}, Автор: {self.author_name}, Цена - {self.price}, Владелец - {self.owner}"


class UserProductRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Удовлетворительно'),
        (2, 'Хорошо'),
        (3, 'Отлично'),
        (4, 'Супер'),
        (5, 'Грандиозно'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    like = models.BooleanField('Лайк', default=False)
    in_bookmarks = models.BooleanField('Закладки', default=False)
    rate = models.PositiveSmallIntegerField('Рейтинг', choices=RATE_CHOICES, null=True)

    class Meta:
        verbose_name = 'Отношение пользователь продукт'
        verbose_name_plural = 'Отношение пользователи продукты'

    def __str__(self):
        return f"Пользователь: {self.user.username}, {self.product}, Рейтинг - {self.rate}"
