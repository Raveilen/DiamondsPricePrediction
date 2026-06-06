#!/usr/bin/env python3
"""
Trains a PySpark RandomForest pipeline on diamonds.csv and saves it to disk.
Run this once before using diamond_predict.py.

Usage:
    python train_model.py [diamonds_csv_path] [model_output_dir]

Defaults:
    diamonds_csv_path = ./diamonds.csv   (next to this script)
    model_output_dir  = ./diamond_model  (next to this script)
"""

import sys
import os

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator


CATEGORICAL_COLS = ["cut", "color", "clarity"]
NUMERICAL_COLS   = ["carat", "depth", "table", "x", "y", "z"]


def remove_outliers(df, cols):
    for c in cols:
        q = df.approxQuantile(c, [0.25, 0.75], 0.01)
        iqr = q[1] - q[0]
        df = df.filter(
            (col(c) >= q[0] - 1.5 * iqr) & (col(c) <= q[1] + 1.5 * iqr)
        )
    return df


def build_pipeline():
    indexers = [
        StringIndexer(inputCol=c, outputCol=c + "_indexed", handleInvalid="keep")
        for c in CATEGORICAL_COLS
    ]
    encoders = [
        OneHotEncoder(inputCol=c + "_indexed", outputCol=c + "_encoded")
        for c in CATEGORICAL_COLS
    ]
    assembler_inputs = [c + "_encoded" for c in CATEGORICAL_COLS] + NUMERICAL_COLS
    assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features")
    rf = RandomForestRegressor(featuresCol="features", labelCol="price", seed=42)
    return Pipeline(stages=indexers + encoders + [assembler, rf])


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path   = sys.argv[1] if len(sys.argv) > 1 else os.path.join(script_dir, "diamonds.csv")
    model_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(script_dir, "diamond_model")

    if not os.path.exists(csv_path):
        print(f"Error: diamonds.csv not found at: {csv_path}", file=sys.stderr)
        sys.exit(1)

    spark = (
        SparkSession.builder
        .appName("DiamondModelTrainer")
        .master("local[1]")
        .config("spark.driver.memory", "2g")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.python.worker.reuse", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        print(f"Loading data from {csv_path} ...")
        df = spark.read.csv(csv_path, header=True, inferSchema=True)
        print(f"Loaded {df.count():,} rows")

        print("Removing outliers...")
        df = remove_outliers(df, NUMERICAL_COLS)
        print(f"After outlier removal: {df.count():,} rows")

        training_data, testing_data = df.randomSplit([0.8, 0.2], seed=42)

        print("Training pipeline...")
        pipeline_model = build_pipeline().fit(training_data)

        predictions = pipeline_model.transform(testing_data)
        rmse = RegressionEvaluator(labelCol="price", predictionCol="prediction", metricName="rmse").evaluate(predictions)
        r2   = RegressionEvaluator(labelCol="price", predictionCol="prediction", metricName="r2").evaluate(predictions)
        print(f"Test RMSE: {rmse:.2f}")
        print(f"Test R²:   {r2:.4f}")

        print(f"Saving model to {model_path} ...")
        pipeline_model.write().overwrite().save(model_path)
        print("Model saved successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()