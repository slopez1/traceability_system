import json

from django.conf import settings

from core.interfaces.SmartContractInterface import SmartContractInterface

class FabricSmartContractInterface(SmartContractInterface):
    ORGS = settings.ORGS
    PEERS = ['peer0.org1.example.com', 'peer0.org2.example.com']
    CC_NAME = "SmartContract"  # Contract name, set on subclass

    def __init__(self, user: str, org: int):
        if self.CC_NAME == "":
            raise Exception("CC_NAME not defined, extends this class an define it")
        if user not in "Admin" and "User" not in user:
            # The 2 organizations have created the users Admin and User1 - User100
            raise Exception("User must be Admin or UserX, here X is a number")
        if org < 1 or org >= len(self.ORGS) + 1:
            raise Exception("Organization have to be gretter than 0 and lower than {}".format(str(len(self.ORGS) + 1)))
        org -= 1  # Org 1 is on position 0

        self.cli = settings.FABRIC_CLIENT
        self.user = self.cli.get_user(org_name=self.ORGS[org], name=user)

        self.peer = self.PEERS[org]
        self.channel = "mychannel"

    def _query(self, fcn: str, args: tuple[str]) -> str:
        """
        Query the ledger without modifying it
        :param fcn: Contract function name
        :param args: Arguments to pass to the function must be strings. An array of several parameters would be represented "['1,2', 'Other value']"
        :return: Function response string
        """
        response = self.loop.run_until_complete(self.cli.chaincode_query)(
            requestor=self.user,
            channel_name=self.channel,
            peers=self.PEERS,
            args=args,
            cc_name=self.CC_NAME,
            fcn=fcn,
        )
        return response


    def _invoke(self, fcn: str, args: list[str]) -> str:
        """
        Query the ledger without modifying it
        :param fcn: Contract function name
        :param args: Arguments to pass to the function must be strings. An array of several parameters would be represented "['1,2', 'Other value']"
        :return: Function response string
        """
        #
        response = self.cli.chaincode_invoke(
            requestor=self.user,
            channel_name=self.channel,
            peers=self.PEERS,
            args=args,
            cc_name=self.CC_NAME,
            fcn=fcn,
        )
        return response




    def  create_asset(self, code: str, description: str, amount: int) -> str:
        return self._invoke(self._get_function_names_map()['create'], [str(code), str(description), str(amount)])

    def read_asset(self, code: str) -> str:
        return self._invoke(self._get_function_names_map()['read'], [str(code)])

    def get_all_assets(self) -> str:
        return self._invoke(self._get_function_names_map()['all'], [])

    def consume_and_create(self, code: str, description: str, amount: int, assets_consumed: [(str, int)]) -> str:
        assets_consumed_modified = [{"ID": str(item[0]), "Amount": item[1]} for item in assets_consumed]
        assets_consumed_modified = json.dumps(assets_consumed_modified)

        return self._invoke(self._get_function_names_map()['consume_and_create'], [str(code), str(description), str(amount), str(assets_consumed_modified)])

    def propose_transfer(self, code: str, send_to: str) -> str:
        return self._invoke(self._get_function_names_map()['propose_transfer'],
                            [str(code), str(send_to)])

    def accept_transfer(self, code: str) -> str:
        return self._invoke(self._get_function_names_map()['accept_transfer'],
                            [str(code)])

    def consume(self, code: str, amount: int) -> str:
        return self._invoke(self._get_function_names_map()['consume'],
                            [str(code), str(amount)])

    def history(self, code: str) -> str:
        return self._invoke(self._get_function_names_map()['history'],
                            [str(code)])

