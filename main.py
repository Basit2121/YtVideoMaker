import praw
import pyttsx3
from playwright.sync_api import playwright, sync_playwright
from moviepy.editor import *
import random
import os

# Connect to the Reddit API
reddit = praw.Reddit(client_id='yourclientid',
                     client_secret='yourclientsecret',
                     user_agent='yourusernmae')

# Get the top post from the AskMe subreddit for today
#AmItheAsshole offmychest unpopularopinion copypasta
subreddit = reddit.subreddit("offmychest")
for submission in subreddit.top(time_filter='day', limit=1):
    post_title = submission.title
    post_url = submission.url
    post = submission.title + "\n" + submission.selftext

    # Define the list of words to be censored
    words_to_censor = ['rape', 'sex', 'fuck', 'murder', 'porn']

    # Replace each word in the list with asterisks
    post = submission.title + "\n" + submission.selftext
    for word in words_to_censor:
        post = post.replace(word, '*' * len(word))

    # Take screenshot of the post
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge")
        context = browser.new_context()
        page = context.new_page()
        page.goto(post_url, timeout=60000)
        # Wait for the div to be loaded
        page.wait_for_selector(".uI_hDmU5GSiudtABRz_37", timeout=30000)
        # Get the bounding box of the div
        element_handle = page.query_selector(".uI_hDmU5GSiudtABRz_37")
        bounding_box = element_handle.bounding_box()
        # Take a screenshot of the div
        page.screenshot(path="post.png", clip=bounding_box)
        browser.close()
        print("The full screenshot has been saved as full_post.png")


    # Narrate the post using pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('voice', 'english-uk')
    engine.setProperty('rate', 150) 
    engine.setProperty('gender', 'male')
    engine.save_to_file(post, 'test.mp3')
    engine.runAndWait()

    # Load the video and audio files
    video = VideoFileClip("bgvideo.mp4")
    audio = AudioFileClip("test.mp3")

    original_audio = video.audio

    # Set the duration of the original audio to be the same as audio
    original_audio = original_audio.set_duration(audio.duration)

    # Combine the original and new audio clips
    combined_audio = CompositeAudioClip([original_audio, audio])

    # Calculate the total duration of the audio
    audio_duration = audio.duration

    # Generate a random start time for the video
    start_time = random.uniform(0, 200)
    print("Start Time is : ", start_time)

    # Cut the video to be 3 seconds longer than the audio, starting at the random start time
    video_duration = audio_duration + 0
    video = video.subclip(start_time, start_time + video_duration)

    # Overlay the custom image on the video
    image = ImageClip("post.png").set_pos(("center","center"))
    image = image.set_duration(audio_duration)

    # Combine the audio and video
    final_video = CompositeVideoClip([video, image])
    final_video = final_video.set_audio(combined_audio)

    video2=VideoFileClip("outro.mp4")

    # Concatenate the two videos together
    result = concatenate_videoclips([final_video, video2])

    # Write the final video to a file
    result.write_videofile("result.mp4")
    os.remove("post.png")
    os.remove("test.mp3")
