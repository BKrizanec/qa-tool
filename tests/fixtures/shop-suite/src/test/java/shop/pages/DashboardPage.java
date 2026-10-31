package shop.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.testng.Assert;

public class DashboardPage {
    private final WebDriver driver;
    private final By heading = By.cssSelector("h1.dashboard");

    public DashboardPage(WebDriver driver) {
        this.driver = driver;
    }

    public void verifyDisplayed() {
        Assert.assertTrue(driver.findElement(heading).isDisplayed(), "Dashboard heading is not visible");
    }
}
