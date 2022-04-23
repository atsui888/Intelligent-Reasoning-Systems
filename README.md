# Project: Personal Financial Butler
for Intelligent Reasoning Systems (IRS) Module <br>
Master of Technology in Intelligent Systems<br>
National University of Singapore (Institute of System Science)<br>

This folder holds the contents of the IRS practice module from Jan 2022 to June 2022, which is part of the requirements to attaining the Masters of Technology.

Project Name: 
- Personal Financial Butler

Project Objective
- To empower users with Personal Finance Advice by recommending a personalized Investment Portfolio Allocation.

Team
- Richard Chai
 -   https://www.linkedin.com/in/richardchai/
 -   atsuishisen@gmail.com

- Koh Hong Wei
 
 

In this module, we will be implementing a forward chaining rule engine, a managed fund recommendation engine and also a stock forecasting module.

Forward chaining (or forward reasoning) is one of the two main methods of reasoning when using an inference engine and can be described logically as repeated application of modus ponens. Forward chaining is a popular implementation strategy for expert systems, business, and production rule systems. Forward chaining starts with the available data and uses inference rules to extract more data (from an end user, for example) until a goal is reached. The name "forward chaining" comes from the fact that the inference engine starts with the data and reasons its way to the answer. 

Because the data determines which rules are selected and used, this method is called data-driven. 

One of the advantages of forward-chaining over backward-chaining is that the reception of new data can trigger new inferences, which makes the engine better suited to dynamic situations in which conditions are likely to change.
Source: https://en.wikipedia.org/wiki/Forward_chaining

![IFB_Hybrid Reasoning System_flow_1920](https://user-images.githubusercontent.com/18540586/164889798-10a402c8-78a1-4134-899f-68c1b2c2c504.png)

In the fund recommendation module, we take two approaches, user-similarity and item-similarity. This allows us to make recommendations based on how similar each user is to others and in situations where even if we have insufficient information about the user, we can still provide recommendations as long as the user has clicked on an item in the app or if we placed a default item in the user's screen. The user-based similarity functionality takes into account each user's risk appetite, investment goals and stock/bond allocation. 

The Stock forecasting module enables us to predict future stock prices with a certain confidence level which we use to make recommendations to the user. In a subsequent enhancement, a portfolio optimisation module is planned for, which uses Genetic Algorithm to create a optimised stock and bond portfolio for the user based on the above factors and in addition, the user's budget.


The proof-of-concept app can be viewed here: https://bit.ly/3jQ0Df0

