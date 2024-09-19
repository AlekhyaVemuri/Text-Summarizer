## Description
A chrome plugin that uses Llama2 model to instantly summarize any webpage via link and any PDF upon upload.

## Pre-requisites
1. Create a conda environment
   	conda create -n llm python=3.11 libuv
2. Install the required dependencies
    pip install -r requirements.txt
3. Clone this repository & use 'Load unpacked extension' in Developer mode. Read more on [Development Basics](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked).

## Explore Sample
The directory structure is as follows:
1. backend -- contains code.py & server.py which processes text post fetching from Webpage/PDF & Flask related code respectively.
2. extension -- contains manifest.json for loading chrome extension & popup.html, popup.js & style.css for UI Interface purposes.

## Steps to run the Plugin

