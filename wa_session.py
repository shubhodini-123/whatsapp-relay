from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os


def generate_session_file():
    # Set up WebDriver
    option = webdriver.ChromeOptions()
    option.add_argument(r"user-data-dir=C:\Users\Dell\AppData\Local\Google\Chrome\User Data")
    
    driver = webdriver.Chrome(options=option)
    driver.get("https://web.whatsapp.com/")
    
    # Wait for QR code scan
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".qr-code")))
    
    # Get session data
    script = """
        var request = indexedDB.open('wawc');
        return new Promise((resolve, reject) => {
            request.onerror = () => reject();
            request.onsuccess = () => resolve(request.result);
        });
    """
    db = json.loads(driver.execute_script(script))
    
    # Extract key-value pairs
    session = {}
    for item in db.transaction('user').objectStore('user').getAllKeys():
        value = db.transaction('user').objectStore('user').get(item)
        session[item] = value
    
    # Save session to file
    with open("session.wa", "w") as f:
        json.dump(session, f)
    
    driver.quit()

def open_with_session(session_file_path):
    if not os.path.exists(session_file_path):
        raise IOError(f'"{session_file_path}" does not exist.')
    
    with open(session_file_path, "r") as f:
        session = json.load(f)
    
    # Set up WebDriver
    option = webdriver.ChromeOptions()
    option.add_argument(r"user-data-dir=C:\Users\Dell\AppData\Local\Google\Chrome\User Data")
    
    driver = webdriver.Chrome(options=option)
    driver.get("https://web.whatsapp.com/")
    
    # Inject session
    script = """
        var db = indexedDB.open('wawc');
        db.onerror = function() {};
        db.onsuccess = function(event) {
            var transaction = event.target.result.transaction(['user'], 'readwrite');
            var objectStore = transaction.objectStore('user');
            for(var key in {}) {
                objectStore.put({}, key);
            }
        };
    """
    driver.execute_script(script, session)
    
    # Refresh page to apply changes
    driver.refresh()
    
    # Wait for WhatsApp web to load
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".main")))
    
    print("WhatsApp web opened successfully.")
    input("Press Enter to close...")
    driver.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "generate":
            generate_session_file()
        elif sys.argv[1].lower() == "open":
            open_with_session(sys.argv[1])
    else:
        print("Usage:")
        print("python script.py generate [session_file_path]")
        print("python script.py open [session_file_path]")