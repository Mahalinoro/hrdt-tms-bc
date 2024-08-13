'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

class MyWorkload extends WorkloadModuleBase {
    constructor() {
        super();
    }

    async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
        await super.initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext);
        for (let i = 0; i < roundArguments.initVehicles; i++) {
            const vehicleId = `vehicle_${workerIndex}_${i}`;
            const initScore = Math.random(); // Initialize with some random trust score
            const request = {
                contractId: 'basic', // Your chaincode name
                contractFunction: 'CreateVehicle',
                contractArguments: [vehicleId, initScore.toString()],
                timeout: 30
            };
            try {
                const result = await this.sutAdapter.sendRequests(request);
                console.log(`Successfully created vehicle: ${vehicleId}`, result);
            } catch (error) {
                console.error(`Error creating vehicle ${vehicleId}: ${error}`);
            }
        }
    }

    async submitTransaction() {
        const vehicleId = `vehicle_${this.workerIndex}_${Math.floor(Math.random() * this.roundArguments.initVehicles)}`;
        const newTrustScore = Math.random(); // Random new trust score
        const request = {
            contractId: 'basic', // Use the chaincode name as committed
            contractFunction: 'UpdateTrustScore',
            contractArguments: [vehicleId, newTrustScore.toString()],
            timeout: 30
        };

        try {
            const result = await this.sutAdapter.sendRequests(request);
            console.log(`Successfully updated trust score for ${vehicleId}: ${newTrustScore}`, result);
        } catch (error) {
            console.error(`Error updating trust score for ${vehicleId}: ${error}`);
        }
        
    }

    async cleanupWorkloadModule() {
        // Clean up resources by deleting all vehicles created during the test
        for (let i = 0; i < this.roundArguments.initVehicles; i++) {
            const vehicleId = `vehicle_${this.workerIndex}_${i}`;
            const request = {
                contractId: 'basic', // Your chaincode name
                contractFunction: 'DeleteVehicle',
                contractArguments: [vehicleId],
                timeout: 30
            };
            try {
                const result = await this.sutAdapter.sendRequests(request);
                console.log(`Successfully deleted vehicle: ${vehicleId}`, result);
            } catch (error) {
                console.error(`Error deleting vehicle ${vehicleId}: ${error}`);
            }
        }
    }
}

function createWorkloadModule() {
    return new MyWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule;