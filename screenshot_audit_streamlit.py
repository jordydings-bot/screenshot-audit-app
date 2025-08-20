# screenshot_audit_streamlit.py
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import zipfile
from io import BytesIO

st.title("Website Screenshot Audit")

# --- Inputs ---
url = st.text_input("Enter website URL")
mode = st.radio("Screenshot Mode", ("Full-page single", "HD 1080 sections"))
max_screens = st.number_input("Max screenshots (0 = all pages)", min_value=0, value=1, step=1)
output_folder = st.text_input("Folder to save screenshots (local path)", value="screenshots")

def take_screenshots(url, mode, max_screens, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    screenshots = []

    try:
        driver.get(url)
        time.sleep(2)  # wait for page to load
        total_height = driver.execute_script("return document.body.scrollHeight")

        if mode == "Full-page single":
            driver.set_window_size(1920, total_height)
            file_path = os.path.join(output_folder, "screenshot_full.png")
            driver.save_screenshot(file_path)
            screenshots.append(file_path)

        else:  # HD 1080 sections
            viewport_height = 1080
            num_screens = total_height // viewport_height + 1
            if max_screens > 0:
                num_screens = min(num_screens, max_screens)

            for i in range(num_screens):
                driver.execute_script(f"window.scrollTo(0, {i*viewport_height});")
                time.sleep(0.5)
                file_path = os.path.join(output_folder, f"screenshot_{i+1}.png")
                driver.save_screenshot(file_path)
                screenshots.append(file_path)

    finally:
        driver.quit()
    return screenshots

if st.button("Run Screenshot"):
    if not url:
        st.error("Please enter a website URL.")
    else:
        st.info("Starting screenshot process...")
        screenshots = take_screenshots(url, mode, max_screens, output_folder)
        st.success(f"Screenshots completed! {len(screenshots)} image(s) saved.")

        # Create ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file in screenshots:
                zipf.write(file, os.path.basename(file))
        zip_buffer.seek(0)

        st.download_button(
            label="Download All Screenshots as ZIP",
            data=zip_buffer,
            file_name="screenshots.zip",
            mime="application/zip"
        )

