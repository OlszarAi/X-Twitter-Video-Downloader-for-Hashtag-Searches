# Twitter Video Downloader

A tool for searching and downloading Twitter videos based on hashtags and engagement metrics.

## Description

This program allows you to search for tweets containing videos with specific hashtags, filter them by minimum likes and views, and automatically download the qualifying videos.

## Prerequisites

Before running the program, you need to install the required dependencies:

```bash
pip install tweepy yt-dlp
```

## Twitter API Access

To use this program, you need a Twitter API Bearer Token:

1. Register as a developer at [developer.twitter.com](https://developer.twitter.com)
2. Create a project and app to get your Bearer Token

## Usage

Run the program using the following command:

```bash
python main.py --token YOUR_BEARER_TOKEN --hashtags debata,debata_prezydencka --min-likes 50 --min-views 1000
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--token` | Your X/Twitter API Bearer Token | **Required** |
| `--hashtags` | Comma-separated list of hashtags to search | "debata,debata prezydencka" |
| `--min-likes` | Minimum number of likes for a video | 10 |
| `--min-views` | Minimum number of views for a video | 100 |
| `--output` | Directory to save downloaded videos | "./downloaded_videos" |

## How It Works

The program will:
1. Search for recent tweets containing videos with the specified hashtags
2. Check if they meet the minimum like and view count requirements
3. Download the qualifying videos to the specified output directory
