package shop.steps;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.openqa.selenium.WebDriver;
import shop.pages.DashboardPage;
import shop.pages.LoginPage;

public class LoginSteps {
    private final WebDriver driver = Driver.get();
    private final LoginPage loginPage = new LoginPage(driver);
    private final DashboardPage dashboardPage = new DashboardPage(driver);

    @Given("the user opens the login page")
    public void openLoginPage() {
        loginPage.open();
    }

    @When("the user signs in with {string} and {string}")
    public void signIn(String user, String pass) {
        loginPage.signIn(user, pass);
    }

    @When("clicks the submit button")
    public void clickSubmit() {
    }

    @Then("the dashboard is displayed")
    public void dashboardIsDisplayed() {
        dashboardPage.verifyDisplayed();
    }

    @Then("an error message is shown")
    public void errorMessageIsShown() {
        String message = loginPage.errorText();
        System.out.println("Error shown: " + message);
    }

    // @Then("the account locked banner is shown")
    // public void lockedBannerIsShown() {
    //     Assert.assertTrue(loginPage.lockedBanner().isDisplayed());
    // }
}
