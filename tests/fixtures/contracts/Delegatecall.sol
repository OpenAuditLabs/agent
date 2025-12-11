// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LibraryContract {
    uint public value;
    address public owner;

    function setVar(uint _value) public {
        value = _value;
    }

    function setOwner(address _owner) public {
        owner = _owner;
    }

    function doSomething() public returns (bool) {
        // This function will execute in the context of the calling contract
        // If called via delegatecall, 'owner' and 'value' will refer to the calling contract's state
        return true;
    }
}

contract DelegatecallVulnerable {
    uint public value;
    address public owner;
    LibraryContract public lib;

    constructor(address _lib) {
        lib = LibraryContract(_lib);
        owner = msg.sender;
        value = 100;
    }

    // Vulnerable: Allows an attacker to call arbitrary functions on the LibraryContract
    // and potentially modify the state of DelegatecallVulnerable.
    function upgrade(bytes calldata _data) public {
        (bool success, ) = address(lib).delegatecall(_data);
        require(success, "Delegatecall failed");
    }
}
