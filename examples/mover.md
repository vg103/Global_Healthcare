# Use Case: the Future Mover
## Goals:
1. Identify top ranked countries
2. Identify which countries among a set of their choosing have the highest rate of medical staff
3. Compare a particular country of interest with their current home country (if home country is in dataset)
## Steps:
1. Execute virtual environment steps outlined in README.md
2. From Global_Healthcare, run dahsboard by running command
```streamlit run hcare/hcare.py```
3. Navigate to streamlit dashboard in browser
4. On the home page, user selects the most recent year from the drop down.
5. User sees the top 5 ranked countries in the year 2021 being: Malta, Finland, Norway, Portugal, and Denmark
6. User selects all 5 countries to view their composite score in the graph below the rankings
7. User sees that although Portugal was ranked 4th, the country has the steepest rate of improvement in the past 20 years and wants to learn more
8. User navigates to "Data by Country" and "Country Overview" tabs to learn more about Portugal