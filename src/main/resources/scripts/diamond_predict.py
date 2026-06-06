#!/usr/bin/env python3
"""
PySpark RandomForest predictor for diamond price.

Expected CLI argument order:
  carat cut color clarity depth table x y z

Trains a RandomForestRegressor on diamonds.csv (located in the same directory
as this script), then predicts the price for the supplied input row.
Prints the predicted price to stdout.
"""

import sys
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.regression import RandomForestRegressor


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


def main() -> int:
    if len(sys.argv) != 10:
        print("Expected 9 arguments: carat cut color clarity depth table x y z", file=sys.stderr)
        return 1

    _, carat_raw, cut, color, clarity, depth_raw, table_raw, x_raw, y_raw, z_raw = sys.argv

    try:
        carat = float(carat_raw)
        depth = float(depth_raw)
        table = float(table_raw)
        x_val = float(x_raw)
        y_val = float(y_raw)
        z_val = float(z_raw)
    except ValueError as exc:
        print(f"Numeric parsing failed: {exc}", file=sys.stderr)
        return 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "diamonds.csv")

    if not os.path.exists(csv_path):
        print(f"diamonds.csv not found at: {csv_path}", file=sys.stderr)
        return 1

    spark = (
        SparkSession.builder
        .appName("DiamondPricePredict")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        df = spark.read.csv(csv_path, header=True, inferSchema=True)
        df = remove_outliers(df, NUMERICAL_COLS)

        pipeline_model = build_pipeline().fit(df)

        input_row = spark.createDataFrame([{
            "carat":   carat,
            "cut":     cut,
            "color":   color,
            "clarity": clarity,
            "depth":   depth,
            "table":   table,
            "x":       x_val,
            "y":       y_val,
            "z":       z_val,
            "price":   0.0,   # dummy label — not used during transform
        }])

        result = pipeline_model.transform(input_row)
        predicted_price = max(result.select("prediction").collect()[0][0], 0.0)

        print(f"{predicted_price:.2f}")
        return 0

    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())