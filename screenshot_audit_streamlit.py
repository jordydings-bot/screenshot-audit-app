import streamlit as st
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from PIL import Image
import time

# Streamlit app layout
st.title("Screenshot Audit App")

url = st.text_input("Enter the URL to take screenshots of:")
max_screens = st.number_input("Maximum number of screenshots", min_value=1, value=5)
output_folder = st.text_input("Folder name to save screenshots", value="outputs")

if st.button("Take Screenshots"):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Set up Selenium Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    screenshots = []

    try:
        driver.get(url)
        time.sleep(2)  # wait for page to load

        for i in range(1, max_screens + 1):
            screenshot_path = os.path.join(output_folder, f"screenshot_{i}.png")
            driver.save_screenshot(screenshot_path)
            screenshots.append(screenshot_path)
            st.image(Image.open(screenshot_path), caption=f"Screenshot {i}")

    finally:
        driver.quit()

    st.success(f"Saved {len(screenshots)} screenshots in '{output_folder}'")
