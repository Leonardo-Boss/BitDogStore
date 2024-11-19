import hashlib

def gen_hash(file):
    # Initialize the hash object with the specified algorithm
    hasher = hashlib.new("sha1")
    # Open the file in binary read mode
    with open(file, 'rb') as file:
        # Read and update hash string in chunks of 4096 bytes
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
    # Return the hexadecimal hash
    return hasher.hexdigest()