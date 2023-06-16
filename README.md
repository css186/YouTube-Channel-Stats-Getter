# YouTube-Channel-Stats-Getter
A tool that can be imported in order to get data from YouTube channels for analysis or store the data in a JSON file

# How to Use it?
- For data analysis purposes:
  1. import this file into jupyter notebook or jupyter lab using `from YouTubeStats import YouTubeStats`.
  2. pass in your own "YouTube Data API v3" API key and the YouTube channel ID you like to analyze as arguments and instantiate object using `yt = YouTubeStats(api_key, channel_id)`.
  3. use `get_channel_statistics()` method to get the overall stats of the channel.
  4. use `get_channel_video()` method to get the unedited raw data from every videos in the channel.
  5. use `get_details()` method to get edited data which can be put into pd.DataFrame() as an argument directly.

- For data storage purposes:
  use `dump_json()` method to get the details of every videos in JSON file. (Can be stored into databases such as MongoDB etc.)
