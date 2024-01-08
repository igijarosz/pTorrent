import secrets

client_id = bytearray()
client_id.extend(bytes('-pT0001-', "UTF-8"))
client_id.extend(secrets.token_bytes(12))
