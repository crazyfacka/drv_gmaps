DailyRoads Voyager Overlayer
=========

This application grabs the videos and subtitle files produced by the DailyRoads Voyager Android app (https://play.google.com/store/apps/details?id=com.dailyroads.v) and creates a map overlay, as well as some other little details, on top of the recorded video.

If you do not know what app I am talking about, you can read a bit more about it on the link above. In a nutshell, it's kind of an auto blackbox that records your daily driving.

As it is somewhat obvious, the author does not accept any liability for any loss regarding these services nor for burning down your house from the use of this tool. Use it (and improve it!) at your own risk.

Required tools
=========

- Python (tested with versions 2.7.x)
- ImageMagick (tested with version 6.6.9-7)
- FFmpeg (tested with version 2.4.2)

Please, for the love of all that is good and holy, **do not** use Ubuntu's repositories to install the *avconv* alternative. Get your FFmpeg, or build your own (like I did) here: https://www.ffmpeg.org/download.html

Notes
=========

There are two hardcoded values on the script, that have to be changed manually if intended. It can be found in line **186**. When I first created this, I used the OpenStreetMaps, but as the time of this writing the API has been unacessible. An alternative is easily introduced, though.

``` python
# Arg1: Show full path or not (If path shown, Google maps are used) | Arg2: OpenStreetMaps or not (Google is the alternative)
downloadMapPath(False, False)
```

There are some more parameters that can be tuned by looking at the source file. I tried to provide comments where fit. Apologies if it's not that clear.

Run
=========

To execute the application, simply run the script from the folder where all the videos and subtitle files are stored.

``` bash
$ python drv_gmaps.py
```

ToDo
=========

- Retrieve the parameters from the command line
- Do a probe of the video to set the correct dimensions for the overlay and final fps
