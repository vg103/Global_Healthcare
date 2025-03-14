# Functional Spec

### Background
This dashboard addresses the need for a data backed platform to help various types of users, such as policymakers, journalists, and individuals looking to evaluate healthcare systems worldwide. Since the quality of healthcare varies between countries and over time, this dashboard provides users with valuable insights into these differences. The interactive visualizations and filters enable users to explore data and find answers to their specific questions.

### User Profiles:

**User 1: Policymaker**

	- wants to know how good their county's healthcare system is, identify strengths and weaknesses to address in future policy, if the country has enough medical staff for their population
	- interacts by using the dashboard, filtering visualizations
	- needs to isolate the information for their specific country and compare with stats of other countries of their choosing
	- not technical, skills include graph comprehension and dashboard navigation

**User 2: Person looking to move to a new country**
    - wants to see countries with top healthcare systems
    - interacts by using the dashboard, seeing average stats across all countries, highlighting top countries
    - needs to see which countries are at the top of different categories
    - not technical, skills include graph comprehension and dashboard navigation

**User 3: Journalist who communicates healthcare trends and issues to the public**

	- wants to compare healthcare systems across countries to highlight success factors and challenges
	- interacts by comparing countries 
	- needs to see high-level trends across countries and over time
	- Moderately non-technical; they understand the importance of data but are not experts in analytics.

### Data Sources
to be merged over country, which is a field in all of the below datasets
- [Institute for Health Metrics and Evaluation](https://vizhub.healthdata.org/gbd-results/)
- [WHO Global Health Workforce Data](https://www.who.int/data/gho/data/themes/topics/health-workforce)


### Use Cases

**Use Case 1: Looking into a specifc country's healthcare**

    User: Uses a toggle to filter the dash to show one country
    System: All visuals display only the one country's data
    User: Decides to add in two more countries to compare metrics and trends
    System: Updates to include multiple countries

**Use Case 2: Explore top countries according to ranking algorithm**
    User: Opens dashboard and navigates to top countries from algorithm output
    System: Runs ranking algorithm and outputs visualization to show a list of all countries in ranked order
    User: Scrolls through ranked country list

**Use Case 3: Explore Global Healthcare Trends: The system enables the journalist to explore and extract global healthcare trends for storytelling**

    User: Opens the dashboard and selects the “Global Trends” section.
    System: Presents interactive graphs and charts that depict various healthcare indicators across multiple countries.
    User: Clicks on a trend line representing health insurance systems to see country-specific data.
    System: Displays a detailed view comparing different countries’ insurance models and outcomes.
    User: Uses filtering options (e.g., region, income level) to narrow down the data.
    System: Updates the visualization in real time based on the selected filters.
    User: Exports visualizations and summary data to use in an article or report.
    System: Provides options to download images and data summaries in multiple formats.