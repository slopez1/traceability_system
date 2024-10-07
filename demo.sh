#!/bin/bash

ROOT_PWD=$(pwd)
FABRIC_DIR=$ROOT_PWD'/FabricContainerSetup'

echo "Checking if fabric is present..."
if [ ! -d $FABRIC_DIR"/fabric-samples" ]; then
  echo "Fabric not found, initializing..."
  cd $FABRIC_DIR
  if ! ./install-fabric.sh d s b; then
      echo "Fabric installation failed"
      exit 1
  fi
  cd ..
  echo "Fabric initialized"
else
  echo "Fabric found"
fi

echo "Checking if docker is present..."
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed, this is required to work, please install it"
  exit 1
else
  echo "Docker is installed"
fi

SAMPLE_CONFIG_DIRECTORY=$FABRIC_DIR"/fabric-samples/test-network"
export PATH=$ROOT_PWD"/FabricContainerSetup/fabric-samples/bin:"$PATH
export FABRIC_CFG_PATH=$ROOT_PWD"/FabricContainerSetup/fabric-samples/config/"



change_user() {
  awk -v new_count="$2" '
  /Users:/ { print; found=1; next }
  found && /Count:/ { sub(/[0-9]+/, new_count); found=0 }
  { print }
  ' "$1" > temp.yaml && mv temp.yaml "$1"
}

echo "Adding users to be created"
YAML_ORG_1=$SAMPLE_CONFIG_DIRECTORY"/organizations/cryptogen/crypto-config-org1.yaml"
YAML_ORG_2=$SAMPLE_CONFIG_DIRECTORY"/organizations/cryptogen/crypto-config-org2.yaml"

N_USERS=100


change_user $YAML_ORG_1 $N_USERS
change_user $YAML_ORG_2 $N_USERS




echo "Starting the Fabric network in Docker"
# Rese network
cd $SAMPLE_CONFIG_DIRECTORY
./network.sh down
if ! ./network.sh up -bft; then
    echo "Starting the Fabric network failed, please check logs"
    exit 1
fi
./network.sh createChannel
echo "Fabric network started"




# Variables
CHANNEL_NAME="mychannel"
ORDERER_CA="$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

# Array of chaincodes
CHAINCODES=("SmartContract")


CHAINCODE_DIR=$ROOT_PWD"/chaincodes"

SEQUENCE=1
for CHAINCODE_NAME in "${CHAINCODES[@]}"
do
    echo "___________________________________________________________"
    echo "___________________________________________________________"
    echo "___________________________________________________________"
    echo $CHAINCODE_NAME
    echo "___________________________________________________________"
    echo "___________________________________________________________"
    echo "___________________________________________________________"

    CHAINCODE_SRC="${CHAINCODE_DIR}/${CHAINCODE_NAME}"
    CHAINCODE_LABEL="${CHAINCODE_NAME}_1.0"
    CHAINCODE_PACKAGE="${CHAINCODE_NAME}.tar.gz"
    echo "Packaging chaincode dir ${CHAINCODE_SRC}"
    # Package chaincode
    echo "Packaging chaincode ${CHAINCODE_NAME}"
    TMP_PWD=$SAMPLE_CONFIG_DIRECTORY
    cd ${CHAINCODE_SRC}
    GO111MODULE=on go mod vendor
    cd $TMP_PWD


    peer lifecycle chaincode package SmartContract.tar.gz --path /Users/sergilopezsorribes/Documents/traceability_system/chaincodes/SmartContract --lang golang --label SmartContract_1.0


    peer lifecycle chaincode package ${CHAINCODE_PACKAGE} --path ${CHAINCODE_SRC} --lang golang --label ${CHAINCODE_LABEL}
    ### LOAD CHAINCODE TO ORGS ###
    export CORE_PEER_TLS_ENABLED=true
    export CORE_PEER_LOCALMSPID="Org1MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
    export CORE_PEER_MSPCONFIGPATH=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
    export CORE_PEER_ADDRESS=localhost:7051

    # Install chaincode
    echo "Installing chaincode ${CHAINCODE_NAME}"
    echo "Intalling on Org1MSP"
    peer lifecycle chaincode install ${CHAINCODE_PACKAGE}


    export CORE_PEER_LOCALMSPID="Org2MSP"
    export CORE_PEER_TLS_ROOTCERT_FILE=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
    export CORE_PEER_MSPCONFIGPATH=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
    export CORE_PEER_ADDRESS=localhost:9051
    echo "Installing chaincode ${CHAINCODE_NAME}"
    echo "Intalling on Org2MSP"
    peer lifecycle chaincode install ${CHAINCODE_PACKAGE}

    echo $(peer lifecycle chaincode queryinstalled)
    CC_PACKAGE_ID=$(peer lifecycle chaincode queryinstalled | grep "${CHAINCODE_LABEL}" | awk -F '[, ]+' '{print $3}')

    echo "Package ID: ${CC_PACKAGE_ID}"

    echo "Aprove chaincode ${CHAINCODE_NAME}"
    echo "Aprove on Org2MSP"
    echo "Approving chaincode ${CHAINCODE_NAME} with sequence ${SEQUENCE}"
    peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name ${CHAINCODE_NAME} --version 1.0 --package-id $CC_PACKAGE_ID --sequence ${SEQUENCE} --tls --cafile "$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" 

    export CORE_PEER_LOCALMSPID="Org1MSP"
    export CORE_PEER_MSPCONFIGPATH=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
    export CORE_PEER_TLS_ROOTCERT_FILE=$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
    export CORE_PEER_ADDRESS=localhost:7051

    echo "Aprove chaincode ${CHAINCODE_NAME}"
    echo "Aprove on Org1MSP"
    echo "Approving chaincode ${CHAINCODE_NAME} with sequence ${SEQUENCE}"
    peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name ${CHAINCODE_NAME} --version 1.0 --package-id $CC_PACKAGE_ID --sequence ${SEQUENCE} --tls --cafile "$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" 


    # Commit chaincode
    peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name ${CHAINCODE_NAME} --version 1.0 --sequence ${SEQUENCE} --tls --cafile "$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --output json 
    peer lifecycle chaincode commit -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name ${CHAINCODE_NAME} --version 1.0 --sequence ${SEQUENCE} --tls --cafile "$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --peerAddresses localhost:7051 --tlsRootCertFiles "$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" 
    peer lifecycle chaincode querycommitted --channelID mychannel --name ${CHAINCODE_NAME}



    echo "InitLedger for ${CHAINCODE_NAME}"
    peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "$SAMPLE_CONFIG_DIRECTORY/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n ${CHAINCODE_NAME} --peerAddresses localhost:7051 --tlsRootCertFiles "$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "$SAMPLE_CONFIG_DIRECTORY/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{"function":"GetAllAssets","Args":[]}'


done


echo "#########################################################"
echo "#                                                       #"
echo "# REMEMBER EXECUTE WITH:"
echo "# uvicorn traceability_system.asgi:application --reload #"
echo "#                                                       #"
echo "#########################################################"