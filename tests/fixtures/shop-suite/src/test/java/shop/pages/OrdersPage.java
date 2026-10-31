package shop.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.testng.Assert;

public class OrdersPage {
    private final WebDriver driver;
    private final By rows = By.cssSelector("table.orders tr");

    public OrdersPage(WebDriver driver) {
        this.driver = driver;
    }

    public void verifyHasOrders() {
        Assert.assertFalse(driver.findElements(rows).isEmpty(), "No orders listed");
    }
}
