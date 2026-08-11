def send_password_reset_email(to_email: str, reset_code: str):
    # Development fallback for forgot password.
    # This does not send real email.
    # It prints the reset code in the backend terminal.

    print()
    print("=" * 60)
    print("OMNILINK CRM PASSWORD RESET CODE - DEVELOPMENT MODE")
    print("=" * 60)
    print(f"Send/reset email for: {to_email}")
    print(f"Reset code: {reset_code}")
    print("Use this code on the forgot-password screen.")
    print("=" * 60)
    print()

    return True
