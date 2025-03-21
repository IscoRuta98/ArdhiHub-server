from algosdk import account, transaction
from algosdk.v2client import algod

from config.settings import settings

algod_client = algod.AlgodClient(
    algod_token='', 
    algod_address=settings.algod_address)

def generate_algorand_keypair() -> tuple[str, str]:
    """
    Generate an Algorand public-private keypair.
    """
    private_key, address = account.generate_account()
    return (private_key, address)


def create_asa(
        private_key: str, 
        creator_address: str, 
        unit_name: str, 
        asset_name: str, 
        total: int, 
        decimals: int, 
        url: str) -> int:
    """
    Create an Algorand Standard Asset (ASA).
    """
    sp = algod_client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url=url,
        total=total,
        decimals=decimals,
    )

    # Sign with secret key of creator
    stxn = txn.sign(private_key)
    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(stxn)
    print(f"Sent asset create transaction with txid: {txid}")
    # Wait for the transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")

    # grab the asset id for the asset we just created
    created_asset = results["asset-index"]
    print(f"Asset ID created: {created_asset}")
    return created_asset

def opt_in_to_asa(private_key: str, address: str, asset_id: int):
    """
    Opt-in to an Algorand Standard Asset (ASA).
    """
    sp = algod_client.suggested_params()
    optin_txn = transaction.AssetOptInTxn(sender=address, sp=sp, index=asset_id)
    signed_optin_txn = optin_txn.sign(private_key)
    txid = algod_client.send_transaction(signed_optin_txn)
    print(f"Sent opt in transaction with txid: {txid}")

    # Wait for the transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")

def transfer_asa(private_key: str, 
                 sender_address: str, 
                 receiver_address: str, 
                 asset_id: int, 
                 amount: int):
    """
    Transfer an Algorand Standard Asset (ASA).
    """
    sp = algod_client.suggested_params()
    xfer_txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=sp,
        receiver=receiver_address,
        amt=amount,
        index=asset_id,
    )
    signed_xfer_txn = xfer_txn.sign(private_key)
    txid = algod_client.send_transaction(signed_xfer_txn)
    print(f"Sent transfer transaction with txid: {txid}")

    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")
    return txid


def revoke_asa(private_key: str, 
                clawback_address: str, 
                holder_address: str, 
                asset_id: int, 
                amount: int):
    """
    Revoke an Algorand Standard Asset (ASA) from a target account.
    """
    sp = algod_client.suggested_params()
    clawback_txn = transaction.AssetTransferTxn(
        sender=clawback_address,
        sp=sp,
        receiver=clawback_address,
        amt=amount,
        index=asset_id,
        revocation_target=holder_address,
    )
    signed_clawback_txn = clawback_txn.sign(private_key)
    txid = algod_client.send_transaction(signed_clawback_txn)
    print(f"Sent clawback transaction with txid: {txid}")

    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")
    return txid