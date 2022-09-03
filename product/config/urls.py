from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter

from store import views
from store.views import ProductViewSet, auth, UserProductRelationViewSet

router = SimpleRouter()

router.register(r'product', ProductViewSet)
router.register(r'productrelation', UserProductRelationViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('admin/', admin.site.urls),
    re_path('', include('social_django.urls', namespace='social')),
    path('auth/', auth),
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += router.urls