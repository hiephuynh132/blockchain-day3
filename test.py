import requests

FILE_ID = "14AAAPomQv32EwbyXG_l97_wzNN-CnABx"
URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

response = requests.get(URL)
with open("downloaded_file", "wb") as f:
    f.write(response.content)

print("Done!")

#gdown https://drive.google.com/uc?id=14AAAPomQv32EwbyXG_l97_wzNN-CnABx
# wget --no-check-certificate "https://drive.google.com/uc?export=download&id=14AAAPomQv32EwbyXG_l97_wzNN-CnABx"