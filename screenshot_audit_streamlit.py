import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import tempfile
from io import BytesIO
import zipfile
import time

# --- Screenshot function ---
def take_screenshots(url, mode="fullpage", max_screens=None):
    # Use temporary folder to store screenshots
    output_folder = os.path.join(tempfile.gettempdir(), "screenshots")
    os.makedirs(output_folder, exist_ok=True)

    # Set up Selenium Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    driver.get(url)
    time.sleep(2)  # wait for page to load

    screenshots = []

    if mode == "fullpage":
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        file_path = os.path.join(output_folder, "screenshot_1.png")
        driver.save_screenshot(file_path)
        screenshots.append(file_path)
    else:  # split into 1080p sections
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        sections = (scroll_height // 1080) + 1
        for i in range(sections):
            driver.execute_script(f"window.scrollTo(0, {i*1080})")
            time.sleep(0.5)
            file_path = os.path.join(output_folder, f"screenshot_{i+1}.png")
            driver.save_screenshot(file_path)
            screenshots.append(file_path)
            if max_screens and i+1 >= max_screens:
                break

    driver.quit()
    return output_folder, screenshots

# --- ZIP creation function ---
def create_zip(folder):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)  # store only filenames
    zip_buffer.seek(0)
    return zip_buffer

# --- Streamlit App ---
st.title("Website Screenshot Audit Tool")

url = st.text_input("Enter website URL:")
mode = st.radio("Screenshot mode:", ["Full-page (single)", "Split into 1080p sections"])
max_screens = st.number_input("Max screenshots (leave 0 for all pages):", min_value=0, value=0)

if st.button("Run Screenshot Audit") and url:
    st.info("Running screenshot audit...")
    split_mode = "split" if mode.startswith("Split") else "fullpage"
    folder, screenshots = take_screenshots(url, mode=split_mode, max_screens=max_screens or None)
    st.success(f"Captured {len(screenshots)} screenshots!")

    # Create ZIP for download
    zip_file = create_zip(folder)
    st.download_button(
        label="Download all screenshots",
        data=zip_file,
        file_name="screenshots.zip",
        mime="application/zip"
    )

    # Optional: Show previews
    st.subheader("Preview screenshots:")
    for s in screenshots:
        st.image(s)
