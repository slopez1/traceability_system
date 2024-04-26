import time

from django.core.management.base import BaseCommand, CommandError

from traceability_system import settings
from fabric.interfaces.FabricSmartContractInterface import FabricSmartContractInterface
from fabric.models import *

class Command(BaseCommand):
    help = "Test Fabric Speed (Needed command fabric_init_example_data)"

    def handle(self, *args, **options):
        peers = PeerNode.objects.all()
        orderers = OrdererNode.objects.all()

        if not peers.exists():
            raise Exception("You need at least one peers for the endorsement policies")

        if not orderers.exists():
            raise Exception("You need at least two orderers for the endorsement policies")
        orderer = orderers.first()
        interface = FabricSmartContractInterface(binary_path=settings.BINARY_PATH,
                                            fabric_cfg_path=settings.CONFIG_PATH,
                                            peer_msp_id=settings.MSP_ID,
                                            peer_msp_config_path=settings.MSP_CONFIG_PATH,
                                            peer_tls_root_cert=settings.TLS_ROOT_CERT,
                                            peer_address=settings.PEER_ADDRESS,
                                            channel=settings.CHANNEL,
                                            chaincode=settings.CHAINCODE,
                                            orderer=[orderer.host, orderer.tls_host_override,
                                                     orderer.path_to_tls_ca_cert],
                                            endorsement_peers=[[peer.host, peer.path_to_tls_ca_cert]
                                                               for peer in peers.iterator()]
                                            )


        num = "01"

        a = "a"+num
        b = "b" + num
        # print("Create")
        # print("-------------------------")
        # print(interface.create_asset(a, "Test 1", 100))
        # time.sleep(3)


        # print("transfer")
        # print("-------------------------")
        # print(interface.propose_transfer(a, "eDUwOTo6Q049VXNlcjFAb3JnMS5leGFtcGxlLmNvbSxPVT1jbGllbnQsTD1TYW4gRnJhbmNpc2NvLFNUPUNhbGlmb3JuaWEsQz1VUzo6Q049Y2Eub3JnMS5leGFtcGxlLmNvbSxPPW9yZzEuZXhhbXBsZS5jb20sTD1TYW4gRnJhbmNpc2NvLFNUPUNhbGlmb3JuaWEsQz1VUw=="))
        # time.sleep(3)

        # print("accept_transfer")
        # print("-------------------------")
        # print(interface.accept_transfer(a))
        # time.sleep(3)


        # print("Read")
        # print("-------------------------")
        # print(interface.read_asset(a))
        # time.sleep(3)

        # print("Create with consume")
        # print("-------------------------")
        # print(interface.consume_and_create(b, "Test 1", 100, [(a, 100), ("a00", 100), ]))
        # time.sleep(3)


        print("Consume")
        print("-------------------------")
        print(interface.consume(b, 100))
        time.sleep(3)


        print("get_all")
        print("-------------------------")
        print(interface.get_all_assets())