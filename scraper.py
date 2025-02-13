import time
import os
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "job_scraper")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

def connect_db():
    """Connects to PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

def save_to_db(job_title, company, location, link):
    """Saves job data into PostgreSQL."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO jobs (title, company, location, link) VALUES (%s, %s, %s, %s) ON CONFLICT (link) DO NOTHING;",
            (job_title, company, location, link)
        )
        conn.commit()
    except Exception as e:
        print(f"Error inserting job: {e}")
    finally:
        cursor.close()
        conn.close()

def scrape_jobs(keyword, city):
    """Scrapes job listings from Stepstone.de."""
    driver = webdriver.Chrome()  # Use ChromeDriver
    driver.get("https://www.stepstone.de")

    time.sleep(3)  # Allow page to load

    # Accept cookies
    try:
        cookie_btn = driver.find_element(By.ID, "ccmgt_explicit_accept")
        cookie_btn.click()
        time.sleep(2)
    except:
        pass  # If no cookie popup, continue

    # Enter job title
    search_box = driver.find_element(By.NAME, "ke")
    search_box.send_keys(keyword)

    # Enter city
    location_box = driver.find_element(By.NAME, "ss")
    location_box.send_keys(Keys.CONTROL + "a")  # Select existing text
    location_box.send_keys(Keys.DELETE)  # Clear it
    location_box.send_keys(city)

    # Submit search
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)  # Allow results to load

    jobs = driver.find_elements(By.CSS_SELECTOR, ".sc-1k8d6zk-0")

    for job in jobs:
        try:
            title = job.find_element(By.CSS_SELECTOR, "h2").text
            company = job.find_element(By.CSS_SELECTOR, ".sc-1pe7b5t-2").text
            location = job.find_element(By.CSS_SELECTOR, ".sc-1pe7b5t-3").text
            link = job.find_element(By.TAG_NAME, "a").get_attribute("href")

            print(f"Saving job: {title} | {company} | {location}")
            save_to_db(title, company, location, link)

        except Exception as e:
            print(f"Error scraping job: {e}")

    driver.quit()

print("Scraped jobs:", scrape_jobs)  # Debugging output


if __name__ == "__main__":
    keyword = input("Enter job title: ")
    city = input("Enter city: ")
    scrape_jobs(keyword, city)