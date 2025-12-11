// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IntegerOverflow {
    uint public totalTokens;
    uint public MAX_TOKENS = 100;

    constructor() {
        totalTokens = 0;
    }

    function mint(uint _amount) public {
        // Vulnerable: _amount + totalTokens can overflow if _amount is large
        totalTokens += _amount;
        require(totalTokens <= MAX_TOKENS, "Exceeds max tokens");
    }

    function burn(uint _amount) public {
        // Vulnerable: totalTokens - _amount can underflow if _amount is larger than totalTokens
        require(totalTokens >= _amount, "Not enough tokens");
        totalTokens -= _amount;
    }
}
