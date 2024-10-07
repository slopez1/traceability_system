package chaincode

import (
	"encoding/json"
	"fmt"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)


type SmartContract struct {
	contractapi.Contract
}

type AssetConsumed struct {
	ID     string `json:"id"`
	Amount int    `json:"amount"`
}

type Asset struct {
    Code           string          `json:"code"`
    Description    string          `json:"description"`
    Owner          string          `json:"owner"`
    Creator        string          `json:"creator"`
    SendTo         string          `json:"send_to"`
    Amount         int             `json:"amount"`
    AssetsConsumed []AssetConsumed `json:"assets_consumed"`
    ConsumedOn     []AssetConsumed `json:"consumed_on"`
}


// AssetExists returns true when asset with given ID exists in world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, code string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(code)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return assetJSON != nil, nil
}

// GetAllAssets returns all assets found in world state
func (s *SmartContract) GetAllAssets(ctx contractapi.TransactionContextInterface) ([]*Asset, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()
	var assets []*Asset
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}
		var asset Asset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return nil, err
		}
		assets = append(assets, &asset)
	}
	return assets, nil
}


// CreateAsset issues a new asset to the world state with given details.
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, code string, description string, amount int) (*Asset, error)  {
	exists, err := s.AssetExists(ctx, code)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, fmt.Errorf("the asset %s already exists", code)
	}

    clientIdentity := ctx.GetClientIdentity()
    creator, err := clientIdentity.GetID()
    if err != nil {
        return nil, err
    }

	asset := Asset{
		Code:           code,
		Description:    description,
		Owner:          string(creator),
		Creator:        string(creator),
		SendTo:        "",
		Amount:         amount,
		AssetsConsumed: make([]AssetConsumed, 0),
		ConsumedOn:     make([]AssetConsumed, 0),
	}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return nil, err
	}
	return &asset,ctx.GetStub().PutState(code, assetJSON)
}

func (s *SmartContract) CreateAssetWithConsume(ctx contractapi.TransactionContextInterface, code string, description string, amount int, assetsConsumed []AssetConsumed) (*Asset, error)  {
	exists, err := s.AssetExists(ctx, code)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, fmt.Errorf("the asset %s already exists", code)
	}

	clientIdentity := ctx.GetClientIdentity()
	creator, err := clientIdentity.GetID()
	if err != nil {
		return nil, err
	}
    // Check if assetsConsumed  can be consumed (correct owner, and amount)
    for _, ac := range assetsConsumed {
		assetJSON, err := ctx.GetStub().GetState(ac.ID)
		if err != nil {
			return nil, fmt.Errorf("failed to get asset %s: %v", ac.ID, err)
		}
		if assetJSON == nil {
			return nil, fmt.Errorf("asset %s does not exist", ac.ID)
		}
		var asset Asset
		json.Unmarshal(assetJSON, &asset)
		if asset.Owner != creator {
			return nil, fmt.Errorf("asset %s is not owned by the requester", ac.ID)
		}
		if asset.Amount < ac.Amount {
			return nil, fmt.Errorf("insufficient amount for asset %s", ac.ID)
		}
	}

    for _, ac := range assetsConsumed {
		assetJSON, _ := ctx.GetStub().GetState(ac.ID) // Error handling omitted, checked previously
		var asset Asset
		json.Unmarshal(assetJSON, &asset)
		asset.Amount -= ac.Amount
		asset.ConsumedOn = append(asset.ConsumedOn, AssetConsumed{ID: code, Amount: ac.Amount})
		updatedAssetJSON, err := json.Marshal(asset)
		if err != nil {
			return nil, err
		}
		err = ctx.GetStub().PutState(ac.ID, updatedAssetJSON)
		if err != nil {
			return nil, fmt.Errorf("failed to update asset %s: %v", ac.ID, err)
		}
	}
    asset := Asset{
		Code:           code,
		Description:    description,
		Owner:          string(creator),
		Creator:        string(creator),
		SendTo:         "",
		Amount:         amount,
		AssetsConsumed: assetsConsumed,
		ConsumedOn:     make([]AssetConsumed, 0),
	}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return nil, err
	}


	return &asset, ctx.GetStub().PutState(code, assetJSON)
}


// ReadAsset returns the asset stored in the world state with given id.
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, code string) (*Asset, error) {
	assetJSON, err := ctx.GetStub().GetState(code)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("the asset %s does not exist", code)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	return &asset, err
}

func (s *SmartContract) ProposeTransfer(ctx contractapi.TransactionContextInterface, code string, sendTo string) (*Asset, error)  {
	assetJSON, err := ctx.GetStub().GetState(code)
	if err != nil {
		return nil, fmt.Errorf("failed to get asset %s: %v", code, err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("asset %s does not exist", code)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	clientIdentity := ctx.GetClientIdentity()
	ownerID, err := clientIdentity.GetID()
	if err != nil {
		return nil, err
	}

	if asset.Owner != ownerID {
		return nil, fmt.Errorf("asset %s is not owned by the requester", code)
	}

	// Actualizar el campo SendTo solo si el solicitante es el propietario
	asset.SendTo = sendTo
	updatedAssetJSON, err := json.Marshal(asset)
	if err != nil {
		return nil, err
	}

	err = ctx.GetStub().PutState(code, updatedAssetJSON)
	if err != nil {
		return nil, fmt.Errorf("failed to update asset %s: %v", code, err)
	}

	return &asset, err
}

func (s *SmartContract) AcceptTransfer(ctx contractapi.TransactionContextInterface, code string) (*Asset, error)  {
	assetJSON, err := ctx.GetStub().GetState(code)
	if err != nil {
		return nil, fmt.Errorf("failed to get asset %s: %v", code, err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("asset %s does not exist", code)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	clientIdentity := ctx.GetClientIdentity()
	newOwnerID, err := clientIdentity.GetID()
	if err != nil {
		return nil, err
	}

	if asset.SendTo != newOwnerID {
		return nil, fmt.Errorf("only the designated recipient can accept the transfer")
	}

	// Actualizar el propietario y reiniciar SendTo
	asset.Owner = newOwnerID
	asset.SendTo = ""

	updatedAssetJSON, err := json.Marshal(asset)
	if err != nil {
		return nil, err
	}

	err = ctx.GetStub().PutState(code, updatedAssetJSON)
	if err != nil {
		return nil, fmt.Errorf("failed to update asset %s: %v", code, err)
	}

	return &asset, err
}


func (s *SmartContract) ConsumeAsset(ctx contractapi.TransactionContextInterface, code string, amount int) (*Asset, error)  {
	assetJSON, err := ctx.GetStub().GetState(code)
	if err != nil {
		return nil, fmt.Errorf("failed to get asset %s: %v", code, err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("asset %s does not exist", code)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	clientIdentity := ctx.GetClientIdentity()
	currentOwnerID, err := clientIdentity.GetID()
	if err != nil {
		return nil, err
	}

	if asset.Owner != currentOwnerID {
		return nil, fmt.Errorf("asset %s can only be consumed by its owner", code)
	}

	if asset.Amount < amount {
		return nil, fmt.Errorf("insufficient amount available in asset %s", code)
	}

	// Actualizar el 'amount' del activo
	asset.Amount -= amount
    asset.ConsumedOn = append(asset.ConsumedOn, AssetConsumed{ID: code, Amount: amount})
	updatedAssetJSON, err := json.Marshal(asset)
	if err != nil {
		return nil, err
	}

	err = ctx.GetStub().PutState(code, updatedAssetJSON)
	if err != nil {
		return nil, fmt.Errorf("failed to update asset %s: %v", code, err)
	}

	return &asset, err
}


// FetchHistory returns all historical changes for a given asset code.
func (s *SmartContract) FetchAssetHistory(ctx contractapi.TransactionContextInterface, code string) (string, error) {
	resultsIterator, err := ctx.GetStub().GetHistoryForKey(code)
	if err != nil {
		return "", fmt.Errorf("failed to retrieve asset history for %s: %v", code, err)
	}
	defer resultsIterator.Close()

	// Slice for storing the historical records.
	var records []map[string]interface{}

	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return "", fmt.Errorf("failed to get next item from iterator: %v", err)
		}

		// Parse the historical state into a readable format
		var record map[string]interface{}
		if err := json.Unmarshal(response.Value, &record); err != nil {
			fmt.Println("Could not unmarshal record:", err)
		}

		// Append a history record including the transaction ID and value.
		historyRecord := map[string]interface{}{
			"TxId":      response.TxId,
			"Timestamp": response.Timestamp,
			"Record":    record,
			"IsDelete":  response.IsDelete,
		}
		records = append(records, historyRecord)
	}

	// Convert records slice to JSON
	historyJSON, err := json.Marshal(records)
	if err != nil {
		return "", fmt.Errorf("failed to encode JSON response: %v", err)
	}

	return string(historyJSON), nil
}












