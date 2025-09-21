# DSP Mapping
This is a small ETL service I created for my role at Bella Figura Music.

The script uses the BigQuery API to read data from the central datawarehouse. It checks for new values that are not currently categorised, and maps them to a clean value. 

Using Flask and Docker, I containerise the code and upload to GCP artifact registry before automating it with CloudRun and Cloud Scheduler


# Setup
- Create a virtual environment
- Run:
```bash
pip install poetry
poetry install
```

### To update dependencies:
```bash
poetry lock
```

# Running locally
Authenticate with Google:
```bash
gcloud auth application-default login
```

### Run the script
```bash
make run    #Run without posing to BigQuery
make post   #Post to BigQuery manually
```


# Cleaning / Formatting:
Github action to check pylint score will run on push. Run the commands below to check score / format.
```bash
make pylint     # Return pylint score
make black      # Auto format code
```

