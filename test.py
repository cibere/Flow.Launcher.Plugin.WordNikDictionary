import requests

word = "github"
url = "http://api.urbandictionary.com/v0/define"
res = requests.get(url, params={"term": word})
data = res.json()
import json

print(json.dumps(data, indent=4))
