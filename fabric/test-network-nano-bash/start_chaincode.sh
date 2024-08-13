#!/usr/bin/env sh
#
# SPDX-License-Identifier: Apache-2.0
#

# look for binaries in local dev environment /build/bin directory and then in local samples /bin directory
export PATH="${PWD}"/../../fabric/build/bin:"${PWD}"/../bin:"$PATH"


. ./peer1admin.sh

# Install Chaincode on Peer1
peer lifecycle chaincode package basic.tar.gz --path ../asset-transfer-basic/chaincode-go --lang golang --label basic_1 >> ./logs/start_chaincode.log 2>&1
peer lifecycle chaincode install basic.tar.gz >> ./logs/start_chaincode.log 2>&1

# Set the CHAINCODE_ID from the created chaincode package
CHAINCODE_ID=$(peer lifecycle chaincode calculatepackageid basic.tar.gz)
export CHAINCODE_ID

# Approve the chaincode using Peer1Admin
peer lifecycle chaincode approveformyorg -o 127.0.0.1:6050 --channelID mychannel --name basic --version 1 --package-id "${CHAINCODE_ID}" --sequence 1 --tls --cafile "${PWD}"/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt >> ./logs/start_chaincode.log 2>&1
peer lifecycle chaincode commit -o 127.0.0.1:6050 --channelID mychannel --name basic --version 1 --sequence 1 --tls --cafile "${PWD}"/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt >> ./logs/start_chaincode.log 2>&1

# # InitLedger
# peer chaincode invoke -o 127.0.0.1:6050 --tls --cafile "${PWD}"/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt -C mychannel -n basic --peerAddresses 127.0.0.1:7051 --tlsRootCertFiles "${PWD}"/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt -c '{"function":"InitLedger","Args":[]}'
