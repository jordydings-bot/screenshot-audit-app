import os
from io import BytesIO
from zipfile import ZipFile
from PIL import Image
import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess

# Ensure Playwright browsers are installed
subprocess.run(["playwright", "install"])

# --- Streamlit App ---
st.title("Website Screenshot Audit Tool")

url = st.text_input("Enter website URL:", "https://example.com")

split_mode = st.radio(
    "Screenshot mode:",
    ("Full Page (single image)", "Full HD Sections (multiple images)")
)

max_screens_option = st.radio(
    "Number of screenshots:",
    ("All pages", "Set max screenshots")
)

max_screens = None
if max_screens_option == "Set max screenshots":
    max_screens = st.number_input("Maximum number of screenshots:", min_value=1, value=5)

if st.button("Take Screenshots"):
    if not url:
        st.error("Please enter a valid URL")
    else:
        st.info("Starting browser, this may take a few seconds...")

        screenshots = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # Determine screenshot strategy
            if split_mode == "Full Page (single image)":
                screenshot = page.screenshot(full_page=True)
                screenshots.append(("screenshot_full.png", screenshot))
            else:
                # Split page into 1080p sections
                viewport_height = 1080
                page_height = page.evaluate("() => document.body.scrollHeight")
                num_screens = (page_height // viewport_height) + 1

                if max_screens:
                    num_screens = min(num_screens, max_screens)

                for i in range(num_screens):
                    page.evaluate(f"window.scrollTo(0, {i * viewport_height})")
                    st.info(f"Capturing section {i+1} / {num_screens}")
                    clip = {"x": 0, "y": i * viewport_height, "width": 1920, "height": viewport_height}
                    screenshot = page.screenshot(clip=clip)
                    screenshots.append((f"screenshot_{i+1}.png", screenshot))

            browser.close()

        st.success(f"Captured {len(screenshots)} screenshots!")

        # Create zip for download
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "a") as zip_file:
            for name, data in screenshots:
                zip_file.writestr(name, data)
        zip_buffer.seek(0)

        st.download_button(
            label="Download All Screenshots as ZIP",
            data=zip_buffer,
            file_name="screenshots.zip",
            mime="application/zip"
        )

        for name, data in screenshots:
            st.image(data, caption=name, use_column_width=True)
