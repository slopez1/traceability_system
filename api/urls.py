from django.urls import path
from .views import (
    CreateAssetView,
    CreateAssetWithConsumeView,
    GetAllAssetsView,
    ReadAssetView,
    ProposeTransferView,
    AcceptTransferView,
    ConsumeAssetView, FetchAssetHistoryView
)

urlpatterns = [
    # Path for creating an asset
    path('asset/create/', CreateAssetView.as_view(), name='create_asset'),

    # Path for creating an asset with consumed assets
    path('asset/create_with_consume/', CreateAssetWithConsumeView.as_view(), name='create_asset_with_consume'),

    # Path for getting all assets
    path('asset/all/', GetAllAssetsView.as_view(), name='get_all_assets'),


    # Path for proposing a transfer of an asset
    path('asset/<str:code>/transfer/propose/', ProposeTransferView.as_view(), name='propose_transfer'),

    # Path for accepting a transfer of an asset
    path('asset/<str:code>/transfer/accept/', AcceptTransferView.as_view(), name='accept_transfer'),

    # Path for consuming an asset
    path('asset/<str:code>/consume/', ConsumeAssetView.as_view(), name='consume_asset'),

    # Path for reading a single asset by code
    path('asset/<str:code>/history/', FetchAssetHistoryView.as_view(), name='history_asset'),

    # Path for reading a single asset by code
    path('asset/<str:code>/', ReadAssetView.as_view(), name='read_asset')

]
