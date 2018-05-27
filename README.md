# Wingman
A helper script for F-List that recommends you the best and most compatible profiles in an F-Chat channel.

Setup
=====
1. Open wingman.py in the text editor of your choice.
2. Put your login details in the ACCOUNT and PASSWORD variables.
3. Select a character to compare kink compatibility with and put their name in the CHARACTER variable.
4. Put the name of a public channel, or code of a private one, in the CHANNEL variable.

Use
===
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
