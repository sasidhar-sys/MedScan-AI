import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.utils.password import hash_password, verify_password

password = "MyStrongPassword123!"

hashed = hash_password(password)

print("Hashed Password:")
print(hashed)

print("\nVerification Test:")
print("Correct Password Match:", verify_password(password, hashed))
print("Wrong Password Match:", verify_password("WrongPassword", hashed))
