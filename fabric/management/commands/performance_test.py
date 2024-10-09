import json
import time

from django.core.management.base import BaseCommand
from fabric.interfaces.FabricSmartContractInterface import FabricSmartContractInterface
from fabric.performance_test.PerformanceBlockChainTest import PerformanceBlockChainTest
from traceability_system import settings


class Command(BaseCommand):
    help = "Test Performance"


    def add_arguments(self, parser):
        # Adding a numeric argument to the command
        parser.add_argument('init_id', type=int, help='A numeric argument to be processed')


    def handle(self, *args, **kwargs):
        # ORGS = ["org1.example.com", "org2.example.com"]
        # PEERS = ['peer0.org1.example.com', 'peer0.org2.example.com']
        TEST_LATENCY = True
        TEST_RESPONSE_TIME = True
        TEST_THROUGHPUT = True

        self.cli = settings.FABRIC_CLIENT
        N = 5000 # Iterations
        init_id = kwargs['init_id']
        transfer_to_user = "eDUwOTo6Q049VXNlcjFAb3JnMS5leGFtcGxlLmNvbSxPVT1jbGllbnQsTD1TYW4gRnJhbmNpc2NvLFNUPUNhbGlmb3JuaWEsQz1VUzo6Q049Y2Eub3JnMS5leGFtcGxlLmNvbSxPPW9yZzEuZXhhbXBsZS5jb20sTD1TYW4gRnJhbmNpc2NvLFNUPUNhbGlmb3JuaWEsQz1VUw=="
        interface = FabricSmartContractInterface("User1", 1)

        # READ FUNCTIONS
        read = interface.read_asset
        all = interface.get_all_assets
        history = interface.history

        # CHANGE BLOCKCHAIN STATUS FUNCTIONS

        create = interface.create_asset
        consume_and_create = interface.consume_and_create
        propose = interface.propose_transfer
        accept = interface.accept_transfer
        consume = interface.consume

        def validate_create(loop, code, description, amount, consumed=None):
            result = None
            while True:
                result = loop.run_until_complete(read(code))
                try:
                    json_data = json.loads(result)
                    # Verificar si la clave 'code' no está en el JSON
                    if "code" in json_data:
                        result = json_data
                        break
                except Exception as e:
                    time.sleep(0.1)
            #print(str(result))

        def validate_transfer(loop, code, sent_to):
            result = None
            while True:
                result = loop.run_until_complete(read(code))
                try:
                    json_data = json.loads(result)
                    # Verificar si la clave 'code' no está en el JSON
                    if "send_to" in json_data and json_data["send_to"] != '':
                        result = json_data
                        # print("Transfer: " + str(result))
                        break
                except Exception as e:
                    time.sleep(0.1)
            #print(str(result))

        def validate_transfer_accept(loop, code):
            result = None
            while True:
                result = loop.run_until_complete(read(code))
                try:
                    json_data = json.loads(result)
                    # Verificar si la clave 'code' no está en el JSON
                    if "send_to" in json_data and json_data["send_to"] == '':
                        result = json_data
                        # print("Accept: " + str(result))
                        break
                except Exception as e:
                    time.sleep(0.1)

        def validate_consume(loop, code, amount):
            result = None
            while True:
                result = loop.run_until_complete(read(code))
                try:
                    json_data = json.loads(result)
                    # Verificar si la clave 'code' no está en el JSON
                    if "amount" in json_data and json_data["amount"] == 0:
                        result = json_data
                        # print("Consume: " + str(result))
                        break
                except Exception as e:
                    time.sleep(0.1)
            #print(str(result))


        def validate_create_throughtput(loop, code, description, amount):
            result = loop.run_until_complete(read(code))
            try:
                json_data = json.loads(result)
                # Verificar si la clave 'code' no está en el JSON
                if "code" in json_data:
                    return 1
            except Exception as e:
                pass
            return 0

        pt = PerformanceBlockChainTest()

        if TEST_RESPONSE_TIME:
            #########################
            #      RESPONSE TIME    #
            #########################


            # Create
            create_time = []
            for i in range(1, N):
                create_time.append(pt.latency(create, validate_create, str(init_id), str(init_id), 1))
                init_id += 1

            # Create and consume
            consume_and_create_time = []
            for i in range(1, N):
                consume_and_create_time.append(pt.latency(consume_and_create, validate_create, str(init_id), str(init_id), 1, [[str(init_id-1), 1]]))
                init_id += 1

            # Propose Transfer
            propose_time = [pt.latency(propose, validate_transfer, str(init_id-N+i), transfer_to_user) for i in range(1, N)]

            # Accept Transfer
            accept_time = [pt.latency(accept, validate_transfer_accept, str(init_id-N+i)) for i in range(1, N)]

            # Consume
            consume_time = [pt.latency(consume, validate_consume, str(init_id-N+i), 1) for i in range(1, N)]

            print()
            print()
            print("#####################")
            print("RESULT Response Time")
            print("#####################")
            print("###### Create ######")
            print(pt.time_statistics(create_time))
            print("###### Create and Consume ######")
            print(pt.time_statistics(consume_and_create_time))
            print("###### Propose Transfer ######")
            print(pt.time_statistics(propose_time))
            print("###### Accept Transfer ######")
            print(pt.time_statistics(accept_time))
            print("###### Consume ######")
            print(pt.time_statistics(consume_time))

        if TEST_LATENCY:
            #########################
            #      Latency TIME     #
            #########################

            # All Time
            all_time = [pt.response_time(all) for i in range(1, N)]

            # Read Time
            read_time = [pt.response_time(read, str(init_id-N+i)) for i in range(1, N)]

            # History Time
            history_time = [pt.response_time(history, str(init_id-N+i)) for i in range(1, N)]

            # Create
            create_response_time = []
            for i in range(1, N):
                create_response_time.append(pt.response_time(create, str(init_id), str(init_id), 1))
                init_id += 1

            # Create and consume
            consume_and_create_response_time = []
            for i in range(1, N):
                consume_and_create_response_time.append(
                    pt.response_time(consume_and_create, str(init_id), str(init_id), 1, [[str(init_id - 1), 1]]))
                init_id += 1

            # Propose Transfer
            propose_response_time = [pt.response_time(propose, str(init_id - N + i), transfer_to_user) for i in
                            range(1, N)]

            # Accept Transfer
            accept_response_time = [pt.response_time(accept, str(init_id - N + i)) for i in range(1, N)]

            # Consume
            consume_response_time = [pt.response_time(consume, str(init_id - N + i), 1) for i in range(1, N)]

            print()
            print()
            print("#####################")
            print("RESULT Latency")
            print("#####################")

            print("###### All ######")
            print(pt.time_statistics(all_time))

            print("###### Read ######")
            print(pt.time_statistics(read_time))

            print("###### HISTORY ######")
            print(pt.time_statistics(history_time))
            print("###### Create ######")
            print(pt.time_statistics(create_response_time))
            print("###### Create and Consume ######")
            print(pt.time_statistics(consume_and_create_response_time))
            print("###### Propose Transfer ######")
            print(pt.time_statistics(propose_response_time))
            print("###### Accept Transfer ######")
            print(pt.time_statistics(accept_response_time))
            print("###### Consume ######")
            print(pt.time_statistics(consume_response_time))
        total = 0
        if TEST_THROUGHPUT:
            def create_generator(init_value):
                while True:
                    yield [str(init_value), str(init_value), 1]
                    init_value += 1

            throughput_time = 3600
            throughput_time_wait_until_validation = 120

            total, correct = pt.throughput_serial(create, validate_create_throughtput, create_generator(init_id), throughput_time, throughput_time_wait_until_validation)

            print()
            print()
            print("#####################")
            print("RESULT Throughput")
            print("#####################")

            print("###### Create  ######")
            print(str({
                'Time': throughput_time,
                'Total': total,
                'Correct': correct
            }))

        print()
        print()
        init_id += total + 1
        print("Last id: " + str(init_id))




