import asyncio
import random
import re
from pydantic import BaseModel

import selenium.webdriver.firefox.service
import uvicorn as uvicorn
from selenium import webdriver
from selenium.webdriver.common.by import By
import pytube
from fastapi import FastAPI



class Music(BaseModel):

    url:str = ""
    title:str = ""
    duration:str = ""
    author:str = ""
    thumbnail:str = ""

    def toJson(self):
        return {
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "author": self.author,
            "thumbnail": self.thumbnail
        }

    def __hash__(self):
        return hash((self.url, self.title, self.duration, self.author, self.thumbnail))

class Playlist:
    def __init__(self, url):
        self.url = url
        pytube_obj = pytube.Playlist(url)
        self.videos = []
        print("Playlist Hazırlanıyor...")

        for video in pytube_obj.videos:
            music = Music()
            music.url = video.watch_url
            music.title = video.title
            music.duration = video.length
            music.thumbnail = video.thumbnail_url
            music.author = video.author
            self.videos.append(music)

        random.shuffle(self.videos)


class Player:
    def __init__(self):
        print("Driver Başlatılıyor...")
        service_obj = selenium.webdriver.firefox.service.Service(executable_path="geckodriver.exe")
        self.driver = webdriver.Firefox(firefox_binary="C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                                        service=service_obj)

        self.driver.install_addon("./adblock_for_youtube-0.3.6.xpi", temporary=True)
        self.driver.implicitly_wait(10)

        self.playlist = Playlist("https://www.youtube.com/playlist?list=PL13pjv-f2BiIdAtxtYOTNOAfx359Mn2rN")
        self.played = []
        self.vote_list = {}
        print("Müzik Oynatılıyor...")


    async def play(self, music: Music):
        print("Müzik Oynatma Süreci Başlatılıyor...")
        self.driver.get(music.url)
        await self.declare_next_possible_songs()
        try:
            button = self.driver.find_element(By.CLASS_NAME, "ytp-large-play-button")
            button.click()
            await asyncio.sleep(int(music.duration))

        except:
            try:
                button = self.driver.find_element(By.CLASS_NAME, "ytp-large-play-button ytp-button")
                button.click()
                await asyncio.sleep(int(music.duration))
            except:
                pass



        self.driver.get("https://www.google.com")



        # add music to played list
        print("Sonraki Müzik Seçiliyor...")
        self.played.append(music)
        self.playlist.videos.remove(music)
        if len(self.playlist.videos) < 4:
            # add played songs to the playlist.videos
            self.playlist.videos.extend(self.played)
            # remove played songs from played list
            self.played = []
            # shuffle playlist.videos
            random.shuffle(self.playlist.videos)

        # select most voted music from self.vote_list
        most_voted_music = max(self.vote_list, key=self.vote_list.get)
        # play most voted music

        await self.play(most_voted_music)

    async def info(self):
        title = self.driver.find_element(By.CSS_SELECTOR,
                                         'h1.style-scope.ytd-watch-metadata yt-formatted-string.style-scope.ytd-watch-metadata')
        duration = self.driver.find_element(By.CLASS_NAME, "ytp-time-duration")
        thumbnail = self.driver.find_element(By.CLASS_NAME, "ytp-cued-thumbnail-overlay-image")

        music = Music()
        music.title = title.text
        music.duration = duration.text
        pattern = r'url\("([^"]+)"\)'
        match = re.search(pattern, thumbnail.get_attribute("style"))

        if match:
            url = match.group(1)
            music.thumbnail = url
        else:
            music.thumbnail = ""
        return music

    async def current_duration(self):
        current_duration = self.driver.find_element(By.CLASS_NAME, "ytp-time-current")
        return current_duration.text

    async def get_next_possible_songs(self):
        return self.vote_list

    async def declare_next_possible_songs(self):
        self.vote_list = {}
        next_songs = []
        # make a while loop, if next_songs lenght < 4 then continue for adding songs not played recently
        while len(next_songs) < 4:
            # take a random song from playlist
            random_song = random.choice(self.playlist.videos)
            # if random song is not in played list then add it to next_songs
            if random_song not in self.played:
                next_songs.append(random_song)
        # add next songs to vote list with 0 votes
        for song in next_songs:
            self.vote_list[song] = 0

    async def vote(self, url) -> str:
       #vote for matching url
        for song in self.vote_list:
            if song.url == url:
                self.vote_list[song] += 1
                return "SUCCESS : Your vote is added"

    # remove vote from song
    async def remove_vote(self, url) -> str:
        # vote for matching url
        for song in self.vote_list:
            if song.url == url:
                self.vote_list[song] -= 1
                return "SUCCESS : Your vote is removed"


app = FastAPI()
player = Player()
# run player.play() in background
asyncio.create_task(player.play(player.playlist.videos[0]))





@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/track/current")
async def current_track():
    music = await player.info()
    return music.toJson()


@app.get("/vote/song")
async def next_songs():
    next_songs = await player.get_next_possible_songs()
    #return next_songs keys  as json
    return [song.toJson() for song in next_songs.keys()]


@app.post("/vote/song")
async def vote(url: str):
    await player.vote(url)
    return "SUCCESS : Your vote is added"


@app.delete("/vote/song")
async def remove_vote(url: str):
    await player.remove_vote(url)
    return "SUCCESS : Your vote is removed"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)
