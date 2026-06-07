import json
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

# -----------------------------
# Kafka configuration
# -----------------------------
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "DiamondsPricePrediction"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# -----------------------------
# Spark session
# -----------------------------
spark = SparkSession.builder \
    .appName("DiamondsCSVLoader") \
    .getOrCreate()

# -----------------------------
# Load CSV
# -----------------------------
df_spark = spark.read.csv("diamonds.csv", header=True, inferSchema=True)

# -----------------------------
# Remove outliers
# -----------------------------
df_no_outliers = df_spark
initial_row_count = df_spark.count()
print(f"Initial row count: {initial_row_count}")

cols_for_outlier_removal = ["carat", "depth", "table", "x", "y", "z"]

for i in cols_for_outlier_removal:
    quantiles = df_no_outliers.approxQuantile(i, [0.25, 0.75], 0.01)
    Q1 = quantiles[0]
    Q3 = quantiles[1]
    IQR = Q3 - Q1

    lower_bound = Q1 - (1.5 * IQR)
    upper_bound = Q3 + (1.5 * IQR)

    df_no_outliers = df_no_outliers.filter(
        (col(i) >= lower_bound) & (col(i) <= upper_bound)
    )
    print(f"Rows after removing outliers for '{i}': {df_no_outliers.count()}")

final_row_count = df_no_outliers.count()
print(f"Final row count after outlier removal for all columns: {final_row_count}")
print(f"Total rows removed: {initial_row_count - final_row_count}")

df_spark = df_no_outliers

# -----------------------------
# Feature engineering
# -----------------------------
categorical_cols = ["cut", "color", "clarity"]
numerical_cols = [c for c in df_spark.columns if c not in categorical_cols + ["price"]]

indexers = [
    StringIndexer(inputCol=c, outputCol=c + "_indexed", handleInvalid="keep")
    for c in categorical_cols
]

encoders = [
    OneHotEncoder(inputCol=c + "_indexed", outputCol=c + "_encoded")
    for c in categorical_cols
]

assembler_inputs = [c + "_encoded" for c in categorical_cols] + numerical_cols
vector_assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features")

pipeline = Pipeline(stages=indexers + encoders + [vector_assembler])

df_transformed = pipeline.fit(df_spark).transform(df_spark)

# -----------------------------
# Train/test split
# -----------------------------
(training_data, testing_data) = df_transformed.randomSplit([0.8, 0.2], seed=42)

# -----------------------------
# Batch training
# -----------------------------
batch_proportions = [x / 10.0 for x in range(1, 11, 1)]

print("Starting batch training...")

for prop in batch_proportions:
    print(f"\n--- Training with {prop*100:.0f}% of training data ---")

    current_training_batch = training_data.sample(
        withReplacement=False,
        fraction=prop,
        seed=42
    )
    batch_size = current_training_batch.count()
    print(f"Batch size: {batch_size} rows")

    rf_regressor_batch = RandomForestRegressor(
        featuresCol="features",
        labelCol="price",
        seed=42
    )
    rf_model_batch = rf_regressor_batch.fit(current_training_batch)

    batch_predictions = rf_model_batch.transform(testing_data)

    evaluator_rmse_batch = RegressionEvaluator(
        labelCol="price",
        predictionCol="prediction",
        metricName="rmse"
    )
    rmse_batch = evaluator_rmse_batch.evaluate(batch_predictions)

    evaluator_r2_batch = RegressionEvaluator(
        labelCol="price",
        predictionCol="prediction",
        metricName="r2"
    )
    r2_batch = evaluator_r2_batch.evaluate(batch_predictions)

    avg_predicted_price = batch_predictions.select("prediction") \
        .agg({"prediction": "avg"}) \
        .collect()[0][0]

    print(f"RMSE on test data for this batch: {rmse_batch}")
    print(f"R-squared on test data for this batch: {r2_batch}")
    print(f"Average Predicted Price for this batch: {avg_predicted_price}")

    # -----------------------------
    # Send message to Kafka
    # -----------------------------
    message = {
        "iteration": int(prop * 10),
        "batch_percent": int(prop * 100),
        "batch_size": batch_size,
        "rmse": rmse_batch,
        "r2": r2_batch,
        "avg_predicted_price": avg_predicted_price
    }

    producer.send(KAFKA_TOPIC, value=message)
    producer.flush()

    print(f"Sent to Kafka topic '{KAFKA_TOPIC}': {message}")
    
# -----------------------------
# Cleanup
# -----------------------------
producer.close()
spark.stop()