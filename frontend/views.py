from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View


# Create your views here.

class Main(View):
    template_name = 'data.html'

    def get(self, request):
        api_url = settings.API_URL
        api_get_all = api_url + reverse('get_all_assets')
        owner_id = settings.OWNER_IDENTITY
        transfer_url = '/transfer/propose/'
        return render(request, self.template_name,
                      context={'api_url': api_url,
                               'api_get_all': api_get_all,
                               "owner_id": owner_id,
                               "transfer_url": transfer_url
                               })


class CreateAsset(View):
    template_name = 'create.html'
    def get(self, request):
        api_url = settings.API_URL
        api_get_all = api_url + reverse('get_all_assets')

        api_create_with_consume = api_url + reverse('create_asset_with_consume')
        api_create = api_url + reverse('create_asset')

        owner_id = settings.OWNER_IDENTITY
        return render(request, self.template_name,
                      context={'api_get_all': api_get_all,
                               'api_create': api_create,
                               'api_create_with_consume': api_create_with_consume,
                               "owner_id": owner_id})


class AssetTraceability(View):
    template_name = 'traceability.html'

    def get(self, request):
        api_url = settings.API_URL
        api_read = api_url + '/api/asset/'
        api_history = '/history/'
        owner_id = settings.OWNER_IDENTITY
        return render(request, self.template_name,
                      context={'api_url': api_url,
                               'api_read': api_read,
                               'api_history': api_history,
                               "owner_id": owner_id})


class AssetPending(View):
    template_name = 'pending.html'

    def get(self, request):
        api_url = settings.API_URL
        api_get_all = api_url + reverse('get_all_assets')
        owner_id = settings.OWNER_IDENTITY
        accept_url = '/transfer/accept/'
        return render(request, self.template_name,
                      context={'api_url': api_url,
                               'api_get_all': api_get_all,
                               "owner_id": owner_id,
                               "accept_url": accept_url
                               })