
import sys
import math
import random
import librosa
import librosa.display
import argparse
import got_remix_utils
import matplotlib.pyplot as plt
from progressbar import ProgressBar
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate

FRAME_DURATION = 0.1
THRESHOLD = 0.02
FRAME_MIN_SIZE = 3
DURATION = 300


def split_audio_to_frames(file_path):

    # Load the audio from the video file
    audio_data, sr = librosa.load(file_path)

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

    # Aggregate consecutive frames and for each one save the local minimum in the frame
    aggregated_frames = [(silent_frames[0], 0)]
    for index, frame_num in enumerate(silent_frames[1:]):
        if frame_num - silent_frames[index] > FRAME_MIN_SIZE:
            start = int(frame_num * frame_len)
            stop = int((frame_num * frame_len) + 0.3 * sr)
            frame = map(abs, audio_data[start:stop])
            min_val_index = frame.index(min(frame)) + (frame_num * frame_len)
            aggregated_frames.append((frame_num, min_val_index))

    # Zip the frames together so we'll have a complete list of frames
    frames = zip(
        [frame[1] for frame in aggregated_frames], 
        [frame[1] - 1 for frame in aggregated_frames][1:]
    )
    
    # Check if we calculated frames until the end of the file.
    # If not, add another frame until the end of the file.
    if frames[-1][1] < len(audio_data):
        frames[-1] = (frames[-1][0], len(audio_data))

    # Return a list of found frames 
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

def main():

    # Get arguments
    parser = argparse.ArgumentParser(description='Create a video mix of Sam working in the Citadel, Game of Thrones - Season 7 Episode 1)')
    parser.add_argument('--input-file', help='The video input file', required=True)
    parser.add_argument('--output-file', help='The video output file', required=True)
    parser.add_argument('--output-duration', help='Duration, in seconds, of the final video', 
        type=int, default=DURATION, required=False)

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    duration = args.output_duration

    print("Creating video mix from {0} and outputing it to {1} with duration of {2}".format(
        input_file, output_file, duration))

    # Split the audio of the video file to frames
    frames, sr = split_audio_to_frames(input_file)

    # Create the video mix from the frames
    create_video_mix(input_file, output_file, frames, sr, duration)

if __name__ == "__main__":
    sys.exit(main())
