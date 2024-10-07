import asyncio
import re
import time

from django.core.management.base import BaseCommand
from fabric.interfaces.FabricSmartContractInterface import FabricSmartContractInterface
from traceability_system import settings


class Command(BaseCommand):
    help = "Test Fabric Speed (Needed command fabric_init_example_data)"

    def handle(self, *args, **options):
        ORGS = ["org1.example.com", "org2.example.com"]
        PEERS = ['peer0.org1.example.com', 'peer0.org2.example.com']
        self.cli = settings.FABRIC_CLIENT

        print(self.user.enrollment._cert)


        # loop = asyncio.get_event_loop()
        #
        # interface = FabricSmartContractInterface("User1", 1)
        #
        #
        # num = "01"
        #
        # a = "a"+num
        # b = "b" + num
        # print("Create")
        # print("-------------------------")
        # print(loop.run_until_complete(interface.create_asset("000", "0001", "10")))
        # time.sleep(1)


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


        # print("Consume")
        # print("-------------------------")
        # print(interface.consume(b, 100))
        # time.sleep(3)
        #
        #
        # print("get_all")
        # print("-------------------------")
        # print(loop.run_until_complete(interface.get_all_assets()))