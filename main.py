from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Set up Chrome options
options = Options()
# Comment out the headless option to see the browser
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Specify the path to ChromeDriver
chrome_driver_path = "/opt/homebrew/bin/chromedriver"

# Initialize the WebDriver with the specified ChromeDriver path
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Login to LinkedIn (you'll need to handle the login manually)
driver.get('https://www.linkedin.com/login')
time.sleep(3)

# Input your LinkedIn credentials
username = driver.find_element("id", 'username')
username.send_keys('example@email.com')  # Replace with your LinkedIn email
password = driver.find_element("id", 'password')
password.send_keys('password')  # Replace with your LinkedIn password
password.send_keys("\n")
time.sleep(5)

# Search for posts with keywords "hiring" and "Gurgaon" from the last 15 days
search_url = (
    'https://www.linkedin.com/search/results/content/?keywords=hiring%20gurgaon&sortBy=%22date_posted%22&f_TPR=r1296000'  # Adjust the time range to 15 days
)
driver.get(search_url)
time.sleep(5)

# Scroll to load more posts
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Scrape posts
post_links = []
post_contents = []

# Update the XPath based on manual inspection
posts = driver.find_elements("xpath", '//div[@class="search-result__info pt3 pb4 ph0"]')
print(f"Found {len(posts)} posts.")

for post in posts:
    try:
        link_element = post.find_element("xpath", './/a')
        link = link_element.get_attribute('href')
        post_links.append(link)

        # Extract post content
        content_element = post.find_element("xpath", './/span')
        content = content_element.text
        if "hiring" in content.lower():
            post_contents.append(content)
        else:
            post_links.pop()  # Remove link if it doesn't meet criteria
    except Exception as e:
        print(f"Failed to process a post: {e}")
        if post_links:
            post_links.pop()  # Remove link if processing fails

# Check if any posts were captured
if not post_links:
    print("No posts were captured. Please check the element selectors and search URL.")
else:
    # Create a DataFrame and save to Excel
    df = pd.DataFrame({
        'Post Link': post_links,
        'Post Content': post_contents
    })

    df.to_excel('linkedin_hiring_gurgaon_posts.xlsx', index=False)

    print("Scraping completed and saved to 'linkedin_hiring_gurgaon_posts.xlsx'.")

# Clean up
driver.quit()

