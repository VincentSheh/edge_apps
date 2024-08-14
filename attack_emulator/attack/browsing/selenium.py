from selenium import webdriver

# Set up WebDriver
driver = webdriver.Chrome('/path/to/chromedriver')

# Navigate to the website
driver.get("http://parkingtracker.com")

# Add any interaction you want here, such as clicking a button or filling a form

# Close the browser
driver.quit()
