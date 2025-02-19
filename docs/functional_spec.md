# Functional Spec

### Background

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
- [Institute for Health Metrics and Evaluation](https://vizhub.healthdata.org/gbd-results/)
- build a sheet using data from this document [International Profiles of Health Care Systems](https://www.commonwealthfund.org/sites/default/files/2020-12/International_Profiles_of_Health_Care_Systems_Dec2020.pdf)
- [WHO Global Health Workforce Data](https://www.who.int/data/gho/data/themes/topics/health-workforce)


### Use Cases

**Use Case 1: Looking into a specifc country's healthcare**

    User: Uses a toggle to filter the dash to show one country
    System: All visuals display only the one country's data
    User: Decides to add in two more countries to compare metrics and trends
    System: Updates to include multiple countries

**Use Case 2: See what countries have good access to healthcare**

    User: Click on Page/Icon for graph to show healthcare access across countries
    System: Show bar chart comparing countries and percentage of population with healthcare access
    User: Visually detects countries with higher percentages

**Use Case 3: Maintain and Update Dashboard: The system supports the technical user in maintaining the dashboard by integrating and updating data source**

    User: Accesses the back-end data integration module.
    System: Displays a list of connected data sources (e.g., WHO, Kaggle, international profiles).
    User: Initiates a data refresh to pull the latest information from the sources.
    System: Executes the data extraction, cleaning, and integration process.
    User: Monitors the data pipeline status through a dedicated dashboard module.
    System: Displays logs, error messages, and performance metrics for the data pipeline.
    User: Adjusts dashboard configurations based on new data insights or feedback from non-technical users.
    System: Updates visualizations and reports to reflect the latest data and improvements.
    User: Schedules regular maintenance tasks for future updates.
    System: Confirms the scheduling and displays upcoming maintenance tasks on the calendar view.

**Use Case 4: Explore Global Healthcare Trends: The system enables the journalist to explore and extract global healthcare trends for storytelling**

    User: Opens the dashboard and selects the “Global Trends” section.
    System: Presents interactive graphs and charts that depict various healthcare indicators across multiple countries.
    User: Clicks on a trend line representing health insurance systems to see country-specific data.
    System: Displays a detailed view comparing different countries’ insurance models and outcomes.
    User: Uses filtering options (e.g., region, income level) to narrow down the data.
    System: Updates the visualization in real time based on the selected filters.
    User: Exports visualizations and summary data to use in an article or report.
    System: Provides options to download images and data summaries in multiple formats.