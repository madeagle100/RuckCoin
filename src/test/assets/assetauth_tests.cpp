// Copyright (c) 2021 The Raven Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <assets/assets.h>

#include <test/test_raven.h>

#include <boost/test/unit_test.hpp>

#include <amount.h>
#include <base58.h>
#include <chainparams.h>
#include <script/standard.h>
#include <consensus/validation.h>
#include <consensus/tx_verify.h>
#include <validation.h>

BOOST_FIXTURE_TEST_SUITE(assetauth_tests, BasicTestingSetup)

    // Helper: build a preimage for the given names (sorted automatically)
    static CAssetAuthPreimage MakePreimage(uint8_t nRequired, std::vector<std::string> vNames)
    {
        std::sort(vNames.begin(), vNames.end());
        return CAssetAuthPreimage(nRequired, vNames);
    }

    // Helper: build a P2AH base scriptPubKey for a preimage
    static CScript MakeP2AHScript(const CAssetAuthPreimage& preimage)
    {
        CScript script;
        preimage.ConstructTransaction(script);
        return script;
    }

    // Helper: build the scriptSig (single push of the serialized preimage)
    static CScript MakeP2AHScriptSig(const CAssetAuthPreimage& preimage)
    {
        CDataStream ss(SER_NETWORK, PROTOCOL_VERSION);
        ss << preimage;
        std::vector<unsigned char> vchPreimage(ss.begin(), ss.end());
        return CScript() << vchPreimage;
    }

    // Helper: a P2PKH script to use as a generic key-protected destination
    static CScript MakeKeyScript()
    {
        return GetScriptForDestination(DecodeDestination(GetParams().GlobalBurnAddress()));
    }

    // Helper: add a coin to the view, returning its outpoint
    static COutPoint AddCoin(CCoinsViewCache& coins, const CScript& scriptPubKey, CAmount nValue, uint32_t n)
    {
        CTxOut txOut;
        txOut.nValue = nValue;
        txOut.scriptPubKey = scriptPubKey;
        uint256 hash = uint256S(strprintf("%064x", 0xdeadbeef00 + n));
        COutPoint outpoint(hash, n);
        coins.AddCoin(outpoint, Coin(txOut, 10, 0), true);
        return outpoint;
    }

    BOOST_AUTO_TEST_CASE(preimage_validation_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Preimage Validation Test");

        std::string strError;

        // Valid 1-of-1
        CAssetAuthPreimage p1 = MakePreimage(1, {"ALPHA!"});
        BOOST_CHECK_MESSAGE(p1.IsValid(strError), strError);

        // Valid 2-of-3
        CAssetAuthPreimage p2 = MakePreimage(2, {"ALPHA!", "BETA!", "GAMMA!"});
        BOOST_CHECK_MESSAGE(p2.IsValid(strError), strError);

        // Invalid: zero required
        CAssetAuthPreimage p3 = MakePreimage(0, {"ALPHA!"});
        BOOST_CHECK(!p3.IsValid(strError));

        // Invalid: required more than available
        CAssetAuthPreimage p4 = MakePreimage(2, {"ALPHA!"});
        BOOST_CHECK(!p4.IsValid(strError));

        // Invalid: empty list
        CAssetAuthPreimage p5(1, {});
        BOOST_CHECK(!p5.IsValid(strError));

        // Invalid: not an owner asset name
        CAssetAuthPreimage p6 = MakePreimage(1, {"ALPHA"});
        BOOST_CHECK(!p6.IsValid(strError));

        // Invalid: duplicate names
        CAssetAuthPreimage p7(1, {"ALPHA!", "ALPHA!"});
        BOOST_CHECK(!p7.IsValid(strError));

        // Invalid: unsorted names
        CAssetAuthPreimage p8(1, {"BETA!", "ALPHA!"});
        BOOST_CHECK(!p8.IsValid(strError));

        // Invalid: more than MAX_ASSET_AUTH_NAMES
        std::vector<std::string> vTooMany;
        for (int i = 0; i < MAX_ASSET_AUTH_NAMES + 1; i++)
            vTooMany.push_back(strprintf("ASSET_%02d!", i));
        CAssetAuthPreimage p9 = MakePreimage(1, vTooMany);
        BOOST_CHECK(!p9.IsValid(strError));
    }

    BOOST_AUTO_TEST_CASE(preimage_serialization_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Preimage Serialization Test");

        CAssetAuthPreimage p1 = MakePreimage(2, {"ALPHA!", "BETA!", "GAMMA!"});

        // Round trip through serialization
        CDataStream ss(SER_NETWORK, PROTOCOL_VERSION);
        ss << p1;
        CAssetAuthPreimage p2;
        ss >> p2;

        BOOST_CHECK_EQUAL(p1.nRequired, p2.nRequired);
        BOOST_CHECK(p1.vOwnerAssetNames == p2.vOwnerAssetNames);
        BOOST_CHECK(p1.GetHash() == p2.GetHash());

        // Same set of names always produces the same hash (canonical)
        CAssetAuthPreimage p3 = MakePreimage(2, {"GAMMA!", "ALPHA!", "BETA!"});
        BOOST_CHECK(p1.GetHash() == p3.GetHash());

        // Different m produces a different hash
        CAssetAuthPreimage p4 = MakePreimage(3, {"ALPHA!", "BETA!", "GAMMA!"});
        BOOST_CHECK(p1.GetHash() != p4.GetHash());
    }

    BOOST_AUTO_TEST_CASE(script_recognition_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Script Recognition Test");

        SelectParams(CBaseChainParams::MAIN);

        CAssetAuthPreimage preimage = MakePreimage(1, {"ALPHA!"});
        CScript script = MakeP2AHScript(preimage);

        // The base script is exactly 25 bytes
        BOOST_CHECK_EQUAL(script.size(), 25);

        // Recognized as P2AH, not as P2PKH or P2SH
        BOOST_CHECK(script.IsPayToAssetAuthHash());
        BOOST_CHECK(script.IsAssetAuthScript());
        BOOST_CHECK(!script.IsPayToPublicKeyHash());
        BOOST_CHECK(!script.IsPayToScriptHash());

        // Solver classifies it as TX_ASSET_AUTH and extracts the hash
        txnouttype whichType;
        std::vector<std::vector<unsigned char> > vSolutions;
        BOOST_CHECK(Solver(script, whichType, vSolutions));
        BOOST_CHECK_EQUAL(whichType, TX_ASSET_AUTH);
        BOOST_CHECK(uint160(vSolutions[0]) == preimage.GetHash());

        // ExtractDestination returns a CAssetAuthID
        CTxDestination dest;
        BOOST_CHECK(ExtractDestination(script, dest));
        const CAssetAuthID* id = boost::get<CAssetAuthID>(&dest);
        BOOST_CHECK(id != nullptr);
        BOOST_CHECK(*id == CAssetAuthID(preimage.GetHash()));

        // GetScriptForDestination round-trips
        CScript script2 = GetScriptForDestination(dest);
        BOOST_CHECK(script == script2);

        // Address encode/decode round-trips
        std::string address = EncodeDestination(dest);
        CTxDestination decoded = DecodeDestination(address);
        BOOST_CHECK(IsValidDestination(decoded));
        const CAssetAuthID* decodedId = boost::get<CAssetAuthID>(&decoded);
        BOOST_CHECK(decodedId != nullptr && *decodedId == *id);

        // AssetAuthHashFromScript extracts the committed hash
        uint160 hash;
        BOOST_CHECK(AssetAuthHashFromScript(script, hash));
        BOOST_CHECK(hash == preimage.GetHash());

        // P2AH script with asset transfer data appended is still an asset auth script
        // and is also recognized as an asset script (so asset accounting works)
        CScript assetScript = MakeP2AHScript(preimage);
        CAssetTransfer transfer("SOMEASSET", 100 * COIN);
        transfer.ConstructTransaction(assetScript);
        BOOST_CHECK(assetScript.IsAssetAuthScript());
        BOOST_CHECK(!assetScript.IsPayToAssetAuthHash()); // not the bare form
        BOOST_CHECK(assetScript.IsAssetScript());
        BOOST_CHECK(assetScript.IsTransferAsset());

        // ExtractDestination on the asset-carrying P2AH script returns the P2AH address
        CTxDestination assetDest;
        BOOST_CHECK(ExtractDestination(assetScript, assetDest));
        const CAssetAuthID* assetId = boost::get<CAssetAuthID>(&assetDest);
        BOOST_CHECK(assetId != nullptr && *assetId == *id);
    }

    BOOST_AUTO_TEST_CASE(scriptsig_parsing_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH ScriptSig Parsing Test");

        CAssetAuthPreimage preimage = MakePreimage(2, {"ALPHA!", "BETA!", "GAMMA!"});
        CScript scriptSig = MakeP2AHScriptSig(preimage);

        // Round-trips through the scriptSig parser
        CAssetAuthPreimage parsed;
        BOOST_CHECK(AssetAuthPreimageFromScriptSig(scriptSig, parsed));
        BOOST_CHECK_EQUAL(parsed.nRequired, preimage.nRequired);
        BOOST_CHECK(parsed.vOwnerAssetNames == preimage.vOwnerAssetNames);

        // Empty scriptSig fails
        CAssetAuthPreimage dummy;
        BOOST_CHECK(!AssetAuthPreimageFromScriptSig(CScript(), dummy));

        // scriptSig with two pushes fails (must be exactly one)
        CScript twoPushes = MakeP2AHScriptSig(preimage);
        twoPushes << std::vector<unsigned char>{0x01};
        BOOST_CHECK(!AssetAuthPreimageFromScriptSig(twoPushes, dummy));

        // scriptSig with garbage data fails
        CScript garbage = CScript() << std::vector<unsigned char>{0xde, 0xad, 0xbe, 0xef};
        BOOST_CHECK(!AssetAuthPreimageFromScriptSig(garbage, dummy));
    }

    BOOST_AUTO_TEST_CASE(authorization_valid_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization Valid Test");

        SelectParams(CBaseChainParams::MAIN);

        CAssetAuthPreimage preimage = MakePreimage(1, {"ALPHA!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        // Coin 1: a P2AH output holding RVN
        COutPoint p2ahOutpoint = AddCoin(coins, MakeP2AHScript(preimage), 50 * COIN, 1);

        // Coin 2: the ALPHA! owner token at a key-protected address
        CScript ownerScript = MakeKeyScript();
        CAssetTransfer ownerTransfer("ALPHA!", OWNER_ASSET_AMOUNT);
        ownerTransfer.ConstructTransaction(ownerScript);
        COutPoint ownerOutpoint = AddCoin(coins, ownerScript, 0, 2);

        // Spending tx: P2AH input + owner token input; owner token moves to an output
        CMutableTransaction mutTx;

        CTxIn p2ahIn;
        p2ahIn.prevout = p2ahOutpoint;
        p2ahIn.scriptSig = MakeP2AHScriptSig(preimage);
        mutTx.vin.push_back(p2ahIn);

        CTxIn ownerIn;
        ownerIn.prevout = ownerOutpoint;
        mutTx.vin.push_back(ownerIn);

        // Outputs: RVN destination + owner token moves on
        mutTx.vout.push_back(CTxOut(50 * COIN, MakeKeyScript()));
        CScript ownerOutScript = MakeKeyScript();
        ownerTransfer.ConstructTransaction(ownerOutScript);
        mutTx.vout.push_back(CTxOut(0, ownerOutScript));

        CTransaction tx(mutTx);

        // The P2AH input is authorized: ALPHA! is present from a key-protected input
        std::string strError;
        BOOST_CHECK_MESSAGE(CheckTxAssetAuthInputs(tx, coins, strError), strError);
    }

    BOOST_AUTO_TEST_CASE(authorization_no_movement_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization No Movement Test");

        SelectParams(CBaseChainParams::MAIN);

        CAssetAuthPreimage preimage = MakePreimage(1, {"ALPHA!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        COutPoint p2ahOutpoint = AddCoin(coins, MakeP2AHScript(preimage), 50 * COIN, 1);

        // Spending tx: ONLY the P2AH input, no owner token anywhere
        CMutableTransaction mutTx;
        CTxIn p2ahIn;
        p2ahIn.prevout = p2ahOutpoint;
        p2ahIn.scriptSig = MakeP2AHScriptSig(preimage);
        mutTx.vin.push_back(p2ahIn);
        mutTx.vout.push_back(CTxOut(50 * COIN, MakeKeyScript()));

        CTransaction tx(mutTx);

        std::string strError;
        BOOST_CHECK(!CheckTxAssetAuthInputs(tx, coins, strError));
        BOOST_CHECK_EQUAL(strError, "bad-txns-assetauth-insufficient-owner-movement");
    }

    BOOST_AUTO_TEST_CASE(authorization_wrong_preimage_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization Wrong Preimage Test");

        SelectParams(CBaseChainParams::MAIN);

        CAssetAuthPreimage preimage = MakePreimage(1, {"ALPHA!"});
        CAssetAuthPreimage wrongPreimage = MakePreimage(1, {"BETA!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        COutPoint p2ahOutpoint = AddCoin(coins, MakeP2AHScript(preimage), 50 * COIN, 1);

        // Spend revealing the WRONG preimage
        CMutableTransaction mutTx;
        CTxIn p2ahIn;
        p2ahIn.prevout = p2ahOutpoint;
        p2ahIn.scriptSig = MakeP2AHScriptSig(wrongPreimage);
        mutTx.vin.push_back(p2ahIn);
        mutTx.vout.push_back(CTxOut(50 * COIN, MakeKeyScript()));

        CTransaction tx(mutTx);

        std::string strError;
        BOOST_CHECK(!CheckTxAssetAuthInputs(tx, coins, strError));
        BOOST_CHECK_EQUAL(strError, "bad-txns-assetauth-hash-mismatch");
    }

    BOOST_AUTO_TEST_CASE(authorization_m_of_n_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization M of N Test");

        SelectParams(CBaseChainParams::MAIN);

        // 2-of-3 P2AH
        CAssetAuthPreimage preimage = MakePreimage(2, {"AAA!", "BBB!", "CCC!"});

        // Helper to build the spending tx with the given owner tokens moving
        auto buildAndCheck = [&](const std::vector<std::string>& vMovingTokens) -> bool {
            CCoinsView view;
            CCoinsViewCache coins(&view);

            COutPoint p2ahOutpoint = AddCoin(coins, MakeP2AHScript(preimage), 50 * COIN, 1);

            CMutableTransaction mutTx;

            CTxIn p2ahIn;
            p2ahIn.prevout = p2ahOutpoint;
            p2ahIn.scriptSig = MakeP2AHScriptSig(preimage);
            mutTx.vin.push_back(p2ahIn);

            // Add the owner token inputs and matching outputs
            uint32_t n = 10;
            for (const std::string& name : vMovingTokens) {
                CScript ownerScript = MakeKeyScript();
                CAssetTransfer ownerTransfer(name, OWNER_ASSET_AMOUNT);
                ownerTransfer.ConstructTransaction(ownerScript);
                COutPoint ownerOutpoint = AddCoin(coins, ownerScript, 0, n++);

                CTxIn ownerIn;
                ownerIn.prevout = ownerOutpoint;
                mutTx.vin.push_back(ownerIn);

                CScript ownerOutScript = MakeKeyScript();
                ownerTransfer.ConstructTransaction(ownerOutScript);
                mutTx.vout.push_back(CTxOut(0, ownerOutScript));
            }

            mutTx.vout.push_back(CTxOut(50 * COIN, MakeKeyScript()));

            CTransaction tx(mutTx);
            std::string strError;
            return CheckTxAssetAuthInputs(tx, coins, strError);
        };

        // 0 or 1 of 3 moving: not enough
        BOOST_CHECK(!buildAndCheck({}));
        BOOST_CHECK(!buildAndCheck({"AAA!"}));

        // 2 of 3 moving: authorized
        BOOST_CHECK(buildAndCheck({"AAA!", "BBB!"}));
        BOOST_CHECK(buildAndCheck({"AAA!", "CCC!"}));
        BOOST_CHECK(buildAndCheck({"BBB!", "CCC!"}));

        // All 3 moving: authorized
        BOOST_CHECK(buildAndCheck({"AAA!", "BBB!", "CCC!"}));

        // Wrong tokens moving: not authorized
        BOOST_CHECK(!buildAndCheck({"XXX!", "YYY!"}));
    }

    BOOST_AUTO_TEST_CASE(authorization_chaining_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization Chaining Test");

        SelectParams(CBaseChainParams::MAIN);

        // ROOT! authorizes P2AH(ROOT!) which holds LEAF!
        // LEAF! authorizes P2AH(LEAF!) which holds RVN
        CAssetAuthPreimage rootPreimage = MakePreimage(1, {"ROOT!"});
        CAssetAuthPreimage leafPreimage = MakePreimage(1, {"LEAF!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        // Coin 1: ROOT! at a key address
        CScript rootScript = MakeKeyScript();
        CAssetTransfer rootTransfer("ROOT!", OWNER_ASSET_AMOUNT);
        rootTransfer.ConstructTransaction(rootScript);
        COutPoint rootOutpoint = AddCoin(coins, rootScript, 0, 1);

        // Coin 2: LEAF! held at P2AH(ROOT!)
        CScript leafScript = MakeP2AHScript(rootPreimage);
        CAssetTransfer leafTransfer("LEAF!", OWNER_ASSET_AMOUNT);
        leafTransfer.ConstructTransaction(leafScript);
        COutPoint leafOutpoint = AddCoin(coins, leafScript, 0, 2);

        // Coin 3: RVN held at P2AH(LEAF!)
        COutPoint rvnOutpoint = AddCoin(coins, MakeP2AHScript(leafPreimage), 5 * COIN, 3);

        // The chained spending transaction
        auto buildTx = [&](bool fIncludeRoot) -> CTransaction {
            CMutableTransaction mutTx;

            if (fIncludeRoot) {
                CTxIn rootIn;
                rootIn.prevout = rootOutpoint;
                mutTx.vin.push_back(rootIn);
            }

            CTxIn leafIn;
            leafIn.prevout = leafOutpoint;
            leafIn.scriptSig = MakeP2AHScriptSig(rootPreimage);
            mutTx.vin.push_back(leafIn);

            CTxIn rvnIn;
            rvnIn.prevout = rvnOutpoint;
            rvnIn.scriptSig = MakeP2AHScriptSig(leafPreimage);
            mutTx.vin.push_back(rvnIn);

            // Outputs: both owner tokens move on, RVN to a destination
            if (fIncludeRoot) {
                CScript rootOutScript = MakeKeyScript();
                rootTransfer.ConstructTransaction(rootOutScript);
                mutTx.vout.push_back(CTxOut(0, rootOutScript));
            }

            CScript leafOutScript = MakeKeyScript();
            leafTransfer.ConstructTransaction(leafOutScript);
            mutTx.vout.push_back(CTxOut(0, leafOutScript));

            mutTx.vout.push_back(CTxOut(5 * COIN, MakeKeyScript()));

            return CTransaction(mutTx);
        };

        // With ROOT! in the tx: the whole chain is authorized
        std::string strError;
        BOOST_CHECK_MESSAGE(CheckTxAssetAuthInputs(buildTx(true), coins, strError), strError);

        // Without ROOT!: LEAF! can't move, so the RVN can't be spent either
        BOOST_CHECK(!CheckTxAssetAuthInputs(buildTx(false), coins, strError));
        BOOST_CHECK_EQUAL(strError, "bad-txns-assetauth-insufficient-owner-movement");
    }

    BOOST_AUTO_TEST_CASE(authorization_cycle_rejected_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH Authorization Cycle Rejected Test");

        SelectParams(CBaseChainParams::MAIN);

        // Cycle: AAA! held at P2AH(BBB!), BBB! held at P2AH(AAA!).
        // Neither has a key-protected root, so neither can ever be authorized
        CAssetAuthPreimage aPreimage = MakePreimage(1, {"AAA!"});
        CAssetAuthPreimage bPreimage = MakePreimage(1, {"BBB!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        // AAA! held at P2AH(BBB!)
        CScript aScript = MakeP2AHScript(bPreimage);
        CAssetTransfer aTransfer("AAA!", OWNER_ASSET_AMOUNT);
        aTransfer.ConstructTransaction(aScript);
        COutPoint aOutpoint = AddCoin(coins, aScript, 0, 1);

        // BBB! held at P2AH(AAA!)
        CScript bScript = MakeP2AHScript(aPreimage);
        CAssetTransfer bTransfer("BBB!", OWNER_ASSET_AMOUNT);
        bTransfer.ConstructTransaction(bScript);
        COutPoint bOutpoint = AddCoin(coins, bScript, 0, 2);

        // Try to spend both in one tx (each token "moves")
        CMutableTransaction mutTx;

        CTxIn aIn;
        aIn.prevout = aOutpoint;
        aIn.scriptSig = MakeP2AHScriptSig(bPreimage);
        mutTx.vin.push_back(aIn);

        CTxIn bIn;
        bIn.prevout = bOutpoint;
        bIn.scriptSig = MakeP2AHScriptSig(aPreimage);
        mutTx.vin.push_back(bIn);

        CScript aOutScript = MakeKeyScript();
        aTransfer.ConstructTransaction(aOutScript);
        mutTx.vout.push_back(CTxOut(0, aOutScript));

        CScript bOutScript = MakeKeyScript();
        bTransfer.ConstructTransaction(bOutScript);
        mutTx.vout.push_back(CTxOut(0, bOutScript));

        CTransaction tx(mutTx);

        // The cycle has no key-protected root: rejected
        std::string strError;
        BOOST_CHECK(!CheckTxAssetAuthInputs(tx, coins, strError));
        BOOST_CHECK_EQUAL(strError, "bad-txns-assetauth-insufficient-owner-movement");
    }

    BOOST_AUTO_TEST_CASE(authorization_one_token_many_inputs_test)
    {
        BOOST_TEST_MESSAGE("Running P2AH One Token Authorizes Many Inputs Test");

        SelectParams(CBaseChainParams::MAIN);

        CAssetAuthPreimage preimage = MakePreimage(1, {"ALPHA!"});

        CCoinsView view;
        CCoinsViewCache coins(&view);

        // Three P2AH UTXOs at the same address
        COutPoint p2ah1 = AddCoin(coins, MakeP2AHScript(preimage), 10 * COIN, 1);
        COutPoint p2ah2 = AddCoin(coins, MakeP2AHScript(preimage), 20 * COIN, 2);
        COutPoint p2ah3 = AddCoin(coins, MakeP2AHScript(preimage), 30 * COIN, 3);

        // The owner token
        CScript ownerScript = MakeKeyScript();
        CAssetTransfer ownerTransfer("ALPHA!", OWNER_ASSET_AMOUNT);
        ownerTransfer.ConstructTransaction(ownerScript);
        COutPoint ownerOutpoint = AddCoin(coins, ownerScript, 0, 4);

        // One tx spends all three P2AH UTXOs with a single ALPHA! movement
        CMutableTransaction mutTx;
        for (const COutPoint& outpoint : {p2ah1, p2ah2, p2ah3}) {
            CTxIn in;
            in.prevout = outpoint;
            in.scriptSig = MakeP2AHScriptSig(preimage);
            mutTx.vin.push_back(in);
        }

        CTxIn ownerIn;
        ownerIn.prevout = ownerOutpoint;
        mutTx.vin.push_back(ownerIn);

        mutTx.vout.push_back(CTxOut(60 * COIN, MakeKeyScript()));
        CScript ownerOutScript = MakeKeyScript();
        ownerTransfer.ConstructTransaction(ownerOutScript);
        mutTx.vout.push_back(CTxOut(0, ownerOutScript));

        CTransaction tx(mutTx);

        std::string strError;
        BOOST_CHECK_MESSAGE(CheckTxAssetAuthInputs(tx, coins, strError), strError);
    }

BOOST_AUTO_TEST_SUITE_END()
