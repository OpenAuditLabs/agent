from locust import HttpUser, between, task


class AnalysisUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def submit_analysis(self):
        contract_code = """
        pragma solidity ^0.8.0;

        contract SimpleStorage {
            uint public storedData;

            function set(uint x) public {
                storedData = x;
            }

            function get() public view returns (uint) {
                return storedData;
            }
        }
        """
        self.client.post("/analysis/", json={"contract_code": contract_code})
