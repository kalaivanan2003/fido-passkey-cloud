from cryptography.fernet import Fernet
message = "dd36aeebbcbb758093d2c2ec24309c1534ff5aeeafcf148bcd4a41c34e433c1c"
key = Fernet.generate_key()

Decryptkey = key.decode()

fernet = Fernet(key)
encMessage = fernet.encrypt(message.encode())

print("original string: ", message)
print("encrypted string: ", encMessage)