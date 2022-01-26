# Cnnct4
A twitterbot for Connect 4

Uses Tweepy API and AWS-DynamoDB as the database for storing user IDs, game board, game status, and wins/losses. 


How to:
1. Download these files. 
2. Add auth.py file to project, containing all authentication codes necessary... template below, simply fill in values in single-quoted sections:

```
	# Twitter API
	consumer_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
	consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
	access_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
	access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
	bearer_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


	# DynamoDB
	ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
	SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
```

3. Manually retrieve the latest mention status ID for the bot's twitter account. 
	- This can be by using the Tweepy api.mentions_timeline() method in python and finding the ID of the first listed Item
	- OR just go to the latest mention for that Twitter account in the Twitter desktop app, and copy the list of numbers at the end of the URL. 

4. Paste that into the latest_mention_id.txt text file, replacing whatever text is on the first line. 

5. Run the following command to begin twitterbot: 
	python3 cnnct4.py

Enjoy!