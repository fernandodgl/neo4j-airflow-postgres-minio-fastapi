import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StructType, StructField, StringType
import xmlschema
import pandas as pd

def parse_xml(xml_content: str):
    schema = xmlschema.XMLSchema('https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot.xsd')
    entry_dict = schema.to_dict(xml_content)
    return entry_dict.get("entry", [])

def parse_xml_udf(xml_content: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([parse_xml(x) for x in xml_content])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: parse_uniprot_xml_spark.py <input> <output>", file=sys.stderr)
        sys.exit(-1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    spark = SparkSession.builder.appName("ParseUniprotXML").getOrCreate()

    schema = StructType([
        StructField("xml_content", StringType(), True)
    ])

    df = spark.read.text(input_path).withColumnRenamed("value", "xml_content")

    parse_xml_pandas_udf = pandas_udf(parse_xml_udf, returnType=schema)

    parsed_df = df.select(parse_xml_pandas_udf("xml_content").alias("entry"))

    parsed_df.write.json(output_path)

    spark.stop()
