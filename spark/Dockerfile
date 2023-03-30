FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parse_uniprot_xml_spark.py .

CMD ["python", "parse_uniprot_xml_spark.py"]
