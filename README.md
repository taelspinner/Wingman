# Wingman
A helper script for F-List that recommends you the best and most compatible profiles in an F-Chat channel. It separates the wheat from the chaff with minimal effort on your part.

# BIG DISCLAIMER: This script hasn't been optimized in a long time and it uses a lot of API calls. If you use it the mods might get mad at you. If you want me to turn it into anything usable and efficient you'll have to yell at me.

Download
========
Click the green "Clone or download" button on the top right, and then click "Download ZIP."

Setup
=====
1. Open wingman.py in the text editor of your choice.
2. Put your login details in the ACCOUNT and PASSWORD variables.
3. Select a character to compare kink compatibility with and put their name in the CHARACTER variable.
4. Put the names of public channels, or codes of private ones, in the CHANNELS list variable (like so: ["Sex Driven LFRP", "adh-f051bba3c0104d2954c9"]).

Use
===
* You'll need to install Python from https://www.python.org/downloads/release/python-372/ if you don't already have it.
* Make sure you have the script's dependencies installed (listed below). You can use PIP to install them. Learn how to install packages at https://packaging.python.org/tutorials/installing-packages/.
* Use the Command Prompt to run wingman.py for the best experience.
* Run wingman.py to connect to the specified channel and receive a recommendation list compiled from the users therein. You will be logged out when the script starts if you're on that character, but can log in while grading is being done safely.
* Specify the name of a profile to receive just the grade of that specific profile.
* After the first time you run the script, a blacklist.txt file will be created in the folder. Put names of profiles in there to not have them recommended to you anymore.

Configuration
=============
* SUGGESTIONS_TO_MAKE: How many profiles Wingman will attempt to recommend to you after grading.
* RANDOMIZE_SUGGESTIONS: If set to True, suggestions will be picked randomly above the cutoff, rather than showing the highest graded.
* QUALITY_CUTOFF: The minimum grade a profile must receive to be recommended to you.
* REJECT_ODD_GENDERS: With this enabled, only male and female profiles will be considered.
* GRADE_WEIGHTS: Total grade weights add up to 1. Alter them to place emphasis on other parts of a profile.
* BAD_SPECIES_LIST: The words in this list will incur a grading penalty if the profile's species contains them.
* GOOD_SPECIES_LIST: The words in this list will give extra credit if the profile's species contains them.
* AUTOFAIL_DESCRIPTION_LIST: Anything in this list found in a profile's description will result in the profile being discarded.
* DISALLOWED_COCK_SHAPES: If specified, any profile that has a cock shape in this list will be discarded.
* STRICT_MATCHING: If enabled, you will only be shown profiles that definitely fit your tastes (for instance, submissives will only be shown dominants, not switches).

Dependencies
============

requests, websockets
