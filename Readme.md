# Create Virtual Environment

python3 -m venv venv
source venv/bin/activate

# Install all dependecies

pip3 install -r requirements.txt

# Running App

uvicorn main:app --reload
