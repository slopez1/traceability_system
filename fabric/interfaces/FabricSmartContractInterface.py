from core.interfaces.SmartContractInterface import SmartContractInterface

import subprocess
import os
import json


class FabricSmartContractInterface(SmartContractInterface):

    def __init__(self, binary_path: str, fabric_cfg_path: str,
                 peer_msp_id: str, peer_msp_config_path: str, peer_tls_root_cert: str,
                 peer_address: str,
                 channel: str, chaincode: str,
                 orderer: list = [],
                 endorsement_peers: list = []):
        """
        :param binary_path: Path to fabric binaries
        :param fabric_cfg_path: Path to fabric config folder
        :param peer_msp_id: ID of local msp
        :param peer_msp_config_path: Path to user msp
        :param peer_tls_root_cert: Path to the public key of TLS-CA
        :param peer_address: Hostname and port of the current peer witch locate this code.

        :param channel: Channel where smart contract was locate
        :param chaincode: Chain code name to target


        :param orderer: Data to connect to the orderer:
                    ['endpoint', 'orderer_tls_hostname_override', 'tls_root_cert_files_orderer']
                    endpoint: It is the network address of a orderer together with its port, for example localhost:7050
                    orderer_tls_hostname_override: The hostname override to use when validating the TLS connection to
                    the orderer: orderer.example.com
                    tls_root_cert_files_orderer: The location of the tls CA public certificate used by the peer

        :param endorsement_peers: Nodes to point when endorsement will be required estruct:
                    [['addr_peer1', 'tls_root_cert_files_peer1'], ['addr_peer2', 'tls_root_cert_files_peer2'], ... ].
                        addr_peer: It is the network address of a peer together with its port, for example localhost:9051
                        tls_root_cert_files_peer: The location of the tls CA public certificate used by the peer



        """
        self.env = dict(os.environ)
        self.env['PATH'] = "$PATH:" + binary_path
        self.env['FABRIC_CFG_PATH'] = fabric_cfg_path
        self.env['CORE_PEER_TLS_ENABLED'] = "true"
        self.env['CORE_PEER_LOCALMSPID'] = peer_msp_id
        self.env['CORE_PEER_MSPCONFIGPATH'] = peer_msp_config_path
        self.env['CORE_PEER_TLS_ROOTCERT_FILE'] = peer_tls_root_cert
        self.env['CORE_PEER_ADDRESS'] = peer_address

        self.binary_path = binary_path
        self.channel = channel
        self.chaincode = chaincode
        self.orderer = orderer
        self.endorsement_peers = endorsement_peers

    def _generate_secure_command(self, command) -> str:
        base = "peer chaincode query -C {} -n {} -c ".format(self.channel, self.chaincode)
        return base + command

    def _generate_command_that_needs_to_fulfill_a_policy(self, command) -> str:
        base = "peer chaincode invoke -o {} --ordererTLSHostnameOverride {} --tls --cafile {} -C {} -n {} ".format(
            self.orderer[0],
            self.orderer[1],
            self.orderer[2],
            self.channel,
            self.chaincode)
        for peer in self.endorsement_peers:
            base = base + "--peerAddresses {} --tlsRootCertFiles {} ".format(peer[0], peer[1])

        base = base + "-c "
        return base + command

    def _clean_payload_response(self, unclean_response: str) -> str:
        response_string = unclean_response.replace('\\"', '"')
        if len(response_string) < 5:
            return ''
        json_data = json.loads(response_string)
        return json_data

    def _run_and_process_command(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, env=self.env)
        if result.stderr:
            if "Error" in result.stderr:
                print("Command: " + str(command))
                print("Error: " + str(result.stderr))
                raise Exception(result.stderr)
        return self._clean_payload_response(str(result.stdout))

    def create_asset(self, code: str, description: str, amount: int) -> str:
        command = self._generate_command_that_needs_to_fulfill_a_policy(
            '\'{"function":"' + self._get_function_names_map()[
                'create'] + '","Args":["' + code + '","' + description + '","' + str(amount) + '"]}\'')
        return self._run_and_process_command(command)


    def read_asset(self, code: str) -> str:
        command = self._generate_secure_command(
            '\'{"Args":["' + self._get_function_names_map()['read'] + '", "' + code + '"]}\'')
        return self._run_and_process_command(command)

    def get_all_assets(self) -> str:
        command = self._generate_secure_command('\'{"Args":["' + self._get_function_names_map()['all'] + '"]}\'')
        # print(command)
        return self._run_and_process_command(command)

    def consume_and_create(self, code: str, description: str, amount: int, assets_consumed: [(str, int)]) -> str:
        assets_consumed_modified = "["
        for asset in assets_consumed:
            assets_consumed_modified += "{\\\"ID\\\":\\\"" + asset[0] + "\\\",\\\"Amount\\\":" + str(asset[1]) + "},"
        assets_consumed_modified = assets_consumed_modified[:-1]
        assets_consumed_modified += "]"
        command = self._generate_command_that_needs_to_fulfill_a_policy(
            '\'{"function":"' + self._get_function_names_map()[
                'consume_and_create'] + '","Args":["' + code + '","' + description + '","' + str(amount) + '","' + str(assets_consumed_modified) + '"]}\'')
        return self._run_and_process_command(command)

    def propose_transfer(self, code: str, send_to: str) -> str:
        command = self._generate_command_that_needs_to_fulfill_a_policy(
            '\'{"function":"' + self._get_function_names_map()['propose_transfer'] + '","Args":["' + code + '","' + send_to + '"]}\'')
        return self._run_and_process_command(command)

    def accept_transfer(self, code: str) -> str:
        command = self._generate_command_that_needs_to_fulfill_a_policy(
            '\'{"function":"' + self._get_function_names_map()['accept_transfer'] + '","Args":["' + code +  '"]}\'')
        return self._run_and_process_command(command)

    def consume(self, code: str, amount: int) -> str:
        command = self._generate_command_that_needs_to_fulfill_a_policy(
            '\'{"function":"' + self._get_function_names_map()['consume'] + '","Args":["' + code + '","' + str(amount) + '"]}\'')
        return self._run_and_process_command(command)

    def history(self, code: str) -> str:
        command = self._generate_secure_command(
            '\'{"Args":["' + self._get_function_names_map()['history'] + '", "' + code + '"]}\'')
        return self._run_and_process_command(command)
