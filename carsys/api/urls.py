from django.urls import path
from rest_framework.routers import DefaultRouter


from api.views import search, CarViewSet

urlpatterns = [
    path('records/', search),
]

router = DefaultRouter()
router.register('cars', CarViewSet)
urlpatterns += router.urls
