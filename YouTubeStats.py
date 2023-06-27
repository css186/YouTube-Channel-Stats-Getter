import requests
import json
from tqdm import tqdm


# create a class to store data
class YouTubeStats:

    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_stats = None
        self.video_stats = None

    def get_channel_statistics(self):
        """
        get basic statistical info about the channel(such as viewCount, subscriberCount...etc)
        :return: channel_data (statistics information in dictionary format)
        """
        try:
            # pass the channel id and api key into url address while instantiating
            url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}" \
                  f"&key={self.api_key}"

            # get the response by requesting api
            response = requests.get(url)

            # convert JSON response into python dict
            channel_json_dict = response.json()

            # parse channel statistics using slicing
            # viewCount, subscriberCount, videoCount...are located inside the nested dict with the key "statistics"
            channel_stats = channel_json_dict["items"][0]["statistics"]

        except (requests.RequestException, KeyError):
            channel_stats = None

        # store data to channel_stats attribute
        self.channel_stats = channel_stats

        return channel_stats

    def get_channel_videos(self):
        """
        1. get all the videos' ids inside the channel
        2. get all the stats of the videos like likeCounts, viewCounts, commentCounts...etc
        :return:
        """
        # 1. get all the videos (limit=50 is the maximum result YouTube allowed to give back per page)
        total_channel_videos = self._get_channel_videos(limit=50)  # total_channel_video is a dictionary

        # 2. get all the stats data by sending api calls to three parts of url(snippet, statistics, contentDetails)

        parts = ["snippet", "statistics", "contentDetails"]

        for video_id in tqdm(total_channel_videos):
            for part in parts:
                video_stats = self._get_single_video_data(video_id, part)
                total_channel_videos[video_id].update(video_stats)

        self.video_stats = total_channel_videos

        return total_channel_videos

    def _get_single_video_data(self, video_id, part):
        url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        response = requests.get(url)
        single_video_dict = response.json()
        try:
            details = single_video_dict['items'][0][part]

        except (requests.RequestException, KeyError):
            # have error, return empty dict
            details = dict()

        return details

    # helper method of get_channel_video
    # helper method is necessary since the api has pageToken that let us go through all the pages inside the channel
    def _get_channel_videos(self, limit):
        """
        :return: a dictionary with videoId as keys (videos from all the pages in the channel)
        """
        url = f"https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}" \
              f"&part=id&order=date"

        # if the value passed into "limit" is an int, then concatenate it onto the url to get more result of the video
        if limit is not None and isinstance(limit, int):
            url += "&maxResults=" + str(limit)

        # acquire the video_dict and pageToken from the first page
        total_videos_dict, next_page_token = self._get_page_info(url)

        # loop over the page to get more videos' data
        # add a counter to prevent continuous API calls since it is a while loop
        call_counter = 0
        while next_page_token is not None and call_counter < 10:
            next_url = url + "&pageToken=" + next_page_token

            # repeat the function to get the next page's info
            next_videos_dict, next_page_token = self._get_page_info(next_url)

            # add new videos to the video_dict from the first page
            total_videos_dict.update(next_videos_dict)
            call_counter += 1

        return total_videos_dict

    def _get_page_info(self, url):
        """
        :param: API url
        :return: parse pageToken & parse videoId into a dictionary format with videoId as key (Only one page!)
        """
        # create an empty dictionary for storing video data (videoId as key for further usage)
        video_dict = {}

        # get video information and page token per page when requesting
        # get api url
        response = requests.get(url)
        page_data_dict = response.json()

        # if at end of the page(no "items" key is found), return video_dict and pageToken(as None)
        if "items" not in page_data_dict:
            return video_dict, None

        # if "items" is found, continue
        # get videoId in list
        items_dict = page_data_dict["items"]

        # get pageToken(a key inside page_data_dict)
        # if pageToken is not found, return None
        next_page_token = page_data_dict.get("nextPageToken", None)

        for item in items_dict:
            try:
                # get only #video type of info
                if item["id"]["kind"] == "youtube#video":
                    video_id = item["id"]["videoId"]

                    # set videoId as a key in the video_dict
                    # value will be filled with statistics data afterward
                    video_dict[video_id] = {}

            except KeyError:
                print("Key Error")
                next_page_token = None

        return video_dict, next_page_token

    def dump_json(self):
        """
        dump channel statistics into a JSON file
        :return: None
        """
        # if self.channel_stats is None -> failed to request data
        if self.channel_stats is None or self.video_stats is None:
            print("Failed to Get Channel Statistics")

        # combine all the data receive
        file_content = {self.channel_id: {'channel_statistics': self.channel_stats, 'video_data': self.video_stats}}

        # pop any item from the video_stats to get the channel title
        # if we did not get the channelTitle, filled the name with channel_id instead
        channel_name = self.video_stats.popitem()[1].get("channelTitle", self.channel_id)

        # change channel name: replace space with underscore and convert into lower case
        channel_name.replace(" ", "_").lower()
        file_name = channel_name + ".json"

        # open and write file in order to save it
        try:
            with open(file_name, "w") as file:
                json.dump(file_content, file, indent=4)
                print("File Successfully Saved!")
        except EnvironmentError as error_message:
            print(f"Error Occurred: {error_message}")

    def get_details(self):
        """
        get details that can be commonly used for data analysis from self.video_stats
        :return: in dictionary format
        """
                
        ids = []
        dates = []
        titles = []
        views = []
        likes = []
        favorites = []
        comments = []
        durations = []
        tags_list = []
        
        info = 0
        
        if self.video_stats is not None:
            info = self.get_channel_videos()
            
        else:
            info = self.video_stats
        
        for key, value in info.items():
            ids.append(key)
            dates.append(value["publishedAt"])
            titles.append(value["title"])
            views.append(value["viewCount"])
            likes.append(value["likeCount"])
            favorites.append(value["favoriteCount"])
            comments.append(value["commentCount"])
            durations.append(value["duration"])
            if "tags" in value:
                tags_list.append(value["tags"])
            else:
                tags_list.append("No tags")

        details = {
            "video_id": ids,
            "published_date": dates,
            "title": titles,
            "view_count": views,
            "like_count": likes,
            "favorite_count": favorites,
            "comment_count": comments,
            "duration": durations,
            "tags": tags_list,
        }

        return details


