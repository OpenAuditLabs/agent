// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AccessControl {
    address public owner;
    uint public sensitiveData;

    constructor() {
        owner = msg.sender;
        sensitiveData = 0;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    // Vulnerable: Missing onlyOwner modifier, allowing any user to change sensitiveData
    function setSensitiveData(uint _data) public {
        sensitiveData = _data;
    }

    // Correctly protected function
    function changeOwner(address _newOwner) public onlyOwner {
        owner = _newOwner;
    }
}
