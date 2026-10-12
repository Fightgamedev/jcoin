#!/usr/bin/env python3
"""Native GTK4 wallet for the local JCoin prototype."""
import base64, hashlib, json, os, secrets, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jcoin_backup import create_backup, open_backup, open_legacy_native_backup

APP = 'JCoin Wallet'
CONFIG = Path.home()/'.config/jcoin-wallet.json'
DATA = Path.home()/'.local/share/jcoin-wallet'

def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':'))
def address(pub): return 'JC'+hashlib.sha256(pub).hexdigest()[:40]
def request(url, data=None):
    raw = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=raw, headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=3) as response: return json.loads(response.read())

class Wallet(Gtk.Application):
    def __init__(self): super().__init__(application_id='org.jcoin.Wallet'); self.key=None; self.file=None
    def do_activate(self):
        self.window=Gtk.ApplicationWindow(application=self, title=APP); self.window.set_default_size(720,680)
        self.window.add_css_class('jcoin'); self.build(); self.window.present(); self.refresh()
    def build(self):
        css=Gtk.CssProvider(); css.load_from_data(b'.jcoin {background:#10151c;color:#eef3fa}.card {background:#1b2531;border-radius:16px;padding:18px}.title {font-size:28px;font-weight:700}.muted {color:#9eacbd}.big {font-size:30px;font-weight:700}.accent {color:#62e0be}')
        Gtk.StyleContext.add_provider_for_display(self.window.get_display(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14); root.set_margin_top(22); root.set_margin_bottom(22); root.set_margin_start(24); root.set_margin_end(24); self.window.set_child(root)
        head=Gtk.Box(spacing=12); root.append(head); title=Gtk.Label(label='JCoin Wallet'); title.add_css_class('title'); title.set_xalign(0); head.append(title)
        self.status=Gtk.Label(label='Local node'); self.status.add_css_class('muted'); head.append(self.status)
        self.endpoint=Gtk.Entry(); self.endpoint.set_text(self.load_url()); self.endpoint.set_placeholder_text('Node address (local by default)'); root.append(self.endpoint)
        row=Gtk.Box(spacing=8); root.append(row)
        for label,cb in [('Create wallet',self.create_wallet),('Open wallet',self.open_wallet),('Refresh',self.refresh)]:
            b=Gtk.Button(label=label); b.connect('clicked',lambda _,fn=cb:fn()); row.append(b)
        card=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8); card.add_css_class('card'); root.append(card)
        baltitle=Gtk.Label(label='Confirmed balance'); balt=Gtk.Label(label='Confirmed balance'); balt.add_css_class('muted'); balt.set_xalign(0); card.append(balt)
        self.balance=Gtk.Label(label='— JCOIN'); self.balance.add_css_class('big'); self.balance.set_xalign(0); card.append(self.balance)
        self.addr=Gtk.Label(label='Create or open a wallet'); self.addr.set_xalign(0); self.addr.set_selectable(True); self.addr.add_css_class('muted'); card.append(self.addr)
        send=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=9); send.add_css_class('card'); root.append(send)
        label=Gtk.Label(label='Send JCOIN'); label.set_xalign(0); label.add_css_class('title'); send.append(label)
        self.private_mode=Gtk.CheckButton(label='Private send (default; not implemented yet)'); self.private_mode.set_active(True); send.append(self.private_mode)
        self.transparent_mode=Gtk.CheckButton(label='Transparent test send (available now)'); self.transparent_mode.set_group(self.private_mode); send.append(self.transparent_mode)
        self.mode_note=Gtk.Label(label='Private is selected by default, but this prototype cannot send privately. Choose transparent mode to send a test transfer.'); self.mode_note.set_wrap(True); self.mode_note.set_xalign(0); self.mode_note.add_css_class('muted'); send.append(self.mode_note)
        self.private_mode.connect('toggled',self.update_mode_note); self.transparent_mode.connect('toggled',self.update_mode_note)
        self.to=Gtk.Entry(); self.to.set_placeholder_text('Recipient address (JC + 40 hex characters)'); send.append(self.to)
        self.amount=Gtk.Entry(); self.amount.set_placeholder_text('Whole JCOIN amount'); send.append(self.amount)
        b=Gtk.Button(label='Sign and queue transfer'); b.add_css_class('accent'); b.connect('clicked',self.send); send.append(b)
        self.message=Gtk.Label(label='Your key remains encrypted on this computer.'); self.message.set_wrap(True); self.message.set_xalign(0); root.append(self.message)
    def load_url(self):
        try: return json.loads(CONFIG.read_text()).get('node','http://127.0.0.1:8765')
        except Exception: return 'http://127.0.0.1:8765'
    def save_url(self):
        CONFIG.parent.mkdir(parents=True,exist_ok=True); CONFIG.write_text(json.dumps({'node':self.endpoint.get_text().rstrip('/')})); CONFIG.chmod(0o600)
    def prompt(self,title,callback,confirm_password=False):
        d=Gtk.Dialog(title=title,transient_for=self.window,modal=True); d.add_button('Cancel',Gtk.ResponseType.CANCEL); d.add_button('Continue',Gtk.ResponseType.OK)
        box=d.get_content_area(); box.set_spacing(10); box.set_margin_top(14); box.set_margin_bottom(14); box.set_margin_start(14); box.set_margin_end(14)
        e=Gtk.PasswordEntry(); e.set_show_peek_icon(True); e.set_placeholder_text('Wallet password (12+ characters)' if confirm_password else 'Wallet password'); box.append(e)
        second=None
        if confirm_password:
            second=Gtk.PasswordEntry(); second.set_show_peek_icon(True); second.set_placeholder_text('Confirm wallet password'); box.append(second)
        def on_response(dlg,res):
            if res==Gtk.ResponseType.OK:
                if confirm_password and e.get_text()!=second.get_text():
                    self.note('The passwords do not match. Please try creating the wallet again.'); dlg.destroy(); return
                callback(e.get_text())
            dlg.destroy()
        d.connect('response',on_response); d.present()
    def create_wallet(self):
        self.prompt('Create encrypted wallet',lambda password:self._create(password),confirm_password=True)
    def _create(self,password):
        if len(password)<12: self.note('Use a wallet password with at least 12 characters.'); return
        private=Ed25519PrivateKey.generate()
        path=DATA/('wallet-'+time.strftime('%Y%m%d-%H%M%S')+'-'+secrets.token_hex(4)+'.jcoinwallet')
        self.write_compatible_backup(private,password,path,'JCoin wallet')
        self.unlock(private,path,'Wallet created. This encrypted backup works with the browser wallets too.')
    def write_compatible_backup(self,private,password,path,name):
        DATA.mkdir(mode=0o700,parents=True,exist_ok=True)
        payload=create_backup(private,password,name)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as wallet_file:
            json.dump(payload,wallet_file,indent=2); wallet_file.write('\n'); wallet_file.flush(); os.fsync(wallet_file.fileno())
    def open_wallet(self):
        chooser=Gtk.FileChooserNative(title='Open JCoin wallet', transient_for=self.window, action=Gtk.FileChooserAction.OPEN,accept_label='Open',cancel_label='Cancel')
        f=Gtk.FileFilter(); f.set_name('JCoin wallet'); f.add_pattern('*.jcoinwallet'); chooser.add_filter(f)
        chooser.connect('response',lambda dlg,res:self._selected(dlg) if res==Gtk.ResponseType.ACCEPT else None); chooser.show()
    def _selected(self,dlg):
        p=Path(dlg.get_file().get_path()); dlg.destroy()
        self.prompt('Unlock wallet',lambda password:self._unlock(p,password))
    def _unlock(self,p,password):
        try:
            d=json.loads(p.read_text())
            if d.get('format')=='jcoin-wallet':
                private=open_backup(d,password)
                self.unlock(private,p,'Wallet unlocked. This backup is compatible with the browser wallets.')
            else:
                # Read the original native wallet format and preserve it while writing a compatible copy.
                private=open_legacy_native_backup(d,password)
                name='JCoin wallet'
                target=DATA/('wallet-compatible-'+time.strftime('%Y%m%d-%H%M%S')+'-'+secrets.token_hex(4)+'.jcoinwallet')
                self.write_compatible_backup(private,password,target,name)
                self.unlock(private,p,'Legacy wallet opened. A browser-compatible encrypted copy was saved as '+target.name+'.')
        except Exception as e: self.note('Could not unlock wallet. Check the password and file. '+str(e))
    def unlock(self,private,p,message='Wallet unlocked in memory for this session.'):
        self.key=private; self.file=p; self.addr.set_text(address(self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw))); self.note(message); self.refresh()
    def note(self,msg): self.message.set_text(msg)
    def refresh(self,*_):
        try:
            self.save_url(); status=request(self.endpoint.get_text().rstrip('/')+'/api/status'); self.status.set_text('Node online · height '+str(status.get('height','?')))
            if self.key:
                a=self.addr.get_text(); info=request(self.endpoint.get_text().rstrip()+'/api/balance?address='+urllib.parse.quote(a)); self.balance.set_text(str(info.get('balance',0))+' JCOIN')
            else: self.balance.set_text('Open a wallet to view balance')
        except Exception as exc: self.status.set_text('Node unavailable'); self.note('Start the JCoin node, then refresh. '+str(exc))
    def update_mode_note(self,*_):
        if self.private_mode.get_active():
            self.mode_note.set_text('Private is selected by default, but this prototype cannot send privately. Choose transparent mode to send a test transfer.')
        else:
            self.mode_note.set_text('Transparent mode is selected. The node and ledger can expose the sender, recipient, amount, and timing.')
    def send(self,*_):
        if not self.key: self.note('Open or create a wallet first.'); return
        if self.private_mode.get_active(): self.note('Private transfers are not implemented. No transfer was sent. Choose transparent test mode to continue.'); return
        try:
            amount=int(self.amount.get_text()); recipient=self.to.get_text().strip()
            if amount<=0 or len(recipient)!=42 or not recipient.startswith('JC') or any(c not in '0123456789abcdefABCDEF' for c in recipient[2:]): raise ValueError('Enter a valid address and positive whole amount.')
            recipient='JC'+recipient[2:].lower()
            dialog=Gtk.MessageDialog(transient_for=self.window,modal=True,message_type=Gtk.MessageType.WARNING,buttons=Gtk.ButtonsType.NONE,text='Transparent test payment')
            dialog.set_secondary_text(f'Send {amount} test JCOIN to {recipient}? The sender, recipient, amount, and timing will be visible to the node and anyone who can inspect its ledger. This cannot be made private after sending.')
            dialog.add_button('Cancel',Gtk.ResponseType.CANCEL); dialog.add_button('Send transparently',Gtk.ResponseType.ACCEPT)
            dialog.connect('response',lambda dlg,response:self._send_confirmed(dlg,response,recipient,amount)); dialog.present()
        except Exception as e: self.note('Could not prepare transfer: '+str(e))
    def _send_confirmed(self,dialog,response,recipient,amount):
        dialog.destroy()
        if response!=Gtk.ResponseType.ACCEPT: return
        try:
            base=self.endpoint.get_text().rstrip('/'); a=self.addr.get_text(); acct=request(base+'/api/balance?address='+urllib.parse.quote(a)); pub=self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
            tx={'amount':amount,'from':a,'nonce':int(acct['nonce']),'pub':base64.b64encode(pub).decode(),'time':int(time.time()),'to':recipient}
            tx['sig']=base64.b64encode(self.key.sign(canonical(tx).encode('ascii'))).decode(); result=request(base+'/api/transaction',tx)
            self.note('Transparent test transfer signed and queued: '+result.get('txid','')); self.refresh()
        except urllib.error.HTTPError as e:
            try: msg=json.loads(e.read()).get('error',str(e))
            except Exception: msg=str(e)
            self.note('Transfer rejected: '+msg)
        except Exception as e: self.note('Could not send: '+str(e))

Wallet().run()
