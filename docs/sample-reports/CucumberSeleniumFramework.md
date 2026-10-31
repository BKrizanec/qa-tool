# Suite trust audit: CucumberSeleniumFramework

Read **54 scenarios** in 14 feature files, traced through 21 step definitions and 0 page objects.

| Severity | Findings |
|---|---|
| 🔴 High | 41 |
| 🟡 Low | 18 |

## What the scenarios claim vs. what they check

### 🔴 High: "user is already on Login Page" has no working step definition

*Affects 3 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Deal data creation › Free CRM Create a new deal scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:23` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:23`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "title of login page is Free CRM" has no working step definition

*Affects 3 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Deal data creation › Free CRM Create a new deal scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:30` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:30`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user enters "<username>" and "<password>"" has no working step definition

*Affects 2 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/LoginStepDefinition.java:40` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/LoginStepDefinition.java:40`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user clicks on login button" has no working step definition

*Affects 3 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Deal data creation › Free CRM Create a new deal scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:45` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:45`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user is on home page" has no working step definition

*Affects 3 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Deal data creation › Free CRM Create a new deal scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:53` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:53`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user moves to new contact page" has no working step definition

*Scenario:* Free CRM Create Contacts › Free CRM Create a new contact scenario  
*Where:* `src/main/java/stepDefinitions/LoginStepDefinition.java:62` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/LoginStepDefinition.java:62`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user enters contact details "<firstname>" and "<lastname>" and "<position>"" has no working step definition

*Scenario:* Free CRM Create Contacts › Free CRM Create a new contact scenario  
*Where:* `src/main/java/stepDefinitions/LoginStepDefinition.java:72` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/LoginStepDefinition.java:72`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "Close the browser" has no working step definition

*Affects 3 scenarios:* Free CRM Create Contacts › Free CRM Create a new contact scenario; Deal data creation › Free CRM Create a new deal scenario; Free CRM Login Feature › Free CRM Login Test Scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:79` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:79`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user enters username and password" has no working step definition

*Scenario:* Deal data creation › Free CRM Create a new deal scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:37` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:37`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user moves to new deal page" has no working step definition

*Scenario:* Deal data creation › Free CRM Create a new deal scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:61` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:61`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user enters deal details" has no working step definition

*Scenario:* Deal data creation › Free CRM Create a new deal scenario  
*Where:* `src/main/java/stepDefinitions/DealStepDefnition.java:70` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/DealStepDefnition.java:70`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user is on deal page" has no working step definition

*Scenario:* Free CRM app test › free crm create deal test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:22` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:22`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user fills the deals form" has no working step definition

*Scenario:* Free CRM app test › free crm create deal test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:27` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:27`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "deal is created" has no working step definition

*Scenario:* Free CRM app test › free crm create deal test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:32` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:32`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user is on contact page" has no working step definition

*Scenario:* Free CRM app test › free crm create contact test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:38` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:38`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "user fills the contact form" has no working step definition

*Scenario:* Free CRM app test › free crm create contact test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:44` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:44`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: "contact is created" has no working step definition

*Scenario:* Free CRM app test › free crm create contact test  
*Where:* `src/main/java/stepDefinitions/Hooks_StepDefinition.java:49` · *Check:* `UNDEFINED_STEP`

- Its step definition exists but is commented out at `src/main/java/stepDefinitions/Hooks_StepDefinition.java:49`.
- Cucumber reports the step as undefined; with `strict = false` (the default before Cucumber 7) the scenario does not fail.

### 🔴 High: Scenario "This is First test" verifies nothing

*Scenario:* Test Tagged Hooks › This is First test  
*Where:* `taggedhooks.feature:4` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 3 steps contains a check that can fail. It passes as long as nothing crashes.
- It still reads as if it verifies 1 outcome(s): "this is the third step"

### 🔴 High: "this is the third step" claims to verify something but checks nothing

*Affects 3 scenarios:* Test Tagged Hooks › This is First test; Test Tagged Hooks › This is Second test; Test Tagged Hooks › This is Third test  
*Where:* `src/main/java/stepDefinitions/TaggedHooksStepDefinition.java:74` · *Check:* `HOLLOW_THEN`

- Nothing this step runs can make the test fail.

### 🔴 High: Scenario "This is Second test" verifies nothing

*Scenario:* Test Tagged Hooks › This is Second test  
*Where:* `taggedhooks.feature:10` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 3 steps contains a check that can fail. It passes as long as nothing crashes.
- It still reads as if it verifies 1 outcome(s): "this is the third step"

### 🔴 High: Scenario "This is Third test" verifies nothing

*Scenario:* Test Tagged Hooks › This is Third test  
*Where:* `taggedhooks.feature:16` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 3 steps contains a check that can fail. It passes as long as nothing crashes.
- It still reads as if it verifies 1 outcome(s): "this is the third step"

### 🔴 High: Scenario "Login with correct username and correct password" verifies nothing

*Scenario:* Free CRM application testing › Login with correct username and correct password  
*Where:* `tagging.feature:5` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Login with incorrect username and correct password" verifies nothing

*Scenario:* Free CRM application testing › Login with incorrect username and correct password  
*Where:* `tagging.feature:9` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Create a contact" verifies nothing

*Scenario:* Free CRM application testing › Create a contact  
*Where:* `tagging.feature:13` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Create a deal" verifies nothing

*Scenario:* Free CRM application testing › Create a deal  
*Where:* `tagging.feature:17` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Create a tasks" verifies nothing

*Scenario:* Free CRM application testing › Create a tasks  
*Where:* `tagging.feature:21` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Create a case" verifies nothing

*Scenario:* Free CRM application testing › Create a case  
*Where:* `tagging.feature:25` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Verify left panel links" verifies nothing

*Scenario:* Free CRM application testing › Verify left panel links  
*Where:* `tagging.feature:29` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a deal" verifies nothing

*Scenario:* Free CRM application testing › Search a deal  
*Where:* `tagging.feature:33` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a contact" verifies nothing

*Scenario:* Free CRM application testing › Search a contact  
*Where:* `tagging.feature:37` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a case" verifies nothing

*Scenario:* Free CRM application testing › Search a case  
*Where:* `tagging.feature:41` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a task" verifies nothing

*Scenario:* Free CRM application testing › Search a task  
*Where:* `tagging.feature:45` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a call" verifies nothing

*Scenario:* Free CRM application testing › Search a call  
*Where:* `tagging.feature:49` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search an email" verifies nothing

*Scenario:* Free CRM application testing › Search an email  
*Where:* `tagging.feature:53` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a docs" verifies nothing

*Scenario:* Free CRM application testing › Search a docs  
*Where:* `tagging.feature:57` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Search a forms" verifies nothing

*Scenario:* Free CRM application testing › Search a forms  
*Where:* `tagging.feature:61` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "validate a report" verifies nothing

*Scenario:* Free CRM application testing › validate a report  
*Where:* `tagging.feature:65` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "Application Logout" verifies nothing

*Scenario:* Free CRM application testing › Application Logout  
*Where:* `tagging.feature:69` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🔴 High: Scenario "browser closed" verifies nothing

*Scenario:* Free CRM application testing › browser closed  
*Where:* `tagging.feature:72` · *Check:* `SCENARIO_VERIFIES_NOTHING`

- None of its 1 steps contains a check that can fail. It passes as long as nothing crashes.
- It has no `Then` steps at all.

### 🟡 Low: "This is a valid login test" does nothing

*Scenario:* Free CRM application testing › Login with correct username and correct password  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:19` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a invalid login test" does nothing

*Scenario:* Free CRM application testing › Login with incorrect username and correct password  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:23` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a contact test case" does nothing

*Scenario:* Free CRM application testing › Create a contact  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:27` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a deal test case" does nothing

*Scenario:* Free CRM application testing › Create a deal  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:31` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a tasks test case" does nothing

*Scenario:* Free CRM application testing › Create a tasks  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:35` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a case test case" does nothing

*Scenario:* Free CRM application testing › Create a case  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:39` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "clicking on left panel links" does nothing

*Scenario:* Free CRM application testing › Verify left panel links  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:43` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search deal test" does nothing

*Scenario:* Free CRM application testing › Search a deal  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:47` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search contact test" does nothing

*Scenario:* Free CRM application testing › Search a contact  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:51` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search case test" does nothing

*Scenario:* Free CRM application testing › Search a case  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:55` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search task test" does nothing

*Scenario:* Free CRM application testing › Search a task  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:59` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search call test" does nothing

*Scenario:* Free CRM application testing › Search a call  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:63` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search email test" does nothing

*Scenario:* Free CRM application testing › Search an email  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:67` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search docs test" does nothing

*Scenario:* Free CRM application testing › Search a docs  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:71` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a search forms test" does nothing

*Scenario:* Free CRM application testing › Search a forms  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:75` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a report test" does nothing

*Scenario:* Free CRM application testing › validate a report  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:79` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a logout test" does nothing

*Scenario:* Free CRM application testing › Application Logout  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:83` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

### 🟡 Low: "This is a close broswer test" does nothing

*Scenario:* Free CRM application testing › browser closed  
*Where:* `src/main/java/stepDefinitions/TaggingStepDefinition.java:87` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

## Across the suite

### 🔴 High: Runner `TestRunner` points to an absolute path

*Where:* `src/main/java/MyRunner/TestRunner.java` · *Check:* `RUNNER_ABSOLUTE_PATH`

- `features = "/Users/NaveenKhunteta/Documents/workspace/FreeCrmBDDFramework/src/main/java/Features/taggedhooks.feature"` exists only on the original author's machine. Anywhere else (CI, a colleague's laptop) this runner finds no features.

### 🔴 High: 14 of 14 feature files are not run by any runner

*Where:* `runners` · *Check:* `FEATURES_NEVER_RUN`

- No `@CucumberOptions` runner includes them, so their scenarios never execute (unless they are run some other way, e.g. a JUnit Platform suite or the IDE):
- `src/main/java/Features/contacts.feature`
- `src/main/java/Features/deals.feature`
- `src/main/java/Features/dealsmap.feature`
- `src/main/java/Features/hooks.feature`
- `src/main/java/Features/login.feature`
- `src/main/java/Features/taggedhooks.feature`
- `src/main/java/Features/tagging.feature`
- `target/classes/Features/contacts.feature`
- `target/classes/Features/deals.feature`
- `target/classes/Features/dealsmap.feature`
- …and 4 more

