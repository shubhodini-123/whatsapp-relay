from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open WhatsApp Web
driver.get('https://web.whatsapp.com/')
wait = WebDriverWait(driver, 600)  # Wait for QR code scanning
driver.implicitly_wait(10)  # Implicit wait for 10 seconds
# Global variable to track the last processed message time
last_message_time = {"Sender": None, "Reciever": None}

# Function to clear the search bar
def clear_search_bar():
    try:
        search_bar = wait.until(
            ec.visibility_of_element_located((By.CLASS_NAME, "lexical-rich-text-input"))
        )
        search_input = search_bar.find_element(By.XPATH, './/div')
        search_input.click()
        search_input.send_keys(Keys.CONTROL + 'a')
        search_input.send_keys(Keys.BACKSPACE)
        print("Search bar cleared")
    except Exception as e:
        print(f"Error clearing the search bar: {e}")

# Function to dynamically search and open a group
def open_group(group_name):
    try:
        clear_search_bar()
        search_bar = wait.until(
            ec.visibility_of_element_located((By.CLASS_NAME, "lexical-rich-text-input"))
        )
        search_input = search_bar.find_element(By.XPATH, './/div')
        search_input.send_keys(group_name + Keys.ENTER)
        time.sleep(2)
        print(f"Opened chat with {group_name}, exiting open_group function with success")
    except Exception as e:
        print(f"Error locating group {group_name}: {e}")

# Function to detect and forward a new message
def detect_and_forward_message(from_group, to_group):
    global last_message_time
    while True:
        try:
            # Open the source group to check for new messages
            open_group(from_group)
            time.sleep(2)  # Allow the chat to load

            # Locate the last message's timestamp
            timestamp_elements = driver.find_elements(By.XPATH, '//span[contains(@class, "x1rg5ohu x16dsc37")]')
            if timestamp_elements:
                latest_time = timestamp_elements[-1].text  # Get the timestamp of the latest message

                # Check if the time is new (i.e., there is a new message)
                if latest_time != last_message_time[from_group]:
                    last_message_time[from_group] = latest_time  # Update the last processed time
                    print(f"New message detected in {from_group} at {latest_time}")
                    print("last_message_time", last_message_time)

                    # Locate the last message
                    message_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in focusable-list-item")]')
                    print("message_elements", message_elements)
                    last_message = message_elements[-1]
                    text_elements = last_message.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")]')
                    
                    # Check if the message is text
                    if text_elements:
                        message = text_elements[0].text
                        print(f"Text message detected: {message}")
                        clear_search_bar()  # Clear the search bar

                        # Open the destination group
                        search_bar = wait.until(
                            ec.visibility_of_element_located((By.CLASS_NAME , "lexical-rich-text-input"))
                        )
                        search_input = search_bar.find_element(By.XPATH, './/div')
                        search_input.click()
                        search_input.clear()
                        search_input.send_keys(to_group + Keys.ENTER)  # Search for the recipient group
                        time.sleep(5)
                        print(f"Chat opened")

                        # Locate the message input box
                        input_box = wait.until(
                            ec.visibility_of_element_located((By.XPATH, '(//div[contains(@class, "//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p")])[2]'))
                        )
                        input_field = input_box.find_element(By.XPATH, './/div')
                        input_field.click()
                        input_field.send_keys(message + Keys.ENTER)

                        print(f"Text message forwarded to {to_group}")

                    else:
                        print("Detected an image or document. Forwarding as usual...")
                        time.sleep(2)

                        # Update message_elements to get the latest message
                        message_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in focusable-list-item")]')
                        last_message = message_elements[-1]  # Get the latest message again

                        # Locate the forward button in the latest message
                        forward_button = last_message.find_element(By.XPATH, './/div[contains(@class, "x78zum5 x6s0dn4 xl56j7k xexx8yu x4uap5 x18d9i69 xkhd6sd x1f6kntn xk50ysn x7o08j2 xtvhhri x14yjl9h xudhj91 x18nykt9 xww2gxu x12s1jxh xkdsq27 xwwtwea xezl2tj xlrawln x1lnqpwl x1gnnqk1 xpk4wdd") and @role="button"]')
                        forward_button.click()
                        print(f"Forward button clicked")

                        time.sleep(2)

                        # Search for the recipient group
                        search_bar = wait.until(
                            ec.visibility_of_element_located((By.XPATH, '(//div[contains(@class, "//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div/p")])[1]'))
                        )
                        search_input = search_bar.find_element(By.XPATH, './/div')
                        search_input.click()
                        search_input.send_keys(to_group)
                        time.sleep(2)

                        # Select the group from the search results
                        group_element = wait.until(
                            ec.element_to_be_clickable((By.XPATH, f'//span[@title="{to_group}"]'))
                        )
                        group_element.click()
                        print(f"Selected group: {to_group}")

                        # Send the forwarded message
                        send_button = wait.until(
                            ec.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                        )
                        send_button.click()

                        print(f"Message forwarded from {from_group} to {to_group}")
                        time.sleep(2)
                    
                    # Re-open the original group to continue detecting messages
                    print(f"Re-opening chat with {from_group}...")
                    open_group(from_group)
                    time.sleep(5)

            else:
                print(f"No new message detected in {from_group}. Retrying...")
            time.sleep(5)  # Polling interval

        except Exception as e:
            print(f"Error forwarding message from {from_group} to {to_group}: {e}")


# Main execution
if __name__ == "__main__":
    try:
        detect_and_forward_message("Vishal Burrewar", "Khushal Gupta")  # Detect and forward a message from "Sender" to "Receiver"
    finally:
        driver.quit()
