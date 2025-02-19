# Component Spec

**Component 1: Country Filter on Visualization**

What it does: Filters for one or multiple countries and updates views to reflect it

Inputs: Countries to filter on, data, visualizations

    displayVisual(data, filters={}):

        if there are countries in filter, then filter df to only those

        build visual using the filtered df
        
        show visual

**Component 2: Ranking Algorithm**

What it does: Assess a country's healthcare infrastructure and its effectiveness

Inputs: Factor Values by country (i.e. death rates for certain diseases, doctors per 10,000 people)

    - PCA or aggregate score on factors

Outputs: Numerical score (possibly out of 100) for each country

**Component 3: Visualization Manager**

What it does: displays dataframes as graphs, filters by factor or country based on user specification

Input: User selection of graph which graph to expand, user input of filter factor

Output: Graph that filters based on user spec

**Component 4: Web App**

What it does: provides the interface where user can view graphs by factor or country in order to draw conclusions on global healthcare systems

Inputs: User Selection (clicks)

Outputs: Whichever graph was selected

**Interaction Diagrams**

Diagram for Use Case 1: Looking into a specifc country's healthcare
![Component1](comp1.png)

Diagram for Use Case 2:
![Component2](mermaid-diagram-2025-02-18-182722.png)



