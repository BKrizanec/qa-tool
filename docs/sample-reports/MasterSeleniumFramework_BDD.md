# Suite trust audit: MasterSeleniumFramework_BDD

Read **8 scenarios** in 2 feature files, traced through 19 step definitions and 1 page objects.

| Severity | Findings |
|---|---|
| 🟠 Medium | 1 |

## What the scenarios claim vs. what they check

### 🟠 Medium: "I should see an error" always fails

*Scenario:* Add to cart › Show an error when try to add zero quantity  
*Where:* `src/test/java/awesomecucumber/stepdefinitions/ProductStepDefinitions.java:55` · *Check:* `ALWAYS_FAILS`

- `Assert.fail("Failing this step intentionally to check the screenshot attached int the Report")` runs every time (line 58), so this step can never pass and nothing after it runs.
- A permanently red test teaches the team to ignore failures.

