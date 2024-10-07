import asyncio
import json

from asgiref.sync import async_to_sync

# Create your views here.
from adrf.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

from fabric.interfaces.FabricSmartContractInterface import FabricSmartContractInterface



class InterfaceGeneratorSingelton(type):
    interface = None
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        instance = super().__call__(*args, **kwargs)
        cls._instances[cls] = instance
        cls.interface = FabricSmartContractInterface(settings.FABRIC_USER, settings.FABRIC_ORG)
        return cls._instances[cls]


class InterfaceGenerator(metaclass=InterfaceGeneratorSingelton):
    def some_business_logic(self):
        """
        Finally, any singleton should define some business logic, which can be
        executed on its instance.
        """

        # ...


class CreateAssetView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from the request
        data = request.data
        code = data.get('code')
        description = data.get('description')
        amount = data.get('amount')

        # Validate that the necessary data is present
        if not all([code, description, amount is not None]):
            return Response(
                {"error": "Missing required fields: code, description, amount"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Assuming the function create_asset is defined somewhere accessible
            interface = InterfaceGenerator().interface
            response = async_to_sync(interface.create_asset)(code, description, int(amount))
            return Response(
                {"message": "Asset created successfully"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Error handling in case of failures when creating the asset
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )


class CreateAssetWithConsumeView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from the request
        data = request.data
        code = data.get('code')
        description = data.get('description')
        amount = data.get('amount')
        assets_consumed = data.get('assets_consumed')  # This is expected to be a JSON string
        # Validate the presence of all required data
        if not all([code, description, amount is not None, assets_consumed]):
            return Response(
                {"error": "Missing required fields: code, description, amount, or assets_consumed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to parse assets_consumed and validate it
        try:
            # Ensure assets_consumed is a list of tuples
            if not all(isinstance(item, list) and len(item) == 2 for item in assets_consumed):
                raise ValueError("assets_consumed must be a list of [str, int] tuples")
        except (json.JSONDecodeError, ValueError) as e:
            return Response(
                {"error": f"Invalid format for assets_consumed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            print(str(async_to_sync(InterfaceGenerator().interface.consume_and_create)(code, description, int(amount), assets_consumed)))
            return Response(
                {"message": "Asset created successfully"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            raise
            # Handle errors in asset consumption and creation
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )


class GetAllAssetsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Llama a la función asíncrona directamente con await
            assets_json = json.loads(async_to_sync(InterfaceGenerator().interface.get_all_assets)())
            return Response(
                {"assets": assets_json},  # Devolver los activos como JSON
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReadAssetView(APIView):
    def get(self, request, code, *args, **kwargs):
        try:
            asset_details = json.loads(async_to_sync(InterfaceGenerator().interface.read_asset)(code))
            if asset_details:
                return Response(asset_details, status=status.HTTP_200_OK, content_type='application/json')
            else:
                return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Generic error handling
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProposeTransferView(APIView):
    def post(self, request, code, *args, **kwargs):
        # Extract 'code' and 'send_to' from the request data
        post_code = request.data.get('code')
        send_to = request.data.get('send_to')

        # Validate that both 'code' and 'send_to' are provided
        if not post_code or not send_to:
            return Response(
                {"error": "Both 'code' and 'send_to' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if post_code != code:
            return Response(
                {"error": "POST 'code' and GET 'code' missmatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call the propose_transfer function with the parameters
        try:
            async_to_sync(InterfaceGenerator().interface.propose_transfer)(code, send_to)
            return Response(
                {"message": "Asset marked for transfer"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Generic error handling
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )


class AcceptTransferView(APIView):
    def post(self, request, code,  *args, **kwargs):
        # Extract 'code' from the request data
        post_code = request.data.get('code')

        # Validate that 'code' is provided
        if not post_code:
            return Response(
                {"error": "The 'code' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if post_code != code:
            return Response(
                {"error": "POST 'code' and GET 'code' missmatch"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Call the accept_transfer function with the code
        try:
            async_to_sync(InterfaceGenerator().interface.accept_transfer)(code)
            return Response(
                {"message": "Asset transfer successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Generic error handling
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )


class ConsumeAssetView(APIView):
    def post(self, request, code, *args, **kwargs):
        # Extract 'code' and 'amount' from the request data
        post_code = request.data.get('code')
        amount = request.data.get('amount')

        # Validate that 'code' and 'amount' are provided
        if not post_code or amount is None:
            return Response(
                {"error": "Both 'code' and 'amount' parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if post_code != code:
            return Response(
                {"error": "POST 'code' and GET 'code' missmatch"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Convert amount to integer and call the consume function
            amount = int(amount)
            result = async_to_sync(InterfaceGenerator().interface.consume)(code, amount)
            return Response(
                {"message": "Asset consumed successfully"},
                status=status.HTTP_200_OK
            )
        except ValueError:
            # Handle case where amount is not a valid integer
            return Response(
                {"error": "Invalid 'amount' parameter. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Generic error handling
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_INTERNAL_SERVER_ERROR
            )


class FetchAssetHistoryView(APIView):
    def get(self, request, code, *args, **kwargs):
        try:
            asset_details = json.loads(async_to_sync(InterfaceGenerator().interface.history)(code))
            if asset_details:
                return Response(asset_details, status=status.HTTP_200_OK, content_type='application/json')
            else:
                return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Generic error handling
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
