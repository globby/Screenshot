#!/usr/bin/env python2
import re
import os
import sys
import time
import json
import argparse
import urllib
import urllib2

ID = "c01d446d57b2073"

UPLOADURL = "https://api.imgur.com/3/image"
IMGURL = "https://i.imgur.com/"

# HELP:
#-i --id       <id>                         Specify an imgur api id
#-d --delay    <seconds>                    Wait X seconds before taking shot
#-q --quiet                                 No output except link
#-c --clean                                 Delete screenshot after
#-f --filename <filename>                   Specify filename
#-h --help                                  Display help
#-v --verbose                               Display additional progress
#                                           information
#-l --clipboard                             Copy link to clipboard

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", help="Specify an imgur api id")
parser.add_argument(
    "-d",
    "--delay",
    type=int,
    help="Wait <delay> seconds before taking shot")
parser.add_argument(
    "-f",
    "--filename",
    help="Specify a filename (default is a timestamp)")
parser.add_argument(
    "-c",
    "--clean",
    action="store_true",
    help="Delete screenshot after upload (default false)")
parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="No output except the link")
parser.add_argument(
    "-s",
    "--select",
    action="store_true",
    help="Select a sub area of the screen")
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Display additional progress information")
parser.add_argument(
    "-l",
    "--clipboard",
    action="store_true",
    help="Copy imgur link to clipboard (requires xclip)")
args = parser.parse_args()


def printv(text):
    if args.verbose and not args.quiet:
        print "[v]\t" + text


def writev(text):
    if args.verbose:
        sys.stdout.write(text)
        sys.stdout.flush()


def prints(text):
    if not args.quiet:
        print "[+]\t" + text


def printe(text):
    print "[-]\t" + text
    sys.exit(-1)


def takeScreenshot():
    printv("Checking if scrot is installed...")
    if not os.path.isfile("/usr/bin/scrot"):
        printe("Error: scrot not installed (command scrot -v failed)")
    else:
        printv("Success: scrot is installed!")
        prints("Taking screenshot...")
        command = "scrot "
        if args.delay:
            d = args.delay
            while d:
                writev(str(d) + "... ")
                time.sleep(1)
                d -= 1
        if args.select:
            command += "-s "
        FILENAME = args.filename if args.filename else time.strftime(
            "%Y.%m.%d.%H.%M.%S.png",
            time.localtime())
        command += FILENAME
        resp = os.system(command)
        FILENAME = "%s/%s" % (os.getcwd(), FILENAME)
        if resp:
            printe("Error: Couldn't take screenshot!")
        else:
            if os.path.exists(FILENAME):
                with open(FILENAME, "rb") as f:
                    data = f.read()
                if args.clean:
                    printv("Deleting screenshot")
                    os.remove(FILENAME)
                return data
            else:
                printe(
                    "Error: The screenshot file seems to have dissapeared... \
                    what did you do???")


def uploadScreenshot(screenshot):
    if args.id:
        CID = args.id
    else:
        CID = ID
    prints("Starting image upload...")
    data = urllib.urlencode({"image": screenshot, "type": "file"})
    req = urllib2.Request(UPLOADURL, data)
    req.add_header('Authorization', 'Client-ID ' + CID)
    resp = urllib2.urlopen(req)

    # Haven't actually gotten here so not 100% sure it will work. If someone
    # gets to this point and it fails please leave a bug report on github
    if int(resp.info()["X-RateLimit-ClientRemaining"]) < 1:
        printe("You have run out of credits!")

    try:
        jdat = json.loads(resp.read())
        if "data" in jdat and "link" in jdat["data"]:
            prints("Successfully uploaded image!")
            if args.clipboard:
                printv("Checking if xclip is installed...")
                if os.path.isfile("/usr/bin/xclip"):
                    printv("Success: xclip is installed!")
                    os.system(
                        "echo %s | xclip -selection c" %
                        jdat["data"]["link"])
                    prints("The link has been copied to your clipboard")
                else:
                    printv("Error: xclip is not installed!")
                    printv("Printing link to console...")
                    print "Link: " + jdat["data"]["link"]
            else:
                print "Link: " + jdat["data"]["link"]
    except Exception as e:
        printv(str(e))
        printe("Error: Couldn't upload image")
if __name__ == "__main__":
    uploadScreenshot(takeScreenshot())
