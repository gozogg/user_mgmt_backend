"""Generate a PBKDF2 password hash for SAM parameters.

Usage:
    python scripts/hash_password.py 'your-password'
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from auth.passwords import hash_password


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/hash_password.py 'your-password'", file=sys.stderr)
        sys.exit(1)
    print(hash_password(sys.argv[1]))


if __name__ == "__main__":
    main()
