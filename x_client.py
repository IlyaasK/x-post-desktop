import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

class XClient:
    def __init__(self):
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        access_token = os.getenv("ACCESS_TOKEN")
        access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Missing API keys in .env file")

        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # API v1.1 is still needed for media upload
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.api = tweepy.API(auth)

    def post_tweet(self, text, media_paths=None):
        """
        Post a tweet with optional media.
        
        Args:
            text (str): The text content of the tweet.
            media_paths (list): List of file paths to images/videos.
            
        Returns:
            Response: The response from the API.
        """
        media_ids = []
        if media_paths:
            for path in media_paths:
                # Use API v1.1 for media upload
                media = self.api.media_upload(filename=path)
                media_ids.append(media.media_id)

        response = self.client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
        return response
