import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, IntegerType
import tensorflow as tf
import pickle
import numpy as np

# Set environment variables
os.environ["JAVA_HOME"] = "C:\\Program Files\\Java\\jdk1.8.0_202"
os.environ["HADOOP_HOME"] = "D:\\Subject\\BigData\\spark-3.5.0-bin-hadoop3"
os.environ["PATH"] += os.pathsep + os.path.join(os.environ["HADOOP_HOME"], "bin")
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disable TensorFlow oneDNN logs
os.environ["PYSPARK_PYTHON"] = "D:\\Subject\\BigData\\DoAn\\anime-recommendation\\venv310\\Scripts\\python.exe"

# Load model 
model = tf.keras.models.load_model("model/anime_model.h5")

# Load encoders
with open("encoders/user_encoder.pkl", "rb") as f:
    user_encoder = pickle.load(f)
with open("encoders/anime_encoder.pkl", "rb") as f:
    anime_encoder = pickle.load(f)

def predict_rating(user_id, anime_id):
    if user_id not in user_encoder or anime_id not in anime_encoder:
        return None
    user = user_encoder[user_id]
    anime = anime_encoder[anime_id]
    prediction = model.predict([np.array([user]), np.array([anime])])
    return float(prediction[0][0])

def recommend_anime(user_id, top_n=5):
    try:
        # Encode user
        user_encoded = user_encoder.transform([user_id])[0]

        # Prepare candidate anime IDs (already encoded)
        all_anime_ids = anime_encoder.transform(anime_encoder.classes_)

        user_ids = np.full(len(all_anime_ids), user_encoded)

        predictions = model.predict([user_ids, all_anime_ids], verbose=0)
        top_indices = predictions.flatten().argsort()[-top_n:][::-1]

        top_anime_original_ids = anime_encoder.inverse_transform(all_anime_ids[top_indices])
        return top_anime_original_ids.tolist()
    except Exception as e:
        print(f"Recommendation error: {e}")
        return []
    
def process_row(row):
    user_id = row["user_id"]
    print(f"\nNew data received - user_id: {user_id}")
    
    recommendations = recommend_anime(user_id)
    print(f"Recommended anime IDs for user {user_id}: {recommendations}")

# Create Spark session
spark = SparkSession.builder \
    .appName("AnimeRatingPredictor") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.hadoop.validateOutputSpecs", "false") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Define schema
schema = StructType() \
    .add("user_id", IntegerType()) \
    .add("anime_id", IntegerType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "anime_topic") \
    .load()

df = df.selectExpr("CAST(value AS STRING)")
json_df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")

def foreach_batch_function(df, epoch_id):
    rows = df.collect()
    for row in rows:
        user_id = row["user_id"]
        anime_id = row["anime_id"]

        rating = predict_rating(user_id, anime_id)
        print(f"\n user_id={user_id}, anime_id={anime_id}, rating={rating:.2f}" if rating else f"⚠ Không thể dự đoán.")

        recommendations = recommend_anime(user_id, top_n=5)
        print(f"Gợi ý top anime cho user {user_id}: {recommendations}")

# Start streaming query
query = json_df.writeStream \
    .outputMode("append") \
    .foreachBatch(foreach_batch_function) \
    .start()

query.awaitTermination()