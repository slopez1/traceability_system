

class SmartContractInterface:
    def _get_function_names_map(self) -> dict:
        return {
            'create': 'CreateAsset',
            'read': 'ReadAsset',
            'all': 'GetAllAssets',
            'consume_and_create': 'CreateAssetWithConsume',
            'propose_transfer': 'ProposeTransfer',
            'accept_transfer': 'AcceptTransfer',
            'consume': 'ConsumeAsset',
            'history': 'FetchAssetHistory'
        }

    def create_asset(self, code: str, description: str, amount: int) -> str:
        raise NotImplemented

    def read_asset(self, code: str) -> str:
        raise NotImplemented

    def get_all_assets(self) -> str:
        raise NotImplemented

    def consume_and_create(self, code: str, description: str, amount: int, assets_consumed: [(str, int)]) -> str:
        raise NotImplemented

    def propose_transfer(self, code: str, send_to: str) -> str:
        raise NotImplemented

    def accept_transfer(self, code: str) -> str:
        raise NotImplemented

    def consume(self, code: str, amount: int) -> str:
        raise NotImplemented

    def history(self, code: str) -> str:
        raise NotImplemented

