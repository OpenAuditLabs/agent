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
        unchecked {
            totalTokens += _amount;
        }
        // The vulnerability is that after an overflow, totalTokens might be <= MAX_TOKENS,
        // making this require pass when it shouldn't have.
        require(totalTokens <= MAX_TOKENS, "Exceeds max tokens after unchecked addition");
    }

    function burn(uint _amount) public {
        // Vulnerable: totalTokens - _amount can underflow if _amount is larger than totalTokens
        unchecked {
            totalTokens -= _amount;
        }
        // The vulnerability is that after an underflow, totalTokens might be a very large number,
        // making this require pass when it shouldn't have (if totalTokens was truly less than _amount).
        require(totalTokens >= _amount, "Not enough tokens after unchecked subtraction");
    }
}
