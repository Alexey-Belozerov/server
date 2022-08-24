from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Product, UserProductRelation


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass


@admin.register(UserProductRelation)
class UserProductRelationAdmin(ModelAdmin):
    list_filter = ['like', 'in_bookmarks', 'rate']
