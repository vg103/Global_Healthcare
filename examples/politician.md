# Use Case: the Politician
## Goals: 
1. Compare their home country with others
2. Identify weak spots in their country's healthcare system
## Steps:
1. Execute virtual environment steps outlined in README.md
2. From Global_Healthcare, run dahsboard by running command
```streamlit run hcare/hcare.py```
3. Navigate to streamlit dashboard in browser
4. User navigates to teh "Data over Time" tab to learn how their country of New Zealand is doing
5. User selects the region of their country, Western Pacific, and selects New Zealand, Australia, and Japan for comparison
6. User sees that New Zealand has less medical doctors per population than Australia, but more then Japan. User also learns that in recent years its rate of nurses per population is lower than both Japan and Austraila.
7. User wants to see how this is affecting the people of New Zealand, and navigates to the "IHME Data" tab
8. User once again selects New Zealand, Australia, and Japan for comparison, and selects all causes
9. User can see that although New Zealand has a lower rate of both nurses and medical doctors than Australia, both countries have similar death rates due to the causes. This gives the polititian some hope that they are doing okay, but could aim to improve policy for even better healthcare for their country.