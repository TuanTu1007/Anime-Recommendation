import json
import time
import pandas as pd
from kafka import KafkaProducer

# Đọc dữ liệu từ CSV
df = pd.read_csv("D:/Subject/BigData/DoAn/anime-recommendation/data/animelist.csv")

# Chọn các cột cần thiết 
df = df[['user_id', 'anime_id', 'rating']]

# Xóa dòng null 
df.dropna(subset=['user_id', 'anime_id', 'rating'], inplace=True)

# Cấu hình Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Gửi từng dòng dữ liệu tới Kafka topic
topic = 'anime-recommendation'

print(f"🚀 Kafka Producer đang gửi dữ liệu lên topic: {topic}")
for index, row in df.iterrows():
    message = {
        'user_id': int(row['user_id']),
        'anime_id': int(row['anime_id']),
        'rating': float(row['rating'])
    }

    producer.send(topic, value=message)
    print(f"Gửi: {message}")
    
    time.sleep(0.2)  # Tạm dừng để mô phỏng dữ liệu real-time (giảm tải Kafka)

producer.flush()
print("Hoàn thành gửi dữ liệu.")
