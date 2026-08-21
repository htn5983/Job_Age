import requests
import mariadb
from pprint import pprint


url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=e0809f39-49eb-4c64-951c-cc3282f8843b"
response = requests.get(url=url, timeout=30)
response.raise_for_status()
data = response.json()
data = [
	{key: item[key] for key in ("地區", "數值", "欄位名稱")}
	for item in data
]
pprint(data)