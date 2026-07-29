from dotenv import load_dotenv
load_dotenv()
import os

token = os.getenv('HF_TOKEN')
if token:
    print(f"Token found: {token[:10]}...{token[-5:]}")
else:
    print("Token NOT FOUND in .env")
    print("Make sure you have HF_TOKEN=hf_... in your .env file")
