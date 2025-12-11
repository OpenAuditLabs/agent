// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Reentrancy {
    mapping (address => uint) public balances;

    constructor() {
        balances[msg.sender] = 10 ether;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Withdrawal failed");

        balances[msg.sender] = 0; // Vulnerable: state update after external call
    }

    function getBalance(address _addr) public view returns (uint) {
        return balances[_addr];
    }
}
