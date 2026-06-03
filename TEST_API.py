from dotenv import load_dotenv
import os

load_dotenv()



from quantvn.vn.data.utils import client

api_key = os.getenv("QUANTVN_API_KEY")

client(apikey=api_key)

print("Connected successfully")


