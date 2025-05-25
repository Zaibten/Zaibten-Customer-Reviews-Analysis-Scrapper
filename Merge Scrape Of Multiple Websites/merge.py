import csv
import re
from urllib.parse import quote
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def clean_text(text):
    """Clean text by removing extra whitespace and special characters."""
    return re.sub(r'\s+', ' ', text.strip())

def setup_driver():
    """Set up Chrome WebDriver with options."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # Assuming ChromeDriver is in PATH; update path if needed
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_amazon_reviews(product_name, driver, max_stores=5):
    """Scrape one review from each of the first max_stores product listings on Amazon."""
    reviews = []
    search_url = f"https://www.amazon.com/s?k={quote(product_name)}"
    print("this is amazon link: ", search_url)
    time.sleep(30)
    scrape_time = "01:28 AM PKT, Sunday, May 25, 2025"

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        
        # Find product links
        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-no-outline')[:max_stores]
        if not product_links:
            print("No product listings found on Amazon.")
            return reviews

        product_urls = [link.get_attribute('href') for link in product_links]
        
        for url in product_urls:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                
                # Get the first review
                try:
                    review = driver.find_element(By.CSS_SELECTOR, 'span[data-hook="review-body"]').text
                    reviews.append((clean_text(review), scrape_time))
                except:
                    reviews.append(("No review found for this product.", scrape_time))

            except WebDriverException as e:
                print(f"Error scraping Amazon product {url}: {e}")
                reviews.append(("Error retrieving review.", scrape_time))

    except (TimeoutException, WebDriverException) as e:
        print(f"Error scraping Amazon search page: {e}")
    return reviews

def scrape_ebay_reviews(product_name, driver, max_stores=5):
    """Scrape one review from each of the first max_stores product listings on eBay."""
    reviews = []
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote(product_name)}"
    print("this is ebay link: ", search_url)
    time.sleep(30)
    scrape_time = "01:28 AM PKT, Sunday, May 25, 2025"

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        
        # Find product links
        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.s-item__link')[:max_stores]
        if not product_links:
            print("No product listings found on eBay.")
            return reviews

        product_urls = [link.get_attribute('href') for link in product_links]
        
        for url in product_urls:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                
                # Get the first review
                try:
                    review = driver.find_element(By.CSS_SELECTOR, '#s0-23-25-26-19-4-19\[0\]-\@x-feedback-detail-list-14-tabpanel-0 > div > div > ul > li > div > div.fdbk-container__details__top > div > span').text
                    reviews.append((clean_text(review), scrape_time))
                except:
                    reviews.append(("No review found for this product.", scrape_time))

            except WebDriverException as e:
                print(f"Error scraping eBay product {url}: {e}")
                reviews.append(("Error retrieving review.", scrape_time))

    except (TimeoutException, WebDriverException) as e:
        print(f"Error scraping eBay search page: {e}")
    return reviews

def save_to_csv(product_name, amazon_reviews, ebay_reviews):
    """Save reviews to a CSV file with timestamp."""
    filename = f"{product_name.replace(' ', '_')}_reviews.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product Name', 'Review', 'Source', 'Scraped At'])

        for i, (review, scrape_time) in enumerate(amazon_reviews, 1):
            writer.writerow([product_name, review, f'Amazon Store {i}', scrape_time])
        for i, (review, scrape_time) in enumerate(ebay_reviews, 1):
            writer.writerow([product_name, review, f'eBay Store {i}', scrape_time])

def main():
    try:
        product_name = input("Enter the product name to search for reviews (press Enter for default 'wireless mouse'): ").strip()
        if not product_name:
            product_name = "wireless mouse"
    except EOFError:
        product_name = "wireless mouse"

    print(f"Scraping reviews for: {product_name}")
    
    driver = setup_driver()
    try:
        amazon_reviews = scrape_amazon_reviews(product_name, driver)
        ebay_reviews = scrape_ebay_reviews(product_name, driver)
        
        if not amazon_reviews and not ebay_reviews:
            print("No reviews found on either website.")
            return

        save_to_csv(product_name, amazon_reviews, ebay_reviews)
        print(f"Reviews saved to {product_name.replace(' ', '_')}_reviews.csv")
        print(f"CSV file saved in: {os.getcwd()}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()