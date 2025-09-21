# DSP Mapping
This is an ETL service I created for data mapping and consolidation.

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

---
## Project .py files overview

`Main.py` to run the full project

`compare_vs_original_mapping.py` houses a class to compare the original data mapping vs the current values now present in the datasets

`dsps.py` contains the key: value pairs to map data to. i.e. if a value in the dataset = one of the values in the dictionary, assign the key. 
