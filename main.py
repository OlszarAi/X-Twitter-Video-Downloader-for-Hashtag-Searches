import tweepy
import os
import argparse
import yt_dlp
from datetime import datetime

def setup_twitter_api(bearer_token):
    """Set up and return the X/Twitter API client using bearer token."""
    return tweepy.Client(bearer_token=bearer_token)

def search_videos_by_hashtags(api, hashtags, min_likes):
    """Search for tweets with specified hashtags that contain videos."""
    # Construct search query for all hashtags
    query = " OR ".join([f"#{tag.strip('#')}" for tag in hashtags])
    query += " has:videos -is:retweet" # Only get original tweets with videos
    
    print(f"Searching for tweets with query: {query}")
    
    # Search for tweets
    response = api.search_recent_tweets(
        query=query,
        tweet_fields=['id', 'text', 'created_at', 'author_id', 'public_metrics'],
        expansions=['author_id', 'attachments.media_keys'],
        media_fields=['type', 'preview_image_url', 'url'],
        max_results=100
    )
    
    matching_tweets = []
    
    # Return empty list if no data
    if not response.data:
        return matching_tweets
    
    # Get users for easy reference
    users = {user.id: user.username for user in response.includes.get('users', [])}
    
    # Process each tweet
    for tweet in response.data:
        # Check like count
        like_count = tweet.public_metrics.get('like_count', 0)
        if like_count >= min_likes:
            # Check if this tweet has media attachments
            if hasattr(tweet, 'attachments') and 'media_keys' in tweet.attachments:
                username = users.get(tweet.author_id, "unknown")
                tweet_id = tweet.id
                
                matching_tweets.append({
                    'id': tweet_id,
                    'url': f"https://twitter.com/{username}/status/{tweet_id}",
                    'author': username,
                    'likes': like_count,
                    'created_at': tweet.created_at,
                    'text': tweet.text[:50] + "..." if len(tweet.text) > 50 else tweet.text
                })
    
    return matching_tweets

def download_tweets_with_videos(tweets, min_views, download_dir):
    """Download videos from tweets if they meet the view count requirement."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    downloaded_count = 0
    
    for tweet in tweets:
        try:
            # Format timestamp for filename
            timestamp = tweet['created_at'].strftime('%Y%m%d')
            
            # First extract information without downloading
            ydl_opts = {
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(tweet['url'], download=False)
                view_count = info_dict.get('view_count', 0)
                
                if view_count >= min_views:
                    print(f"\nDownloading video from {tweet['url']}")
                    print(f"- Author: {tweet['author']}")
                    print(f"- Likes: {tweet['likes']}, Views: {view_count}")
                    
                    # Set output filename with metadata
                    output_template = os.path.join(
                        download_dir, 
                        f"{tweet['author']}_{timestamp}_likes{tweet['likes']}_views{view_count}.%(ext)s"
                    )
                    
                    # Download options
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_template,
                        'quiet': False,
                    }
                    
                    # Download the video
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                        ydl_download.download([tweet['url']])
                    
                    downloaded_count += 1
                    print(f"✓ Download complete!")
                else:
                    print(f"Skipping {tweet['url']} - Not enough views (has {view_count}, needed {min_views})")
        
        except Exception as e:
            print(f"Error downloading {tweet['url']}: {str(e)}")
    
    return downloaded_count

def main():
    parser = argparse.ArgumentParser(description='Download X/Twitter videos by hashtags with engagement filters')
    parser.add_argument('--token', required=True, help='Bearer token for Twitter API')
    parser.add_argument('--hashtags', default='debata,debata prezydencka', 
                        help='Comma-separated list of hashtags to search for (without #)')
    parser.add_argument('--min-likes', type=int, default=10, help='Minimum number of likes')
    parser.add_argument('--min-views', type=int, default=100, help='Minimum number of views')
    parser.add_argument('--output', default='./downloaded_videos', help='Output directory for videos')
    
    args = parser.parse_args()
    
    # Set up the API client
    print("Authenticating with X/Twitter API...")
    api = setup_twitter_api(args.token)
    
    # Parse hashtags
    hashtags = [tag.strip() for tag in args.hashtags.split(',')]
    print(f"Will search for hashtags: {', '.join(['#' + tag for tag in hashtags])}")
    
    # Search for tweets with videos
    print("\nSearching for tweets with videos...")
    tweets = search_videos_by_hashtags(api, hashtags, args.min_likes)
    
    if not tweets:
        print("No tweets found matching the criteria.")
        return
    
    print(f"\nFound {len(tweets)} tweets with videos and at least {args.min_likes} likes.")
    print(f"Will now download videos with at least {args.min_views} views to {args.output}")
    
    # Download videos
    downloaded = download_tweets_with_videos(tweets, args.min_views, args.output)
    
    print(f"\nDownload summary:")
    print(f"- Total tweets found: {len(tweets)}")
    print(f"- Videos downloaded: {downloaded}")
    print(f"- Videos skipped: {len(tweets) - downloaded}")
    
    if downloaded > 0:
        print(f"\nVideos saved to: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()