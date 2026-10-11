# Standalone browser wallet

`JCoin-Wallet.html` can be shared as a standalone wallet page. It stores the
private key only in an encrypted `.jcoinwallet` backup and signs transfers in
the browser. The current node records sender addresses, recipient addresses, and amounts in cleartext; encrypted key storage does not make transactions private. Users need the validator operator's node URL to connect.

The current node listens only on the validator's own laptop. It is not
reachable by remote users. Do not publish it or expose it to the internet;
remote access would require a publicly reachable HTTPS endpoint and a separate
security review.

To refresh the distributable `JCoin-Wallet-client.zip` after changing this
page or this document, run `./build-client.sh`.
