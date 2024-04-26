from django.urls import path

from frontend.views import Main, CreateAsset, AssetTraceability, AssetPending

urlpatterns = [
    # Path for creating an asset
    path('', Main.as_view(), name='main'),
    path('create', CreateAsset.as_view(), name='create'),
    path('traceability', AssetTraceability.as_view(), name='traceability'),
    path('pending', AssetPending.as_view(), name='pending'),
]
