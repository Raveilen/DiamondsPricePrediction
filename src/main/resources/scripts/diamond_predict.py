#!/usr/bin/env python3
"""
Loads a pre-trained PySpark PipelineModel and predicts diamond price.

Expected CLI argument order:
    carat cut color clarity depth table x y z

Run train_model.py first to produce the diamond_model directory.
"""

import sys
import os

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
# Set directly in script so it works regardless of whether the IDE
# was restarted after the system environment variable was changed.
os.environ["HADOOP_HOME"] = "C:\\winutils"

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import PipelineModel


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
    model_path = os.path.join(script_dir, "diamond_model")

    if not os.path.exists(model_path):
        print(
            f"Model not found at: {model_path}\n"
            "Run train_model.py first to generate the model.",
            file=sys.stderr
        )
        return 1

    spark = (
        SparkSession.builder
        .appName("DiamondPricePredict")
        .master("local[1]")
        .config("spark.driver.memory", "1g")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.sql.execution.arrow.pyspark.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.python.worker.reuse", "false")
        .config("spark.python.worker.faulthandler.enabled", "true")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        pipeline_model = PipelineModel.load(model_path)

        # Use spark.range(1).select(lit(...)) instead of createDataFrame([{...}]).
        # createDataFrame from a Python dict list serializes data through a Python
        # worker process — which crashes on Windows when launched as a subprocess
        # of Java (SpringBoot). lit() values are pure Scala operations; no Python
        # worker is spawned at all.
        input_row = spark.range(1).select(
            F.lit(carat).alias("carat"),
            F.lit(cut).alias("cut"),
            F.lit(color).alias("color"),
            F.lit(clarity).alias("clarity"),
            F.lit(depth).alias("depth"),
            F.lit(table).alias("table"),
            F.lit(x_val).alias("x"),
            F.lit(y_val).alias("y"),
            F.lit(z_val).alias("z"),
            F.lit(0.0).alias("price"),
        )

        result = pipeline_model.transform(input_row)
        predicted_price = max(result.select("prediction").collect()[0][0], 0.0)

        print(f"{predicted_price:.2f}")
        return 0

    finally:
        spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())