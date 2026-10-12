import { createHash, webcrypto } from "node:crypto";

const input = JSON.parse(await new Promise((resolve, reject) => {
  let data = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", chunk => { data += chunk; });
  process.stdin.on("end", () => resolve(data));
  process.stdin.on("error", reject);
}));

const { subtle } = webcrypto;
const encoder = new TextEncoder();
const toBase64 = value => Buffer.from(value).toString("base64");
const fromBase64 = value => new Uint8Array(Buffer.from(value, "base64"));

async function deriveBackupKey(password, salt) {
  const material = await subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveKey"]);
  return subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: 310000, hash: "SHA-256" },
    material,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

if (process.argv[2] === "open") {
  const { backup, password } = input;
  const key = await deriveBackupKey(password, fromBase64(backup.salt));
  const privateKeyDer = await subtle.decrypt(
    { name: "AES-GCM", iv: fromBase64(backup.iv) },
    key,
    fromBase64(backup.encryptedPrivateKey),
  );
  process.stdout.write(JSON.stringify({ privateKeyDer: toBase64(privateKeyDer) }));
} else if (process.argv[2] === "create") {
  const { password, name } = input;
  const pair = await subtle.generateKey({ name: "Ed25519" }, true, ["sign", "verify"]);
  const privateKeyDer = await subtle.exportKey("pkcs8", pair.privateKey);
  const publicKey = new Uint8Array(await subtle.exportKey("raw", pair.publicKey));
  const salt = webcrypto.getRandomValues(new Uint8Array(16));
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const key = await deriveBackupKey(password, salt);
  const encryptedPrivateKey = await subtle.encrypt({ name: "AES-GCM", iv }, key, privateKeyDer);
  const address = "JC" + createHash("sha256").update(publicKey).digest("hex").slice(0, 40);
  const backup = {
    format: "jcoin-wallet",
    version: 1,
    name,
    address,
    publicKey: toBase64(publicKey),
    kdf: "PBKDF2-SHA256-310000",
    cipher: "AES-256-GCM",
    salt: toBase64(salt),
    iv: toBase64(iv),
    encryptedPrivateKey: toBase64(encryptedPrivateKey),
  };
  process.stdout.write(JSON.stringify(backup));
} else {
  throw new Error("Expected 'open' or 'create' mode.");
}
