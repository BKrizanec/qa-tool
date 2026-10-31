# Suite trust audit: AutomationFrameworkCucumberTestNG

Read **4 scenarios** in 3 feature files, traced through 14 step definitions and 7 page objects.

| Severity | Findings |
|---|---|
| 🟠 Medium | 4 |
| 🟡 Low | 4 |

## What the scenarios claim vs. what they check

### 🟠 Medium: "User navigate to url "<url>"" is switched off: its code is commented out

*Scenario:* Sign in page CRM › Sign in CRM with an email valid  
*Where:* `src/test/java/com/anhtester/projects/website/crm/stepdefinitions/LoginSteps.java:15` · *Check:* `DISABLED_STEP`

- It does nothing when it runs. Commented-out code: `WebUI.getURL(url);`
- The Examples column(s) `url` feed this step, but nothing uses them. Changing the test data has no effect.

### 🟠 Medium: "The user can not redirect to Dashboard page" checks something different from what it says

*Scenario:* Sign in page CRM › Sign in CRM with an email invalid  
*Where:* `src/test/java/com/anhtester/projects/website/crm/stepdefinitions/LoginSteps.java:39` · *Check:* `INTENT_MISMATCH`

- What it actually checks: verify element not present: `getSignInPage().labelEmailError` (xpath: //span[@id='email-error'])
- None of that refers to: dashboard, redirect.
- The scenario's real check is hidden in another step: "User login with username "<username>" and password "<password>" invalid" → verifySignInFail() → assert true: `checkElementExist(alertErrorMessage)`; "User login with username "<username>" and password "<password>" invalid" → verifySignInFail() → assert equals: `getTextElement(alertErrorMessage)`, `"Authentication failed!"`

### 🟡 Low: "User navigate to dashboard" only checks, it does not act

*Scenario:* HRM dashboard page › Open menu  
*Where:* `src/test/java/com/anhtester/projects/website/crm/stepdefinitions/DashboardSteps.java:26` · *Check:* `CHECK_ONLY_ACTION_STEP`

- The wording describes an action, but the code performs no clicks, typing or navigation. It only verifies: verify element visible: `By.xpath("//span[normalize-space()='Home']")` (xpath: //span[normalize-space()='Home']), `20`

### 🟡 Low: "click Login button" does nothing

*Scenario:* Login Test CMS › Login success  
*Where:* `src/test/java/com/anhtester/projects/website/cms/stepdefinitions/LoginSteps.java:32` · *Check:* `EMPTY_STEP`

- The step definition is empty, so the scenario reads as if this happens as a separate step, but nothing runs.

## Across the suite

### 🟠 Medium: Page object `ClientPageCRM` is never used by any scenario

*Where:* `src/test/java/com/anhtester/projects/website/crm/pages/Clients/ClientPageCRM.java` · *Check:* `ORPHAN_PAGE_OBJECT`

- It defines 24 locator(s) and 5 method(s), including checks such as `addClient`, `checkClientDetail`. None of it runs, so this area of the app looks covered but isn't.

### 🟠 Medium: Page object `ProjectPageCRM` is never used by any scenario

*Where:* `src/test/java/com/anhtester/projects/website/crm/pages/Projects/ProjectPageCRM.java` · *Check:* `ORPHAN_PAGE_OBJECT`

- It defines 2 locator(s) and 2 method(s). None of it runs, so this area of the app looks covered but isn't.

### 🟡 Low: Soft assertions can hide failures

*Where:* `src/main/java/com/anhtester/keywords/WebUI.java:59` · *Check:* `SOFT_ASSERT_RISK`

- `WebUI.softAssert` is one static object shared by every scenario and never reset, so one soft failure would also fail every scenario after it (and mixes results across parallel threads).
- Soft failures are collected in `Hooks.afterScenario` (line 113) after the scenario's status is read (line 96), so reports built from that status count soft-failed scenarios as passed.
- Latent: only used by `ClientPageCRM`, which no scenario runs yet.

### 🟡 Low: The failure message "The Dashboard page not display." is used for different checks

*Where:* `src/test/java/com/anhtester/projects/website/crm/pages/SignIn/SignInPageCRM.java:93` · *Check:* `REUSED_FAILURE_MESSAGE`

- When one of them fails, the report points at the wrong problem:
- src/test/java/com/anhtester/projects/website/crm/pages/SignIn/SignInPageCRM.java:93 checks `checkElementExist(getDashboardPage().menuDashboard)`
- src/test/java/com/anhtester/projects/website/crm/pages/SignIn/SignInPageCRM.java:98 checks `checkElementExist(alertErrorMessage)`

