# Standalone browser wallet

`JCoin-Wallet.html` can be shared as a standalone wallet page. It stores the
private key in an encrypted `.jcoinwallet` backup and signs transfers in the
browser. The local dashboard also supports encrypted backup and restore for
new browser wallets; its backup files use the same format as the standalone
wallet. The current node records sender addresses, recipient addresses, and
amounts in cleartext; encrypted key storage does not make transactions
private. Users need the validator operator's node URL to connect.

When creating a dashboard wallet, choose a strong backup password and save
the downloaded `.jcoinwallet` file outside the browser. Use **Download
encrypted backup** to save another copy or **Import backup** to restore it.
JCoin cannot recover a forgotten password. Dashboard wallets created before
this backup feature cannot export their non-extractable keys; create a new
wallet with backup enabled and move any remaining test balance to it.

The send form selects **Private (default)**, but private transfers are not
implemented. To send a prototype transfer, explicitly select **Transparent
test send** and confirm the disclosure prompt; the sender, recipient, amount,
and timing can be visible in the ledger.

The current node listens only on the validator's own laptop. It is not
reachable by remote users. Do not publish it or expose it to the internet;
remote access would require a publicly reachable HTTPS endpoint and a separate
security review.

To refresh the distributable `JCoin-Wallet-client.zip` after changing this
page or this document, run `./build-client.sh`.
