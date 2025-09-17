from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogClassifier:
    def __init__(self):
        self.model = None
        self.setup_model()

    def setup_model(self):
        """Initialize or load the NLP classification model"""
        model_path = "log_classifier_model.pkl"

        if os.path.exists(model_path):
            logger.info("Loading existing model...")
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            logger.info("Training new model...")
            self.train_model()

    def train_model(self):
        """Train a simple NLP classifier for log categorization"""
        # Sample training data - in production, this would be much larger
        training_data = [
            ("User login failed", "Security"),
            ("Authentication error", "Security"),
            ("Unauthorized access attempt", "Security"),
            ("Invalid credentials provided", "Security"),
            ("SQL injection detected", "Security"),
            ("Database connection timeout", "Performance"),
            ("Memory usage high", "Performance"),
            ("CPU utilization 95%", "Performance"),
            ("Response time exceeded 5s", "Performance"),
            ("Disk space low", "Performance"),
            ("User completed purchase", "Business"),
            ("Order processed successfully", "Business"),
            ("Payment received", "Business"),
            ("New user registration", "Business"),
            ("Product viewed", "Business"),
            ("API endpoint called", "General"),
            ("Service started", "General"),
            ("Configuration loaded", "General"),
            ("Debug information", "General"),
            ("Application initialized", "General")
        ]

        texts, labels = zip(*training_data)

        # Create pipeline with TF-IDF and Naive Bayes
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
            ('classifier', MultinomialNB())
        ])

        self.model.fit(texts, labels)

        # Save model
        with open("log_classifier_model.pkl", 'wb') as f:
            pickle.dump(self.model, f)

        logger.info("Model trained and saved")

    def classify(self, message):
        """Classify a log message"""
        if self.model is None:
            return "General"

        try:
            prediction = self.model.predict([message])[0]
            return prediction
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return "General"

def create_spark_session():
    """Create Spark session with Kafka and Elasticsearch dependencies"""
    return SparkSession.builder \
        .appName("LogMonitoringSystem") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.elasticsearch:elasticsearch-spark-30_2.12:8.10.0") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

def process_logs(spark, classifier):
    """Main log processing pipeline"""

    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "logs") \
        .option("startingOffsets", "latest") \
        .load()

    # Define schema for log messages
    log_schema = StructType([
        StructField("timestamp", StringType(), True),
        StructField("service_name", StringType(), True),
        StructField("message", StringType(), True),
        StructField("level", StringType(), True),
        StructField("host", StringType(), True)
    ])

    # Parse JSON messages
    parsed_logs = df.select(
        from_json(col("value").cast("string"), log_schema).alias("log")
    ).select("log.*")

    # Add processing timestamp
    enriched_logs = parsed_logs.withColumn("processed_timestamp", current_timestamp())

    # UDF for classification
    def classify_udf(message):
        return classifier.classify(message) if message else "General"

    classify_func = udf(classify_udf, StringType())

    # Add classification
    classified_logs = enriched_logs.withColumn(
        "category",
        classify_func(col("message"))
    )

    # Prepare for Elasticsearch
    es_logs = classified_logs.select(
        col("timestamp").alias("@timestamp"),
        col("service_name"),
        col("message"),
        col("level"),
        col("host"),
        col("category"),
        col("processed_timestamp")
    )

    # Write to Elasticsearch
    es_query = es_logs.writeStream \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", "logs_classified") \
        .option("es.nodes", "localhost") \
        .option("es.port", "9200") \
        .option("checkpointLocation", "/tmp/checkpoint1") \
        .outputMode("append") \
        .start()

    # Alert processing - count critical logs
    windowed_counts = classified_logs \
        .filter((col("category") == "Security") | (col("level") == "ERROR")) \
        .withWatermark("processed_timestamp", "1 minute") \
        .groupBy(
            window(col("processed_timestamp"), "1 minute"),
            col("category"),
            col("service_name")
        ) \
        .count()

    # Filter for alerts (>10 critical logs per minute)
    alerts = windowed_counts.filter(col("count") > 10)

    # Write alerts to Kafka
    alert_query = alerts.select(
        to_json(struct(
            col("window"),
            col("category"),
            col("service_name"),
            col("count"),
            lit(current_timestamp()).alias("alert_timestamp")
        )).alias("value")
    ).writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "alerts") \
        .option("checkpointLocation", "/tmp/checkpoint2") \
        .outputMode("update") \
        .start()

    return es_query, alert_query

def main():
    """Main function"""
    logger.info("Starting Log Processing System...")

    # Initialize classifier
    classifier = LogClassifier()

    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        # Start processing
        es_query, alert_query = process_logs(spark, classifier)

        logger.info("Streaming queries started successfully")

        # Wait for termination
        es_query.awaitTermination()

    except Exception as e:
        logger.error(f"Error in main processing: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()