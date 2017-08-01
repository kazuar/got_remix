# got_remix

Creating a remix of Sam from game of thrones cleaning the Citadel

[Sam Citadel](https://www.youtube.com/watch?v=azU3I1rwNv8)

More details can be found here: http://kazuar.github.io/got-remix/

Requirements
============

The python dependencies are managed using pip and listed in
`requirements.txt`

Setting up Local Development
============================

First, clone this repository:

    git clone https://github.com/kazuar/git_remix.git

You can use pip, virtualenv and virtualenvwrapper to install the requirements:

    pip install -r requirements.txt

* Make sure you have ffmpeg installed on your machine

Running the script
==================

python got_remix/got_remix.py --input-file resources/sam_citadel.mp4 --output-file resources/output.mp4 --output-duration 300
