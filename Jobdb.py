import requests
import mariadb


url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=e0809f39-49eb-4c64-951c-cc3282f8843b"
response = requests.get(url=url, timeout=30)
response.raise_for_status()
data = response.json()

if not isinstance(data, list):
    raise ValueError("API 回傳資料不是清單")

required_fields = ("地區", "數值", "欄位名稱")
filtered_data = []
for index, item in enumerate(data):
    if not isinstance(item, dict):
        raise ValueError(f"第 {index + 1} 筆資料不是物件")
    missing_fields = [field for field in required_fields if field not in item]
    if missing_fields:
        raise ValueError(f"第 {index + 1} 筆資料缺少欄位: {missing_fields}")
    filtered_data.append({field: item[field] for field in required_fields})

conn = mariadb.connect(
    user="root",
    password="uabg31030",
    host="localhost",
    port=3306,
    database="jobdb",
)

try:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `job_data` (
            `欄位名稱` VARCHAR(255) NOT NULL,
            `地區` VARCHAR(255) NOT NULL,
            `數值` TEXT,
            PRIMARY KEY (`欄位名稱`)
        ) CHARACTER SET utf8mb4
        """
    )

    cursor.executemany(
        """
        INSERT INTO `job_data` (`欄位名稱`, `地區`, `數值`)
        VALUES (?, ?, ?)
        ON DUPLICATE KEY UPDATE
            `地區` = VALUES(`地區`),
            `數值` = VALUES(`數值`)
        """,
        [
            (item["欄位名稱"], item["地區"], item["數值"])
            for item in filtered_data
        ],
    )
    conn.commit()
    print(f"已完成 {len(filtered_data)} 筆資料寫入 jobdb.job_data")
finally:
    conn.close()

