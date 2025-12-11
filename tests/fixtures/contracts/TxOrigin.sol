// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TxOriginVulnerable {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: Using tx.origin for authentication
    // An attacker can trick the owner into sending a transaction to a malicious contract,
    // which then calls this withdrawAll function, draining the contract's funds.
    function withdrawAll(address payable _recipient) public {
        require(tx.origin == owner, "Not owner"); // Vulnerable line
        _recipient.transfer(address(this).balance);
    }

    function deposit() public payable {}
}
