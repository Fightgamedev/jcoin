# Standalone browser wallet

The local dashboard is available in Japanese and English. It starts in
Japanese when your browser language is Japanese, otherwise in English; use
the language button in the header to switch. Your choice is saved in that
browser.

## ローカルダッシュボードを使う方へ

画面上部の言語ボタンで日本語と英語を切り替えられます。日本語設定の
ブラウザーでは、初回表示は日本語です。設定はそのブラウザーに保存されます。

最初に「ブラウザーウォレットを作成」を選び、暗号化バックアップを保存して
ください。受け取りには表示されたアドレスを共有します。送金画面では
「プライベート」が初期選択ですが、非公開送金はまだ使えません。送金する
場合は「公開テスト送金」を明示的に選んでください。取引の詳細は公開され、
実際の資金には対応していません。

`JCoin-Wallet.html` can be shared as a standalone wallet page. It stores the
private key in an encrypted `.jcoinwallet` backup and signs transfers in the
browser. The local dashboard also supports encrypted backup and restore for
new browser wallets; its backup files use the same format as the standalone
and native wallets. The current node records sender addresses, recipient addresses, and
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
