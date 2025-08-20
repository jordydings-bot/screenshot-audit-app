import os
import time
import zipfile
from urllib.parse import urlparse

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Streamlit UI ---
st.set_page_config(page_title="Website Screenshot Tool", layout="wide")
st.title("Website Screenshot Tool")

url = st.text_input("Website URL (include https://)", "https://example.com")
max_pages = st.number_input("Max pages (0 = all pages)", min_value=0, value=0)
screenshot_option = st.radio(
    "Screenshot Option",
    ("Full Page Single Screenshot", "Split into Full HD Sections", "Viewport Only")
)
output_folder = st.text_input("Output folder", "screenshots")

if st.button("Run Screenshot"):
    if not url.startswith("http"):
        st.error("Please enter a valid URL including https://")
    else:
        os.makedirs(output_folder, exist_ok=True)
        st.info("Starting screenshot process...")

        # --- Selenium setup ---
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=driver_options)
        driver.set_window_size(1920, 1080)

        visited = set()
        to_visit = [url]
        count = 0

        # --- Streamlit progress ---
        progress_text = st.empty()
        progress_bar = st.progress(0)

        while to_visit:
            if max_pages != 0 and count >= max_pages:
                break

            page_url = to_visit.pop(0)
            if page_url in visited:
                continue
            visited.add(page_url)

            try:
                driver.get(page_url)
                time.sleep(2)
                safe_name = urlparse(page_url).path.replace("/", "_") or "home"
                base_file_path = os.path.join(output_folder, f"{count:03d}_{safe_name}.png")

                if screenshot_option == "Full Page Single Screenshot":
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    driver.set_window_size(1920, total_height)
                    driver.save_screenshot(base_file_path)

                elif screenshot_option == "Split into Full HD Sections":
                    viewport_height = 1080
                    scroll_height = driver.execute_script("return document.body.scrollHeight")
                    num_sections = (scroll_height // viewport_height) + 1
                    for i in range(num_sections):
                        driver.execute_script(f"window.scrollTo(0, {i * viewport_height});")
                        time.sleep(1)
                        part_file = base_file_path.replace(".png", f"_part{i+1}.png")
                        driver.save_screenshot(part_file)

                else:  # Viewport only
                    driver.save_screenshot(base_file_path)

                count += 1

                # Update Streamlit progress
                progress_text.text(f"Captured ({count} pages): {page_url}")
                if max_pages != 0:
                    progress_bar.progress(min(count / max_pages, 1.0))
                else:
                    progress_bar.progress(min(count / (len(to_visit) + count), 1.0))

                # Add internal links
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href and url in href and href not in visited and href not in to_visit:
                        to_visit.append(href)

            except Exception as e:
                st.error(f"Error visiting {page_url}: {e}")

        driver.quit()

        # --- ZIP all screenshots ---
        zip_filename = os.path.join(output_folder, "screenshots.zip")
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for root, _, files in os.walk(output_folder):
                for f in files:
                    if f.endswith(".png"):
                        zipf.write(os.path.join(root, f), f)

        st.success(f"Done! Screenshots saved in folder: {output_folder}")
        st.download_button("Download All Screenshots as ZIP", zip_filename)
