# TBG-Forums-Bot-Framework
A very basic bot framework for the TBG Forums

# Instructions
## 1. Set-Up
Download the files and place them in a new folder.\
Open config.json and fill out the info according to this guide:\
NAME: Change USERNAME to your bot's account username\
PASS: Change PASSWORD to your bot's account password\
FORUM_URL: It is recommended that this stays as the current tbgforums url (as the bot is built around the websites design) but if you wish to edit the code for another website, this can be changed to the website of your choice\
TOPIC_ID: Change XXXX to the topic ID of your choice (for the time being until I rework the code, it can only be one at a time)\
RESPONSE_THREAD_ID: Change to the same number as the TOPIC_ID variable (intended for future use, just ignore the fact that it is useless for now)\
LAST_POST_FILE: No point of changing this unless you desperately want to, but this also requires change to the main code.\
PREFIX: Change this to your bots prefix (e.g. xe! (for Xenon (Gaul Soodman) or nh! (for Nihonium (r.i.p.))))\

## 2. Functions Set Up
To create your own functions, edit main.py, under the definition "def generate_combined_response".\
There are examples laid out for you, try to follow the structure provided.\

## 3. Post details editing
Under "def post_response" change "subject" to "RE: Your Topic Name or whatever you want it to say"\

## 4. First time running
To run the code, it is recommended that you use Command Prompt or something similar to run main.py.\
Upon running main.py for the first time, a json file will be made to store the last scanned post id.\
The code will run its loop, wait 10 minutes before running again. If you want to automate this response using a cronjob or similar means, this loop may need to be edited.\


# Possible Questions
**Q:** My bot says it is posting, but the post isn't there, what do I do?\
**A:** Double check the username and password is correct, the bot may think that it is logged in, but it isn't, so it can't post but it can still parse the forums.\

**Q:** My bot is not finding any messages with the prefix even though they exist, what can I do?\
**A:** Check that the prefix is set correctly, and that the bot is parsing the right topic ID, it will only scan the one topic, so if posts are in a different topic, then they are not being parsed.\

## Any issues/suggestions/bugs, please contact me on discord. Username: phantomluigi
