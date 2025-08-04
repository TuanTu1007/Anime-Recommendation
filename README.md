# 🎯 Anime Recommendation System

A real-time anime recommendation system that predicts the rating a user might give to an anime based on historical viewing data.  
This project integrates **Apache Kafka** for streaming user activity and **Apache Spark Streaming** for real-time prediction using a pre-trained **deep learning model**.

---

## 📂 Project Structure

anime-recommendation/
│
├── model/
│   └── anime_model.h5                # Pretrained deep learning recommendation model
|   |__traininer-notebook-anime-recommendation-system.ipynb
│
├── encoders/
│   ├── user_encoder.pkl              # LabelEncoder for user IDs
│   └── anime_encoder.pkl             # LabelEncoder for anime IDs
│
├── producer/
│   └── kafka_producer.py            # Kafka script to simulate user activity
│
├── consumer/
│   └── spark_consumer.py            # Spark streaming job to predict ratings
│
├── data/
│   └── animelist.csv                # Source interaction dataset
│
├── requirements.txt                 # Python dependencies


---

## 🚀 Features
- **Real-Time Streaming**: Uses Kafka to send user activity data in real-time.
- **Deep Learning Model**: Trained using TensorFlow to predict user-anime ratings.
- **Streaming Inference**: Spark Structured Streaming processes Kafka events and makes predictions in real-time.
- **Modular Design**: Clear separation between model, encoders, producer, and consumer scripts.

---

## 🛠 Technologies
- Python
- TensorFlow / Keras
- Apache Kafka
- Apache Spark Streaming
- Scikit-learn
- Pandas, NumPy

---

