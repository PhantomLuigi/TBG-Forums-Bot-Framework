import requests
import lxml.etree
import time
import json
import random
from datetime import datetime

# Global session for maintaining login
main_session = requests.Session()

import json

# Load config from file
with open('config.json', 'r') as f:
    config = json.load(f)

# Use the config variables
NAME = config['NAME']
PASS = config['PASS']
FORUM_URL = config['FORUM_URL']
TOPIC_ID = config['TOPIC_ID']
RESPONSE_THREAD_ID = config['RESPONSE_THREAD_ID']
LAST_POST_FILE = config['LAST_POST_FILE']
PREFIX = config['PREFIX']

# Function to log in
def login():
    global main_session
    obtain_login = main_session.get(FORUM_URL + "index.php?action=login")
    time.sleep(6)
    hidden_val = lxml.etree.HTML(obtain_login.text.encode()).xpath('//*[@id="frmLogin"]/input')
    form = {"user": NAME, "passwrd": PASS, "cookielength": 31536000}
    for v in hidden_val:
        form[v.get("name")] = v.get("value")
    login_req = main_session.post(FORUM_URL + "index.php?action=login2", data=form)
    time.sleep(6)
    return login_req.status_code == 200

# Load last processed msg ID
def load_last_msg_id():
    try:
        with open(LAST_POST_FILE, 'r') as file:
            data = json.load(file)
            return data.get("last_msg_id", 0)
    except FileNotFoundError:
        return 0
    
# Save last processed msg ID
def save_last_msg_id(msg_id):
    with open(LAST_POST_FILE, 'w') as file:
        json.dump({"last_msg_id": msg_id}, file)

def convert_date_to_timestamp(date_str):
    try:
        # Parse the date from format, e.g. "Mar 20, 2025, 11:29:50 AM"
        dt_object = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
        return int(time.mktime(dt_object.timetuple()))  # Convert to Unix timestamp
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return None  # Return None if there's an issue

# Scrapes Latest posts
def scrape_latest_posts(last_msg_id):
    global main_session
    responses = []
    page_number = 0
    last_seen_msg_ids = set()
    last_page_msg_ids = None

    while True:
        topic_url = f"{FORUM_URL}index.php?topic={TOPIC_ID}.{page_number}"
        print(f"Checking {topic_url}...")
        page = main_session.get(topic_url)
        time.sleep(6)
        tree = lxml.etree.HTML(page.text.encode())

        posts = tree.xpath('//div[contains(@class, "inner")]')
        if not posts:
            print(f"No posts found on {topic_url}, stopping.")
            break

        current_page_msg_ids = {int(post.get("data-msgid")) for post in posts if post.get("data-msgid")}
        if last_page_msg_ids == current_page_msg_ids:
            print("Detected duplicate final page. Stopping search.")
            break

        last_page_msg_ids = current_page_msg_ids

        for post in posts:
            msg_id_str = post.get("data-msgid")
            if not msg_id_str:
                continue
            try:
                msg_id = int(msg_id_str)
            except ValueError:
                print(f"Skipping invalid msg_id: {msg_id_str}")
                continue
            if msg_id <= last_msg_id or msg_id in last_seen_msg_ids:
                continue

            last_seen_msg_ids.add(msg_id)

            # Extract post text
            text = post.text.strip() if post.text else ""

            # Extract the date from the <a> tag
            date_element = post.xpath('../../..//a[@class="smalltext"]')
            if date_element:
                date_text = date_element[0].text.strip()
                unix_timestamp = convert_date_to_timestamp(date_text)
            else:
                unix_timestamp = None  # If no date is found

            if text.startswith(PREFIX):
                username_element = post.xpath('../../..//div[contains(@class, "poster")]//a')
                username = username_element[0].text.strip() if username_element else "Unknown"
                
                responses.append((msg_id, username, text, unix_timestamp))

        page_number += 25  

    return responses

def generate_combined_response(posts):
    response_content = ""
    latest_msg_id = 0
    
    for msg_id, username, text, timestamp in posts:
        command = text[3:].strip()  # Remove "xx!" prefix and strip spaces
        if timestamp is None:
            timestamp = int(time.time())  # Fallback to current time if parsing failed

        quote = f"[quote author={username} link=msg={msg_id} date={timestamp}]{text}[/quote]"
        response_text = ""

        # Handle "xx!" with no arguments
        if command == "":
            response_text = "Try posting xx!help for info on how to use My Commands."

        # Handle "xx!roll"
        elif command == "roll":
            num = random.randint(1, 6)
            response_text = f"You rolled a {num}!"

        # Handle "xx!rolladice x,y"
        elif command.startswith("rolladice"):
            parts = command.split(" ")
            if len(parts) < 2:
                response_text = "Invalid command format. Use: xx!rolladice x,y"
            else:
                try:
                    x, y = map(int, parts[1].split(","))
                    
                    # Edge case handling
                    if x <= 0:
                        response_text = "That is not possible."
                    elif x > 10000000000:
                        response_text = "Calm down buddy."
                    elif y < 1:
                        response_text = "You rolled no dice and got nothing."
                    elif y > 1000:
                        response_text = "{Insert large amount of text here}"
                    else:
                        rolls = [random.randint(1, x) for _ in range(y)]
                        response_text = "You rolled: " + ", ".join(map(str, rolls))
                
                except ValueError:
                    response_text = "Invalid numbers. Use: xx!rolladice x,y"

        # Handle "xx!coin"
        elif command == "coin":
            outcome = random.choices(
                ["It landed on heads", "It landed on tails", "It landed on its side... what the... how did you even do this?"],
                weights=[49999, 49999, 2],  # 49.999%, 49.999%, 0.002%
                k=1
            )[0]
            response_text = outcome

        # Handle "xx!help"
        elif command == "help":
            response_text = (
                "Available commands:\n"
                "- xx!roll: Rolls a standard 6-sided die.\n"
                "- xx!rolladice x,y: Rolls a die from 1 to x, y times.\n"
                "- xx!coin: Flips a coin (no easter egg here...).\n"
                "- xx!help: Shows this help message.\n"
                "- xx!: Shows a reminder to use xx!help."
            )

        else:
            response_text = "Unknown command. Try xx!help for a list of commands."

        # Append to response
        response_content += f"{quote}\n\n{response_text}\n\n"
        latest_msg_id = max(latest_msg_id, msg_id)

    return response_content.strip(), latest_msg_id

# Post a response
def post_response(content):
    global main_session
    obtain_post_page = main_session.get(FORUM_URL + f"index.php?action=post;topic={RESPONSE_THREAD_ID}")
    time.sleep(6)
    hidden_val = lxml.etree.HTML(obtain_post_page.text.encode()).xpath('//*[@id="postmodify"]/input')
    form = {
        "topic": RESPONSE_THREAD_ID,
        "check_timeout": 1,
        "subject": "Re: Example Text",
        "icon": "xx",
        "message": content,
        "message_mode": 0,
        "notify": 0,
        "goback": 1
    }
    for v in hidden_val:
        form[v.get("name")] = v.get("value")
    postin = main_session.post(FORUM_URL + f"index.php?action=post;topic={RESPONSE_THREAD_ID}", data=form)
    time.sleep(6)
    return postin.status_code == 200

# Main function
if login():
    while True:
        last_msg_id = load_last_msg_id()
        print(f"Checking for new posts in topic {TOPIC_ID}...")
        time.sleep(6)
        
        responses = scrape_latest_posts(last_msg_id)
        if responses:
            response_content, latest_msg_id = generate_combined_response(responses)
            if response_content:
                time.sleep(6)
                if post_response(response_content):
                    print(f"Posted combined response for messages up to {latest_msg_id}")
                    save_last_msg_id(latest_msg_id)
                else:
                    print("Failed to post response")
        
        print("Waiting 10 minutes before checking again...")
        time.sleep(600)  # Wait 10 minutes before checking again
