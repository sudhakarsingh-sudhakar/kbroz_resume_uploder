from app import *

import os

# Generate a random secret key
secret_key = os.urandom(24)

# Convert the secret key to a string
secret_key_str = str(secret_key)

# Print the secret key
print("Generated secret key:", secret_key_str)


if __name__ == '__main__':
    app.run(debug=True,port=8000)
