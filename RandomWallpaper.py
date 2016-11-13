#!/home/dan/anaconda3/bin/python
import praw
import requests
import os
import random
import datetime
import re


class WallpaperRetriever:
    # Reddit Preferences
    SUBREDDIT = "wallpapers"
    USER_AGENT = 'Wallpaper retriever v 0.1.1'
    ACCEPTABLE_TYPES = ['.jpg', '.jpeg', '.png']

    # OS Preferences
    DEFAULT_WALLPAPER_FOLDER = os.path.expanduser('~/Media/Pictures/Wallpapers')
    DEFAULT_CONFIG_FILE = os.path.expanduser('~/.config/pcmanfm/LXDE/desktop-items-0.conf')

    def __init__(self, num_to_choose=20):
        self.num_to_choose = num_to_choose

    def _establish_connection(self):
        self.connection = praw.Reddit(user_agent=self.USER_AGENT)

    # returns a generator of top submissions
    def _get_top_wallpaper_links(self):
        """get tj"""
        subs = self.connection.get_subreddit(self.SUBREDDIT).get_top(limit=self.num_to_choose)
        return [x.url for x in subs]

    @staticmethod
    def _download_picture(url, desired_path):
        """Attempt to download a url to the desired path"""
        response = requests.get(url=url,stream=True)
        with open(desired_path, 'wb') as f:
            f.write(response.content)

    def save_random_picture(self, folder=''):
        if not folder:
            folder = self.DEFAULT_WALLPAPER_FOLDER

        self._establish_connection()
        links = self._get_top_wallpaper_links()

        # get a good url
        random.shuffle(links)
        for link in links:
            tp = link[link.rfind('.'):]
            if tp in self.ACCEPTABLE_TYPES:
                break
        else:
            print("No Good URLS found")
            print(links)
            raise Exception("BadURLList")

        # get a good file name
        file_name = datetime.datetime.today().strftime('%Y%m%d')
        path = '{}/{}{}'.format(folder, file_name, tp)

        if os.path.isfile(path):
            i = 1
            while os.path.isfile('{}_{}{}'.format(path[:path.rfind('.')], i, tp)):
                i += 1
            path = '{}_{}{}'.format(path[:path.rfind('.')], i, tp)

        self._download_picture(link, path)

        return path

    # can also shell out to:
    # pcmanfm --set-wallpaper /point-to-new-wallpaper
    # lxsession-logout
    # but will have to wait for logout.
    # neet to find a way tp reactivate the
    # http://forums.debian.net/viewtopic.php?f=6&t=49672
    def change_wallpaper(self, new_wallpaper_path, config_file=''):
        if not config_file:
            config_file = self.DEFAULT_CONFIG_FILE

        with open(config_file, 'r') as f:
            config = f.read()

        try:
            line = re.search('wallpaper=.*\n', config).group(0)
        except AttributeError:
            print("Error - line not found.  Do you have the right config file?")
            print(config_file)
            print(config)

        old_file = line.replace('wallpaper=', '')
        new_line = 'wallpaper={}\n'.format(os.path.expanduser(new_wallpaper_path))
        config = config.replace(line, new_line)
        with open(config_file, 'w') as f:
            f.write(config)

        return old_file

if __name__ == '__main__':
    wp = WallpaperRetriever()
    wp.change_wallpaper(new_wallpaper_path=wp.save_random_picture())
