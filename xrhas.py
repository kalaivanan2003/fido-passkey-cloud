

def QrCodeVerify():
    import cv2
    cam = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    while True:
        _, img = cam.read()
        data, bbox, _ = detector.detectAndDecode(img)
        if data:

            print(data)



        cv2.imshow("img", img)
        if cv2.waitKey(1) == ord("Q"):
            break

    cam.release()
    cv2.destroyAllWindows()

QrCodeVerify()

'''from ecies.utils import generate_key
from ecies import encrypt, decrypt

# ----------------------------------
# 1. Generate ECC key pair (secp256k1)
# ----------------------------------
secp_k = generate_key()
privhex = secp_k.to_hex()                     # Private key (hex)
pubhex = secp_k.public_key.format(True).hex() # Public key (compressed hex)

print("Private Key:", privhex)
print("Public Key :", pubhex)

# ----------------------------------
# 2. Plain text message
# ----------------------------------
message = "Hello boss! ECIES encryption working 💪"
message_bytes = message.encode("utf-8")

# ----------------------------------
# 3. Encryption (using PUBLIC key)
# ----------------------------------
ciphertext = encrypt(pubhex, message_bytes)
print("Encrypted (hex):", ciphertext.hex())

# ----------------------------------
# 4. Decryption (using PRIVATE key)
# ----------------------------------
decrypted_bytes = decrypt(privhex, ciphertext)
decrypted_message = decrypted_bytes.decode("utf-8")

print("Decrypted Message:", decrypted_message)'''


'''import hashlib

def sha256_hash(data):
    """Generate SHA-256 hash of input data and return as bytes."""
    return hashlib.sha256(data.encode()).digest()

def xor_hashes(hash1, hash2):
    """Perform XOR operation between two hash values (bytes)."""
    return bytes(a ^ b for a, b in zip(hash1, hash2))

# Example input keys
key1 = "secret_key_1"
key2 = "secret_key_2"

# Generate SHA-256 hashes
hash1 = sha256_hash(key1)
hash2 = sha256_hash(key2)

# Perform XOR operation
xor_result = xor_hashes(hash1, hash2)

# Convert result to hexadecimal string
xor_hex = xor_result.hex()

print(f"SHA-256 Hash 1: {hash1.hex()}")
print(f"SHA-256 Hash 2: {hash2.hex()}")
print(f"XOR Result: {xor_hex}")'''
