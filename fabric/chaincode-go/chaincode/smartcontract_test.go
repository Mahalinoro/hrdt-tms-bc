package chaincode_test

import (
	"encoding/json"
	"fmt"
	"testing"

	"github.com/hyperledger/fabric-chaincode-go/v2/shim"
	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
	"github.com/hyperledger/fabric-protos-go-apiv2/ledger/queryresult"
	"github.com/hyperledger/fabric-samples/asset-transfer-basic/chaincode-go/chaincode"
	"github.com/hyperledger/fabric-samples/asset-transfer-basic/chaincode-go/chaincode/mocks"
	"github.com/stretchr/testify/require"
)

//go:generate counterfeiter -o mocks/transaction.go -fake-name TransactionContext . transactionContext
type transactionContext interface {
	contractapi.TransactionContextInterface
}

//go:generate counterfeiter -o mocks/chaincodestub.go -fake-name ChaincodeStub . chaincodeStub
type chaincodeStub interface {
	shim.ChaincodeStubInterface
}

//go:generate counterfeiter -o mocks/statequeryiterator.go -fake-name StateQueryIterator . stateQueryIterator
type stateQueryIterator interface {
	shim.StateQueryIteratorInterface
}

func TestInitLedger(t *testing.T) {
	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	assetTransfer := chaincode.TrustManagementContract{}
	err := assetTransfer.InitLedger(transactionContext)
	require.NoError(t, err)

	chaincodeStub.PutStateReturns(fmt.Errorf("failed inserting key"))
	err = assetTransfer.InitLedger(transactionContext)
	require.EqualError(t, err, "failed to put to world state. failed inserting key")
}

func TestCreateVehicle(t *testing.T) {
	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	assetTransfer := chaincode.TrustManagementContract{}
	err := assetTransfer.CreateVehicle(transactionContext, "24", 0.76)
	require.NoError(t, err)

	chaincodeStub.GetStateReturns([]byte{}, nil)
	err = assetTransfer.CreateVehicle(transactionContext, "9", 0.65)
	require.EqualError(t, err, "the asset 9 already exists")
}

func TestReadAsset(t *testing.T) {
	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	expectedAsset := &chaincode.Vehicle{ID: "9"}
	bytes, err := json.Marshal(expectedAsset)
	require.NoError(t, err)

	chaincodeStub.GetStateReturns(bytes, nil)
	assetTransfer := chaincode.TrustManagementContract{}
	asset, err := assetTransfer.ReadVehicle(transactionContext, "")
	require.NoError(t, err)
	require.Equal(t, expectedAsset, asset)

	chaincodeStub.GetStateReturns(nil, fmt.Errorf("unable to retrieve asset"))
	_, err = assetTransfer.ReadVehicle(transactionContext, "")
	require.EqualError(t, err, "failed to read from world state: unable to retrieve asset")

	chaincodeStub.GetStateReturns(nil, nil)
	asset, err = assetTransfer.ReadVehicle(transactionContext, "asset1")
	require.EqualError(t, err, "the vehicle with ID asset1 does not exist")
	require.Nil(t, asset)
}

func TestUpdateTrustScore(t *testing.T) {
	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	expectedAsset := &chaincode.Vehicle{ID: "9"}
	bytes, err := json.Marshal(expectedAsset)
	require.NoError(t, err)

	chaincodeStub.GetStateReturns(bytes, nil)
	assetTransfer := chaincode.TrustManagementContract{}
	err = assetTransfer.UpdateTrustScore(transactionContext, "9", 0.6)
	require.NoError(t, err)

	chaincodeStub.GetStateReturns(nil, nil)
	err = assetTransfer.UpdateTrustScore(transactionContext, "87", 0.89)
	require.EqualError(t, err, "the vehicle with ID 87 does not exist")

}

func TestDeleteAsset(t *testing.T) {
	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	asset := &chaincode.Vehicle{ID: "9"}
	bytes, err := json.Marshal(asset)
	require.NoError(t, err)

	chaincodeStub.GetStateReturns(bytes, nil)
	chaincodeStub.DelStateReturns(nil)
	assetTransfer := chaincode.TrustManagementContract{}
	err = assetTransfer.DeleteVehicle(transactionContext, "9")
	require.NoError(t, err)

	chaincodeStub.GetStateReturns(nil, nil)
	err = assetTransfer.DeleteVehicle(transactionContext, "10")
	require.EqualError(t, err, "the asset 10 does not exist")
}

func TestGetAllAssets(t *testing.T) {
	asset := &chaincode.Vehicle{ID: "9"}
	bytes, err := json.Marshal(asset)
	require.NoError(t, err)

	iterator := &mocks.StateQueryIterator{}
	iterator.HasNextReturnsOnCall(0, true)
	iterator.HasNextReturnsOnCall(1, false)
	iterator.NextReturns(&queryresult.KV{Value: bytes}, nil)

	chaincodeStub := &mocks.ChaincodeStub{}
	transactionContext := &mocks.TransactionContext{}
	transactionContext.GetStubReturns(chaincodeStub)

	chaincodeStub.GetStateByRangeReturns(iterator, nil)
	assetTransfer := &chaincode.TrustManagementContract{}
	assets, err := assetTransfer.GetAllVehicles(transactionContext)
	require.NoError(t, err)
	require.Equal(t, []*chaincode.Vehicle{asset}, assets)

	iterator.HasNextReturns(true)
	iterator.NextReturns(nil, fmt.Errorf("failed retrieving next item"))
	assets, err = assetTransfer.GetAllVehicles(transactionContext)
	require.EqualError(t, err, "failed to read data from iterator: failed retrieving next item")
	require.Nil(t, assets)
}
