import streamlit as st
from playwright.sync_api import sync_playwright
from PIL import Image
import io, zipfile, math

st.title("Website Screenshot Audit")

url = st.text_input("Website URL")
mode = st.radio("Screenshot mode", ["Full page", "Split 1080p"])
max_screens = st.number_input("Max screenshots (0 for unlimited)", min_value=0, value=0)
run_button = st.button("Run Screenshot Audit")

if run_button and url:
    st.info("Running screenshot process...")

    screenshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        if mode == "Full page":
            img_bytes = page.screenshot(full_page=True)
            screenshots.append(("full_page.png", img_bytes))
        else:
            # Get total page height
            page_height = page.evaluate("document.body.scrollHeight")
            viewport_height = 1080
            num_screens = math.ceil(page_height / viewport_height)
            if max_screens > 0:
                num_screens = min(num_screens, max_screens)

            for i in range(num_screens):
                page.evaluate(f"window.scrollTo(0, {i * viewport_height})")
                st.text(f"Capturing section {i+1}/{num_screens}")
                img_bytes = page.screenshot(clip={"x":0, "y":i*viewport_height, "width":1920, "height":viewport_height})
                screenshots.append((f"section_{i+1}.png", img_bytes))
        
        browser.close()
    
    # Zip the screenshots for download
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a") as zf:
        for name, img_bytes in screenshots:
            zf.writestr(name, img_bytes)
    
    st.success(f"Captured {len(screenshots)} screenshot(s)!")
    st.download_button(
        label="Download all screenshots",
        data=zip_buffer.getvalue(),
        file_name="screenshots.zip",
        mime="application/zip"
    )
