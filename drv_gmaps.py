import urllib2, shutil, math
from os import listdir, system, remove
from os.path import isfile, join
from time import sleep
from decimal import *

class Point:
    pass
        
points = []
lastAngle = 0.0
        
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def getAngle(p, c):
    global lastAngle
    c = c + 1
    if c >= len(points):
        return lastAngle
    while not isNumber(points[c].lat) and not isNumber(points[c].lon):
        c = c + 1
        if c >= len(points):
            return lastAngle
    np = points[c]
    try:
        ang = math.degrees( math.atan( (float(np.lat) - float(p.lat)) / (float(np.lon) - float(p.lon))) )
        if p.lon < np.lon:
            ang = ang + 180
    except:
        return lastAngle
    lastAngle = ang = float(Decimal(ang).quantize(Decimal(10) ** -2))
    return ang
    
def genTempArrow(angle):
    req = urllib2.Request("http://stuff.joagonca.com/files/arrow.php?angle=" + str(angle) + "&save_temp=1")
    rsp = urllib2.urlopen(req)

def getMapPicture(p, c):
    done = False
    while not done:
        req = urllib2.Request(p.url)
        try:
            rsp = urllib2.urlopen(req)
            pic = open("overlay_path_"+str(c)+".png", "w")
            pic.write(rsp.read())
            pic.close()
            done = True
        except urllib2.HTTPError as e:
            print "Server responded with the error", e.code
            print "URL:", p.url
            print "Sleeping for a couple of minutes..."
            sleep(120)
            print "Continuing..."
    
        
def parseFile(coord):
    print "Parsing file..."
    f = open(coord, 'r')
    p = Point()
    
    for line in f:
        # Change matching strings to your case
        if "km/h" in line:
            temp = line.split("   ")
            p.speed = temp[0]
            p.when = temp[1]
            p.altitude = temp[2].strip()
        elif "lat" in line:
            temp = line.split()
            p.lat = temp[1]
            p.lon = temp[3]
            points.append(p)
            p = Point()
            
    f.close()
            
def downloadMapPath(show_path, osm):
    if show_path or not osm:
        print "Downloading maps from Google"
    else:
        print "Downloading maps from OpenStreetMaps..."
        
    point_str = ""
    counter = 0
    url = ""
    
    if show_path:
        for a in range(0,len(points),2):
            point = points[a]
            if isNumber(point.lat) and isNumber(point.lon):
                point_str = point_str + point.lat + "," + point.lon + "|"
        point_str = "path=color:0x0000ff|weight:3|" + point_str[:-1]
        # Change map size to whichever size fits you best
        url = "http://maps.googleapis.com/maps/api/staticmap?size=400x400&sensor=false&" + point_str
        
    else:
        # Change map size to whichever size fits you best
        if osm:
            url = "http://pafciu17.dev.openstreetmap.org/?module=map&width=400&height=400&type=mapnik&zoom=15&pointImageUrl=http://stuff.joagonca.com/files/arrow_temp.png"
        else:
            url = "http://maps.googleapis.com/maps/api/staticmap?size=400x400&sensor=false"
            
    for point in points:
        if isNumber(point.lat) and isNumber(point.lon):
            ang = getAngle(point, counter)
            
            if show_path or not osm:
                marker = "&markers=icon:http://stuff.joagonca.com/files/arrow.php?angle="+str(ang)+"|shadow:false|" + point.lat + "," + point.lon
            else:
                genTempArrow(ang)
                marker = "&center=" + point.lon + "," + point.lat + "&points=" + point.lon + "," + point.lat
                
            url_marker = url + marker
            point.url = url_marker
            getMapPicture(point, counter)
                    
        else:
            if counter == 0:
                system("convert -size 400x400 xc:none overlay_path_"+str(counter)+".png")
            else:
                shutil.copyfile("overlay_path_"+str(counter-1)+".png", "overlay_path_"+str(counter)+".png")
                
        counter = counter + 1

def createOverlays():
    print "Creating image overlays..."
    counter = 0
    # Should be resolution of the video
    system("convert -size 1920x1080 xc:none bkg.png")
    for point in points:
        if isNumber(point.lat) and isNumber(point.lon):
            
            while system("composite -gravity NorthEast overlay_path_"+str(counter)+".png -dissolve 75x100 bkg.png main_overlay_"+str(counter)+".png") != 0:
                getMapPicture(point, counter)
                    
            system("convert main_overlay_"+str(counter)+".png -fill 'rgba(255,255,255,0.5)' -stroke black -strokewidth 2 -font Verdana-Negreta -pointsize 30 -gravity NorthWest -annotate 0 '"+point.speed+"\n"+point.when+"' main_overlay_"+str(counter)+".png")
            
        else:
            
            while system("composite -gravity NorthEast overlay_path_"+str(counter)+".png -dissolve 75x100 bkg.png main_overlay_"+str(counter)+".png") != 0:
                getMapPicture(point, counter)
                    
            system("convert main_overlay_"+str(counter)+".png -fill 'rgba(255,255,255,0.5)' -stroke black -strokewidth 2 -font Verdana-Negreta -pointsize 30 -gravity NorthWest -annotate 0 '-- km/h\n"+point.when+"' main_overlay_"+str(counter)+".png")
            
        counter = counter + 1
        
def createVideo(f, n):
    # Where is 'fps=fps=15', the number should be the fps of the source video
    system("./ffmpeg -i "+f[:-3]+"mp4 -r 1 -i main_overlay_%d.png -filter_complex '[1:0]fps=fps=15[a];[0:0][a]overlay=main_w-overlay_w:main_h-overlay_h' -c:v libx264 -preset veryfast -b:v 4000k -c:a copy finished_overlay_"+str(n)+".ts")
    remove("bkg.png")
    for a in range(len(points)):
        remove("overlay_path_"+str(a)+".png")
        remove("main_overlay_"+str(a)+".png")
        
def concatVideos(n):
    if n == 0:
        system("./ffmpeg -i finished_overlay_0.ts -c copy -bsf:a aac_adtstoasc finished_overlay.mp4")
        remove("finished_overlay_0.ts")
    else:
        cmd = "./ffmpeg -i 'concat:"
        for a in range(n):
            cmd = cmd + "finished_overlay_"+str(a)+".ts|"
        cmd = cmd[:-1] + "' -c copy finished_overlay_total.ts"
        system(cmd)
        for a in range(n):
            remove("finished_overlay_"+str(a)+".ts")
        system("./ffmpeg -i finished_overlay_total.ts -c copy -bsf:a aac_adtstoasc finished_overlay.mp4")
        remove("finished_overlay_total.ts")

files = [ f for f in listdir('.') if isfile(join('.',f)) ]
overlay_no = 0
for file in files:
    if file[-3:] == "srt":
        try:
            with open("finished_overlay_"+str(overlay_no)+".ts"):
                print "Overlay", str(overlay_no), "already produced!"
        except IOError:
            print "Going for video", str(overlay_no), ">", file[:-4]
            parseFile(file)
            # Arg1: Show full path or not (If path shown, Google maps are used) | Arg2: OpenStreetMaps or not (Google is the alternative)
            downloadMapPath(False, False)
            createOverlays()
            createVideo(file, overlay_no)
            points = []
            
        overlay_no = overlay_no + 1
        
concatVideos(overlay_no)
