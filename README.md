# ScratchR2 Remake — A Scratch 2.0 Clone   

## Before we start:
  Before checking out this recreation check out [Heathercat123's ScratchR2 Recreation](http://codeberg.org/heathercat123/APIClone), it has been worked on for quite more time, nice to know I'm not the only one who is obsessed with Scratch 2.0. They actually have a few cool Scratch 2.0 related repositories that you can check out on [his GitHub profile](http://github.com/heathercat123/) or his [Codeberg profile](http://codeberg.org/heathercat123/).

## What is it?
This repository contains a full remake of the Scratch 2.0 backend, frontend, and Scratch.swf.
Using a decompiled version of the original SWF, I rebuilt the backend so you can experience Scratch 2.0 as it worked back in 2013.
You can load, create, and save projects, use the backpack, log in/out, like/unlike, favorite/unfavorite, and even check your messages—just like the real thing.
For the best experience, do not use Ruffle. It’s still early in development and Scratch 2.0 won’t run correctly under it.
Instead, use a Flash Player version without the kill‑switch and a compatible browser such as Pale Moon.

## Running the Server
Make sure you have Python 3 installed, then run:

### Windows
```
.\server.bat
```
    
    
### macOS / Linux
```
./server.sh
```


Once the server starts, open your browser and go to:    
```
http://127.0.0.1:8000
```  
Enjoy scratching like it’s 2013 again.