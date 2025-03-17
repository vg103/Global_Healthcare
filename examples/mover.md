# Use Case: the Future Mover
## Goals:
1. identify top ranked countries
2. identify which countries among a set of their choosing have the highest rate of medical staff
3. compare a particular country of interest with their current home country (if home country is in dataset)
## Steps:
1. execute virtual environment steps outlined in README.md
2. run data_prep/healthcare.py, uses data_prep/data folder
3. run data_prep/ranking.py, uses inner_merged_data.csv output from healthcare.py
4. run hcare/hcare.py by running command
    streamlit run hcare.py
5. navigate to streamlit dashboard in browser