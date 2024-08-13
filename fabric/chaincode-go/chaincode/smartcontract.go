package chaincode

import (
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

// SmartContract provides functions for managing an Asset
type TrustManagementContract struct {
	contractapi.Contract
}

// Asset describes basic details of what makes up a simple asset
// Insert struct field in alphabetic order => to achieve determinism across languages
// golang keeps the order when marshal to json but doesn't order automatically

// trust score is float
type Vehicle struct {
	ID             string `json:"ID"`
	TrustScore	   float64 `json:"TrustScore"`	 
}

// InitLedger adds a base set of assets to the ledger
// func (s *TrustManagementContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
// 	vehicles := []Vehicle{
// 		{ID: "9", TrustScore: 0.75},
// 		{ID: "14", TrustScore: 0.86},
// 		{ID: "21", TrustScore: 0.75},
// 		{ID: "1221", TrustScore: 0.86},
// 	}

// 	for _, vehicle := range vehicles {
// 		vehicleJSON, err := json.Marshal(vehicle)
// 		if err != nil {
// 			return fmt.Errorf("failed to marshal asset: %v", err)
// 		}

// 		err = ctx.GetStub().PutState(vehicle.ID, vehicleJSON)
// 		if err != nil {
// 			return fmt.Errorf("failed to put to world state. %v", err)
// 		}
// 	}

// 	return nil
// }

// CreateAsset issues a new asset to the world state with given details.
func (s *TrustManagementContract) CreateVehicle(ctx contractapi.TransactionContextInterface, id string, tscore string) error {
	exists, err := s.VehicleExists(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if exists {
		return fmt.Errorf("the asset %s already exists", id)
	}

	tscoreFloat, err := strconv.ParseFloat(tscore, 64)
	if err != nil {
		return fmt.Errorf("failed to parse TrustScore: %v", err)
	}

	vehicle := Vehicle{
		ID:             id,
		TrustScore:     tscoreFloat,
	}
	vehicleJSON, err := json.Marshal(vehicle)
	if err != nil {
		return fmt.Errorf("failed to marshal asset: %v", err)
	}

	return ctx.GetStub().PutState(id, vehicleJSON)
}

// ReadAsset returns the asset stored in the world state with given id.
func (s *TrustManagementContract) ReadVehicle(ctx contractapi.TransactionContextInterface, id string) (*Vehicle, error) {
	vehicleJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if vehicleJSON == nil {
		return nil, fmt.Errorf("the vehicle with ID %s does not exist", id)
	}

	var vehicle Vehicle
	err = json.Unmarshal(vehicleJSON, &vehicle)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal asset: %v", err)
	}

	return &vehicle, nil
}

// UpdateAsset updates an existing asset in the world state with provided parameters.
func (s *TrustManagementContract) UpdateTrustScore(ctx contractapi.TransactionContextInterface, id string, tscore string) error {
	exists, err := s.VehicleExists(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if !exists {
		return fmt.Errorf("the vehicle with ID %s does not exist", id)
	}

	// Convert tscore to float64
	tscoreFloat, err := strconv.ParseFloat(tscore, 64)
	if err != nil {
		return fmt.Errorf("failed to parse TrustScore: %v", err)
	}
	
	// overwriting original asset with new asset
	vehicle := Vehicle{
		ID:             id,
		TrustScore:     tscoreFloat,
	}
	vehicleJSON, err := json.Marshal(vehicle)
	if err != nil {
		return fmt.Errorf("failed to marshal asset: %v", err)
	}

	return ctx.GetStub().PutState(id, vehicleJSON)
}

// DeleteAsset deletes an given asset from the world state.
func (s *TrustManagementContract) DeleteVehicle(ctx contractapi.TransactionContextInterface, id string) error {
	exists, err := s.VehicleExists(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if !exists {
		return fmt.Errorf("the asset %s does not exist", id)
	}

	return ctx.GetStub().DelState(id)
}

// AssetExists returns true when asset with given ID exists in world state
func (s *TrustManagementContract) VehicleExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	vehicleJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return vehicleJSON != nil, nil
}


// GetAllAssets returns all assets found in world state
func (s *TrustManagementContract) GetAllVehicles(ctx contractapi.TransactionContextInterface) ([]*Vehicle, error) {
	// range query with empty string for startKey and endKey does an
	// open-ended query of all assets in the chaincode namespace.
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	defer resultsIterator.Close()

	var assets []*Vehicle
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, fmt.Errorf("failed to read data from iterator: %v", err)
		}

		var vehicle Vehicle
		err = json.Unmarshal(queryResponse.Value, &vehicle)
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal asset: %v", err)
		}
		assets = append(assets, &vehicle)
	}

	return assets, nil
}
