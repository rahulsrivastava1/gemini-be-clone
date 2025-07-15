# Signup API

Take phone number of user and stores in users table.

# Send OTP API

Take phone number, checks if phone number exists in users table, then send otp.

# Verify OTP API

Take phone number, and otp. If verify then create JWT Token.

# Forgort Password API

Take phone number, if user exists in users table, then send new otp.

# Change Password API

Take token in headers, if token is valid return new token.
