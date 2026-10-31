package shop.runners;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(features = "src/test/resources/features", glue = "shop.steps")
public class TestRunner extends AbstractTestNGCucumberTests {
}
