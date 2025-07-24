import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

# ======= CONFIGURATION =======
EXCEL_PATH = "C:\\Users\\syed kaif\\Downloads\\accounts.xlsx"
REEL_PATH = "C:\\Users\\syed kaif\\Downloads\\reel2.mp4"  # Absolute path to the reel file
CAPTION = "Which is your favorite dress                                                     Let me know in the comments  #instagram #reels #female_collection #bodycon #india "  # Add your caption here
# =============================

def handle_popups(driver):
    """Handles Instagram popups after login with robust element detection."""
    print("Handling popups...")
    time.sleep(1)
    
    # Handle Save Info popup
    try:
        not_now_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(), 'Not now') and @role='button']")
            )
        )
        not_now_btn.click()
        print("Clicked 'Not now' for Save Info")
    except:
        print("No Save Info popup found")
    
    # # Handle Notification popup
    # try:
    #     not_now_btn = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable(
    #             (By.XPATH, "//button[contains(., 'Not Now')] | //div[text()='Not now']")
    #         )
    #     )
    #     not_now_btn.click()
    #     print("Clicked 'Not now' for Notifications")
    #     time.sleep(1)
    # except:
    #     print("No Notification popup found")

def click_create_button(driver):
    """Clicks the Create button using multiple robust strategies."""
    print("Locating Create button...")
    strategies = [
        {
            "name": "Header plus icon",
            "xpath": "//div[contains(@class, 'x1n2onr6')]//*[local-name()='svg' and @aria-label='New post']",
            "description": "Create button in header (plus icon)"
        },
        {
            "name": "Header Create text",
            "xpath": "//div[contains(text(), 'Create') and @role='button']",
            "description": "Create button in header by text"
        },
    ]

    for strategy in strategies:
        try:
            print(f"Trying strategy: {strategy['name']} ({strategy['description']})")
            
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, strategy["xpath"])))
            
            # Scroll into view if needed
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            # Use JavaScript click as fallback
            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)
            
            print(f"Success with {strategy['name']}")
            return True
                
        except Exception as e:
            print(f"Strategy {strategy['name']} failed: {str(e)}")
            continue
    
    print("All Create button strategies failed")
    return False

def set_aspect_ratio_to_original(driver):
    """Sets the reel aspect ratio to original using the crop button"""
    print("Setting aspect ratio to original...")
    try:
        # Click the crop button using the complex structure
        crop_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, '_aswp') and contains(@class, '_asx2') and .//*[local-name()='svg' and @aria-label='Select crop']]")
            )
        )
        driver.execute_script("arguments[0].click();", crop_button)
        print("Clicked crop button")
        time.sleep(1)
        
        # Select original aspect ratio
        original_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Original']/ancestor::div[@role='button']")
            )
        )
        driver.execute_script("arguments[0].click();", original_option)
        print("Aspect ratio set to original")
        return True
        
    except Exception as e:
        print(f"Couldn't set aspect ratio: {str(e)}")
        return False
    
def upload_reel(driver, reel_path):
    print("Starting upload process...")
    try:
        # Click the Create button
        if not click_create_button(driver):
            raise Exception("Could not find Create button")
        
        # Wait for the upload dialog to appear
        print("Waiting for upload dialog...")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@role='dialog']//button[.='Select from computer']")
            )
        )
        
        # Click "Select from computer" button
        # select_button = driver.find_element(
        #     By.XPATH, 
        #     "//div[@role='dialog']//button[.='Select from computer']"
        # )
        # select_button.click()
        print("Clicked 'Select from computer' button")
        time.sleep(1)
        
        print("Sending file path to hidden input...")
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@role='dialog']//input[@type='file']")
            )
        )
        file_input.send_keys(reel_path)
        print("File path sent successfully")
        
        # Wait for video processing to complete
        print("Waiting for video processing...")
        WebDriverWait(driver, 120).until(
            EC.invisibility_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Processing') or contains(text(), 'Converting')]")
            )
        )
        print("Video processing completed")
        
        try:
            print("Checking for confirmation popup...")

            # Wait for the heading that confirms the popup is present
            popup_header = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Video posts are now shared as reels')]"))
            )
            print("Popup detected")

            # Wait for and click the OK button
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='OK']"))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("Closed confirmation popup")

        except TimeoutException:
            print("No confirmation popup found or it did not load in time")
                

        
        # Set aspect ratio to original
        if not set_aspect_ratio_to_original(driver):
            print("⚠️ Continuing without setting aspect ratio")
        
        # Proceed through upload steps - REDUCED TO 1 OR 2 CLICKS
        print("Determining number of Next steps needed...")
        next_clicks = 0
        
        # First Next click (from crop screen)
        try:
            print("Clicking Next (1/2)...")
            next_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Next' and @role='button']")
                )
            )
            driver.execute_script("arguments[0].click();", next_btn)
            next_clicks += 1
            time.sleep(2)
        except Exception as e:
            print(f"First Next click failed: {str(e)}")
        
        # Second Next click (if available - from filters screen)
        try:
            print("Checking for second Next...")
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[text()='Next' and @role='button']")
                )
            )
            print("Clicking Next (2/2)...")
            driver.execute_script("arguments[0].click();", next_btn)
            next_clicks += 1
            time.sleep(2)
        except:
            print("No second Next button found")
        
        print(f"Completed {next_clicks} Next clicks")
        
        # Add caption - IMPROVED LOCATOR
        print("Adding caption...")
        try:
            caption_area = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@aria-label='Write a caption...' and @role='textbox']")
                )
            )
            # Clear existing text if any
            driver.execute_script("arguments[0].innerHTML = '';", caption_area)
            caption_area.send_keys(CAPTION)
            print("Caption added successfully")
             # Click outside the caption area to remove focus
             # We'll click on a neutral element - the preview area of the reel
            preview_area = driver.find_element(
                By.XPATH, 
                "//div[@role='presentation']//div[@class='x78zum5 x1iyjqo2']"
            )
            preview_area.click()
            print("Clicked outside caption area to remove focus")
        except Exception as e:
            print(f"Couldn't add caption: {str(e)}")
        
        # Final share button - enhanced handling (UPDATED)
        print("Clicking Share...")
        try:
            # First try with our standard locator
            share_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Share' and @role='button']"))
            )
            driver.execute_script("arguments[0].click();", share_btn)
        except:
            # Fallback to alternative locators
            print("Primary share button not found, trying alternatives...")
            share_strategies = [
                "//button[contains(., 'Share')]",
                "//div[text()='Share']",
                "//div[contains(@class, 'x1i10hfl') and contains(., 'Share')]"
            ]
            
            for strategy in share_strategies:
                try:
                    share_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, strategy)))
                    driver.execute_script("arguments[0].click();", share_btn)
                    print("Share button clicked with fallback strategy")
                    break
                except:
                    continue
            else:
                raise Exception("All share button strategies failed")
        
        # Handle final confirmation popup if it appears
        print("Checking for final confirmation popup...")
        try:
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='dialog']//div[text()='OK']")
                )
            )
            ok_button.click()
            print("Closed 'Videos are now Reels' popup")
        except TimeoutException:
            print("No final confirmation popup found")
        
        # Verify upload completion
        print("Verifying upload...")
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Your reel has been shared') or contains(text(), 'Your post has been shared')]")
            )
        )
        print("✅ Reel uploaded successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        # Take screenshot for debugging
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"upload_error_{timestamp}.png")
        print(f"Screenshot saved as upload_error_{timestamp}.png")
        return False

def login_and_upload(username, password, reel_path):
    """Handles full process for one account with enhanced reliability."""
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize WebDriver
        print("Initializing browser...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.set_page_load_timeout(60)
        
        # Login to Instagram
        print("Logging in...")
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Fill credentials
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        ).send_keys(username)
        
        driver.find_element(By.NAME, "password").send_keys(password)
        
        # Click login button
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        driver.execute_script("arguments[0].click();", login_btn)
        print("Login credentials submitted")
        
        # Handle popups
        handle_popups(driver)
        print("Reached home page")
        
        # Upload reel
        if upload_reel(driver, reel_path):
            print(f"✅ Successfully uploaded reel for {username}")
        else:
            print(f"❌ Upload failed for {username}")
        
        # Close browser
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Critical error for {username}: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return False

def main():
    # Read Excel data
    print("Reading accounts data...")
    df = pd.read_excel(EXCEL_PATH)
    
    # Process each account
    total = len(df)
    for index, row in df.iterrows():
        username = row['newusername']
        password = row['password']
        # username = 'laila_taania'
        # password = 'fullmoon@aliza'
        print(f"\n{'='*60}")
        print(f"Processing account {index+1}/{total}: {username}")
        print(f"{'='*60}")
        
        start_time = time.time()
        success = login_and_upload(username, password, REEL_PATH)
        elapsed = time.time() - start_time
        
        if success:
            print(f"✅ Completed in {elapsed:.1f} seconds")
        else:
            print(f"❌ Failed in {elapsed:.1f} seconds")
        
        # Pause between accounts
        print(f"Waiting before next account...")
        time.sleep(5)

if __name__ == "__main__":
    main()