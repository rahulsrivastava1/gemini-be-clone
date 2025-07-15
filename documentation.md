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

# Get User detail API

Take token in headers, if token is valid return user details.

# Create Chatroom

Take token in headers, create chatroom for that user if token is valid.

# Get Chatrooms

Take token in headers, get all chatrooms associated with that user if token is valid.

# Get Chatroom

Take token in headers, and chatroom id -> return chatroom detail if token is valid.
