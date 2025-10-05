# Sprint 2 - A Minimum Viable Product (MVP)


## Sprint Goals

Develop a bare-bones, working web application that provides the key functionality of the system, then test and refine it so that it can serve as the basis for the final phase of development in Sprint 3.


---

## Implemented Database Schema

The implimented Database scheme stayed relatively similar to the original database design. However, I removed the ID key from contains, and created a join Primary key instead. 

![SCREENSHOT OF DB SCHEMA](screenshots/updatedDatabase.png)


---

## Initial Implementation

- Shows all customers and their orders from the database

- Be able to add customers to the database

- Summarises the wood orders from previous years with a Pi chart

- Search for customers in the list of customers

- Removes customers from the database


**PLACE SCREENSHOTS AND/OR ANIMATED GIFS OF THE SYSTEM HERE**


---

## Testing showing a list of customers from the database

Testing that the database will show a list of all the customers names in the database. 

List of names in the database:

![List of customer names in the database](screenshots/CustomersInDatabase.png)


List of names on the customers page on the website:
![List of Customers on the website](screenshots/CustomersOrderedByAge.png)

### Changes / Improvements

I decided it would be more efficiant to order the customers by their name alphabetically, rather than by how long they've been in the database. 

![List of customer names on the website](screenshots/CustomerNamesOnWebsite.png)


---

## Testing adding customers to the database

I am testing the page to add customers to the database. 

List of customers before I added any: 

![Before adding a customer](screenshots/CustomersInDatabase.png)


Adding:
![adding a customer](screenshots/addingACustomer.gif)

After:

![added a customer](screenshots/databaseAfterAdding.png)


### Changes / Improvements



No changes were necesary. 

---

## Testing the summary of previous orders

Testing the amount and types of wood sold from previous years getting summarised with a chart on the wood page. 

Some of the quanitities and the wood they belong to in the contains table.

![some of the quanitites and the wood they belong to in the contains table.](screenshots/qtyofwoodincontainstable.png)

The wood type the ID  corresponds to:

![the ids the woods match up with](screenshots/theIDS.png)

![pi chart in action](screenshots/PichartTesting.gif)


### Changes / Improvements

No changes were necesary. 

---

## Testing searching for customers in the customers list

In the customers table, I am testing the search bar to help the user find certain customers without scrolling. 

![The search bar in action](screenshots/TestingSearchBar.gif)

### Changes / Improvements

No changes were necesary. 




---

## End User Feedback

I showed this design to my end user, and the feedback given was

> We need a confirmination screen before a customer was deleted.

![Delete Confirm](screenshots/deleteConfirm.gif)

After showing this to my end-user they saidto change the feedback given after a customer was deleted, to show their name.

Before Changing:

![customer deleted](screenshots/customerDeleted.png)

After Changing:

![Customer deletion changed](screenshots/deleteME.png)

I showed this to the end-user again, in which they said the prototype was working as intended. 


## Testing removing customers from the database

Testing to make sure, when the remove button is pressed, the customer gets removed from the database.

Database before he was removed

![Database before he was removed](screenshots/databaseAfterAdding.png)

Removing him:

![Deleting a customer](screenshots/deletingCustomers.gif)

Database after:

![database after deleting](screenshots/CustomersInDatabase.png)

---

## Sprint Review

Functionality with adding customers was a struggle, but once it was working the rest of the sprint went smoothly. Linking the tables in the form was difficult 

