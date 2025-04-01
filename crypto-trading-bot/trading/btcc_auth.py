# btcc_auth.py
import hashlib
from urllib.parse import urlencode

def generate_signature(params: dict, secret_key: str) -> str:
    # Step 1: Sort parameters by key
    sorted_params = sorted(params.items())

    # Step 2: Create URL-style string (e.g., key1=value1&key2=value2)
    param_str = urlencode(sorted_params)

    # Step 3: Append secret key
    sign_str = f"{param_str}&secret_key={secret_key}"

    # Step 4: SHA256 hash
    sha256 = hashlib.sha256()
    sha256.update(sign_str.encode('utf-8'))
    return sha256.hexdigest().lower()
