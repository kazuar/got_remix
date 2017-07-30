
import sys
import math
import random
import librosa
import librosa.display
import matplotlib.pyplot as plt
from progressbar import ProgressBar
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate

FRAME_DURATION = 0.1
THRESHOLD = 0.02
FRAME_MIN_SIZE = 3
DURATION = 60

INPUT_FILE_PATH = "resources/short_got.mp4"
OUTPUT_FILE_PATH = "resources/got_remix.mp4"

def split_audio_to_frames(file_path):

    # Load the audio from the video file
    audio_data, sr = librosa.load(INPUT_FILE_PATH)

    # Calculate the frame len based on the FRAME_DURATION constant and sample rate
    frame_len = FRAME_DURATION * sr

    # Calculate the number of frames in the audio file
    num_of_frames = math.floor(len(audio_data) / frame_len)

    # Find silent frames
    silent_frames = []
    pbar = ProgressBar()
    for frame_num in pbar(range(int(num_of_frames))):
        start = int(frame_num * frame_len)
        stop = int((frame_num + 1) * frame_len)
        frame = map(abs, audio_data[start:stop])
        max_val = max(frame)
        if max_val < THRESHOLD:
            silent_frames.append(frame_num)

    aggregated_frames = [silent_frames[0]]
    for index, frame_num in enumerate(silent_frames[1:]):
        if frame_num - silent_frames[index] > FRAME_MIN_SIZE:
            aggregated_frames.append(frame_num)

    # Zip the frames together so we'll have a complete list of frames
    frames = zip(
        [int(frame*frame_len) for frame in aggregated_frames], 
        [int(frame*frame_len) - 1 for frame in aggregated_frames][1:]
    )
    # Check if we calculated frames until the end of the file.
    # If not, add another frame until the end of the file.
    if frames[-1][1] < len(audio_data):
       frames.append((frames[-1][1] + 1, len(audio_data))) 

    # Return a list of found frames, 
    # each list member is a tuple of (start_frame_index, end_frame_index)
    return frames, sr

def create_sub_clip(video_clip, frame, sr):
    start, stop = frame
    sub_clip = video_clip.subclip(start / float(sr), stop / float(sr))
    return sub_clip

def get_next_frame_for_video(frames, last_frames_in_video):
    frame = random.choice(frames[1:-1])
    while frame in last_frames_in_video:
        frame = random.choice(frames[1:-1])
    return frame

def create_video_mix(input_file, output_file, frames, sr, max_duration=DURATION):

    # Load the video
    video_clip = VideoFileClip(input_file)

    # Save the start and end sub clips and put random clips between them
    start_clip = create_sub_clip(video_clip, frames[0], sr)
    end_clip = create_sub_clip(video_clip, frames[-1], sr)
    video_duration = start_clip.duration + end_clip.duration
    frames_in_new_video = []

    # This list will hold the sub clips for the final video
    sub_clips = []

    # This loop will run until the new video duration is over max duration
    while True:
        # Select a random frame
        frame = get_next_frame_for_video(frames, frames_in_new_video[-3:])
        frames_in_new_video.append(frame)
        # Create a sub clip from the random frame
        sub_clip = create_sub_clip(video_clip, frame, sr)
        # Calculate the new video duration with this new sub clip
        video_duration += sub_clip.duration
        # If the new duration is longer than
        # the max duration, stop the loop
        if video_duration >= max_duration:
            break
        # Add the new random sub clip to our list of random sub clips
        sub_clips.append(sub_clip)

    # Create a list of the random clips and the start and end clips
    sub_clips = [start_clip] + sub_clips + [end_clip]

    # Concatenate all sub clips into 
    concat_clip = concatenate_videoclips(sub_clips, method="compose")

    # Output video to file
    concat_clip.write_videofile(output_file)

def plot_sound_wave(input_file, limits=[], v_lines_indexes = []):
    # Load the audio from the video file
    audio_data, sr = librosa.load(input_file)
    plt.plot(audio_data)
    # librosa.display.waveplot(audio_data)
    for limit in limits:
        plt.plot([limit] * len(audio_data))
    if v_lines_indexes:
        plt.vlines(v_lines_indexes, 0, audio_data.max(), color='k')
    plt.show()

def main():

    # Split the audio of the video file to frames
    frames, sr = split_audio_to_frames(INPUT_FILE_PATH)

    # Plot sound waves
    # plot_sound_wave(INPUT_FILE_PATH, [THRESHOLD, -1*THRESHOLD], [x[0] for x in frames] + [frames[-1][1]])

    # Create the video mix from the frames
    create_video_mix(INPUT_FILE_PATH, OUTPUT_FILE_PATH, frames, sr)

if __name__ == "__main__":
    sys.exit(main())
