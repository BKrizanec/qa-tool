Feature: Login

  Scenario: Valid login
    Given the user opens the login page
    When the user signs in with "alice" and "secret"
    Then the dashboard is displayed

  Scenario: Wrong password
    Given the user opens the login page
    When the user signs in with "alice" and "wrong"
    And clicks the submit button
    Then an error message is shown

  Scenario: Locked account
    Given the user opens the login page
    When the user signs in with "bob" and "secret"
    Then the account locked banner is shown
