# Suite trust audit: SeleniumCucumber

Read **10 scenarios** in 4 feature files, traced through 11 step definitions and 0 page objects.

| Severity | Findings |
|---|---|
| 🔴 High | 1 |
| 🟠 Medium | 8 |

## What the scenarios claim vs. what they check

### 🔴 High: Scenario "Adding multiple item into the cart" verifies nothing

*Scenario:* Search with specific filter and add it to cart › Adding multiple item into the cart  
*Where:* `SearchWithFilter.feature:37` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 12 steps contains a check that can fail. It passes as long as nothing crashes.
- It still reads as if it verifies 9 outcome(s): ": I select "JABRA" as the brand"; ": I select "£70 - £105" as the price filter"; ": I select the "JABRA Coach Headphones" with description as "Blue""; ": Add it to the cart"; ": I select "SAMSUNG" as the brand"; …

### 🟠 Medium: ": I should be at the "Laptops" search page with "35 items"" ignores the value it is given

*Affects 7 scenarios:* Adding a laptop to the Cart › Search Laptop and add it to the cart; Search feature of the web page › Search based on Tablets; Search feature of the web page › Search based on Cameras; Search feature of the web page › Search based on Mobile Phones; …  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/SearchStepDfn.java:41` · *Check:* `IGNORED_PARAM`

- Parameter(s) `title` are never used, so changing this value in the feature file has no effect.

### 🟠 Medium: ": I select the "APPLE MacBook Pro Retina" with description as "15-inch, 256GB"" is written as a check but is an action

*Affects 4 scenarios:* Adding a laptop to the Cart › Search Laptop and add it to the cart; Search with specific filter and add it to cart › Validation of Item Bag page; Search with specific filter and add it to cart › Adding multiple item into the cart; Adding a Tablet to the Cart › Search Tablet and add it to the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/LaptopCart.java:19` · *Check:* `MISLABELLED_THEN`

- It performs actions (click) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": Add it to the cart" is written as a check but is an action

*Affects 4 scenarios:* Adding a laptop to the Cart › Search Laptop and add it to the cart; Search with specific filter and add it to cart › Validation of Item Bag page; Search with specific filter and add it to cart › Adding multiple item into the cart; Adding a Tablet to the Cart › Search Tablet and add it to the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/LaptopCart.java:26` · *Check:* `MISLABELLED_THEN`

- It performs actions (click) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": Navigate to user details page and provide the following details" is written as a check but is an action

*Affects 4 scenarios:* Adding a laptop to the Cart › Search Laptop and add it to the cart; Search with specific filter and add it to cart › Validation of Item Bag page; Search with specific filter and add it to cart › Adding multiple item into the cart; Adding a Tablet to the Cart › Search Tablet and add it to the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/LaptopCart.java:32` · *Check:* `MISLABELLED_THEN`

- It performs actions (click, selectByVisibleText, sendKeys) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": I select "SONY" as the brand" is written as a check but is an action

*Affects 3 scenarios:* Search with specific filter and add it to cart › Search based on Speakers; Search with specific filter and add it to cart › Validation of Item Bag page; Search with specific filter and add it to cart › Adding multiple item into the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/SearchWithFilter.java:26` · *Check:* `MISLABELLED_THEN`

- It performs actions (click) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": I select "£40 - £80" as the price filter" is written as a check but is an action

*Affects 3 scenarios:* Search with specific filter and add it to cart › Search based on Speakers; Search with specific filter and add it to cart › Validation of Item Bag page; Search with specific filter and add it to cart › Adding multiple item into the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/SearchWithFilter.java:32` · *Check:* `MISLABELLED_THEN`

- It performs actions (click) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": I change the quantity to "2" and click on update button" is written as a check but is an action

*Scenario:* Search with specific filter and add it to cart › Validation of Item Bag page  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/SearchWithFilter.java:38` · *Check:* `MISLABELLED_THEN`

- It performs actions (clear, click, sendKeys) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

### 🟠 Medium: ": I change the quantity of item "SAMSUNG Gear S2 Smartwatch" to "3" and click on update button" is written as a check but is an action

*Scenario:* Search with specific filter and add it to cart › Adding multiple item into the cart  
*Where:* `src/test/java/com/cucumber/framework/stepdefinition/SearchWithFilter.java:44` · *Check:* `MISLABELLED_THEN`

- It performs actions (clear, click, sendKeys) and nothing in it can fail the test, but `Then` tells readers it verifies an outcome.

