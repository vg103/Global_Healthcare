# Use Case: the Politician
## Goals: 
1. compare their home country with others
2. identify weak spots in their country's healthcare system
## Steps:
1. execute virtual environment steps outlined in README.md
2. run data_prep/healthcare.py, uses data_prep/data folder
3. run data_prep/ranking.py, uses inner_merged_data.csv output from healthcare.py
4. run hcare/hcare.py by running command
    streamlit run hcare.py
5. navigate to streamlit dashboard in browser