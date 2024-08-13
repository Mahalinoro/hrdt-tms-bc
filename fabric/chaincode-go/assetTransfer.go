/*
SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"log"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
	"github.com/hyperledger/fabric-samples/asset-transfer-basic/chaincode-go/chaincode"
)

func main() {
	assetChaincode, err := contractapi.NewChaincode(&chaincode.TrustManagementContract{})
	if err != nil {
		log.Panicf("Error creating trust management contract chaincode: %v", err)
	}

	if err := assetChaincode.Start(); err != nil {
		log.Panicf("Error starting trust management contract chaincode: %v", err)
	}
}
