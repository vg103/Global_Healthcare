# Use Case: Journalist
## Goals:
1. Explore general trends in a specific country's healthcare system
2. Compare general trends in systems across countries
## Steps:
1. Execute virtual environment steps outlined in README.md
2. From Global_Healthcare, run dahsboard by running command
```streamlit run hcare/hcare.py```
3. Navigate to streamlit dashboard in browser
4. User navigates to "Country Overview" tab to view their country of interest, Spain
5. User selects the Spain and year 2020 to view chart
6. User navigates to "WHO Data" tab
7. User selects the year 2020, region of Europe, and Spain and some neighboring countries like Portugal and France for comparison
8. User sees that similar to Portugal, Spain has a much higher ratio of medical doctors to nurses & midwifes than France
9. User goes back to the "Home" tab to see how this has impacted its rank over time
10. For the "Composite Score or Ranking Over Time by Country" graph, user selcets the 3 countries and views the graph
11. User sees that Portugal and Spain both have improving trends in their ranks over recent years while France's ranking has been steadily getting worse. From this user is intrigued to further investigate how the ratio of medical doctors to nurses & midwifes impacts the country's healthcare outcomes.