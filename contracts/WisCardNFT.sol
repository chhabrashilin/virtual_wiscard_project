// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title WisCardNFT
 * @dev Soulbound (Non-Transferable) NFT for UW-Madison Virtual WisCard
 * Each student can mint exactly one NFT bound to their wallet address
 */
contract WisCardNFT is ERC721, Ownable {
    uint256 private tokenCounter = 0;

    // Mapping from token ID to wallet address (for verification)
    mapping(uint256 => address) public tokenToWallet;

    // Mapping from token ID to student data
    mapping(uint256 => StudentData) public studentData;

    // Mapping to track if token is soulbound (non-transferable)
    mapping(uint256 => bool) public isNonTransferable;

    // Mapping to track if a student ID already has an NFT
    mapping(uint256 => bool) public studentIdExists;

    struct StudentData {
        string studentName;
        uint256 studentId;
        string binaryRepresentation;
        string issueDate;
        string expiryDate;
        bytes barcodeData;
        address boundWallet;
    }

    event WisCardMinted(
        uint256 indexed tokenId,
        address indexed minter,
        uint256 studentId,
        string binaryRepresentation
    );

    event WisCardRevoked(uint256 indexed tokenId, address indexed owner);

    constructor() ERC721("UW-Madison WisCard", "WISCARD") {}

    /**
     * @dev Mint a new WisCard NFT (Soulbound to wallet)
     * @param _studentName Full name of the student
     * @param _studentId Numeric student ID
     * @param _binaryRepresentation Binary encoding of student ID
     * @param _issueDate Date of issue
     * @param _expiryDate Expiration date
     * @param _barcodeData PDF417 barcode binary data
     */
    function mintWisCard(
        string memory _studentName,
        uint256 _studentId,
        string memory _binaryRepresentation,
        string memory _issueDate,
        string memory _expiryDate,
        bytes memory _barcodeData
    ) public returns (uint256) {
        require(!studentIdExists[_studentId], "Student ID already has a WisCard NFT");
        require(bytes(_studentName).length > 0, "Student name required");
        require(_studentId > 0, "Valid student ID required");

        uint256 tokenId = tokenCounter;
        tokenCounter++;

        _safeMint(msg.sender, tokenId);
        tokenToWallet[tokenId] = msg.sender;

        studentData[tokenId] = StudentData({
            studentName: _studentName,
            studentId: _studentId,
            binaryRepresentation: _binaryRepresentation,
            issueDate: _issueDate,
            expiryDate: _expiryDate,
            barcodeData: _barcodeData,
            boundWallet: msg.sender
        });

        isNonTransferable[tokenId] = true;
        studentIdExists[_studentId] = true;

        emit WisCardMinted(tokenId, msg.sender, _studentId, _binaryRepresentation);
        return tokenId;
    }

    /**
     * @dev Override transfer functions to prevent transfers (Soulbound)
     */
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public override {
        require(!isNonTransferable[tokenId], "This WisCard is non-transferable (Soulbound)");
        super.transferFrom(from, to, tokenId);
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public override {
        require(!isNonTransferable[tokenId], "This WisCard is non-transferable (Soulbound)");
        super.safeTransferFrom(from, to, tokenId);
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) public override {
        require(!isNonTransferable[tokenId], "This WisCard is non-transferable (Soulbound)");
        super.safeTransferFrom(from, to, tokenId, data);
    }

    /**
     * @dev Verify that a wallet owns a specific WisCard token
     * @param tokenId The token ID to verify
     * @param walletAddress The wallet address to check
     */
    function verifyOwnership(uint256 tokenId, address walletAddress)
        public
        view
        returns (bool)
    {
        require(isNonTransferable[tokenId], "Token must be soulbound");
        return tokenToWallet[tokenId] == walletAddress && ownerOf(tokenId) == walletAddress;
    }

    /**
     * @dev Get student data for a token
     * @param tokenId The token ID to query
     */
    function getStudentData(uint256 tokenId) public view returns (StudentData memory) {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        return studentData[tokenId];
    }

    /**
     * @dev Admin function to revoke a WisCard (emergency use only)
     * @param tokenId The token ID to revoke
     */
    function revokeWisCard(uint256 tokenId) public onlyOwner {
        address owner = ownerOf(tokenId);
        require(owner != address(0), "Token does not exist");

        uint256 studentId = studentData[tokenId].studentId;
        studentIdExists[studentId] = false;

        _burn(tokenId);
        emit WisCardRevoked(tokenId, owner);
    }

    /**
     * @dev Get total number of WisCards minted
     */
    function getTotalMinted() public view returns (uint256) {
        return tokenCounter;
    }

    /**
     * @dev Check if an address owns any WisCard
     * @param owner Address to check
     */
    function getTokensByOwner(address owner) public view returns (uint256[] memory) {
        uint256 balance = balanceOf(owner);
        uint256[] memory tokens = new uint256[](balance);
        uint256 index = 0;

        for (uint256 i = 0; i < tokenCounter; i++) {
            if (ownerOf(i) == owner) {
                tokens[index] = i;
                index++;
            }
        }

        return tokens;
    }
}
