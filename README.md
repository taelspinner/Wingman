# Wingman
A helper script for F-List that recommends you the best and most compatible profiles in an F-Chat channel.

Setup
=====

1. Put your login details in the ACCOUNT and PASSWORD variables.
2. Select a character to compare kink compatibility with and put their name in the CHARACTER variable.
3. Put the name of a public channel, or code of a private one, in the CHANNEL variable.
4. Put the names of all of your characters in the MY_CHARACTERS variable.

Use
===
* Run wingman.py to connect to the specified channel and receive a recommendation list compiled from the users therein.
* Specify the name of a profile to receive just the grade of that specific profile.

Configuration
=============
* SUGGESTIONS_TO_MAKE: How many profiles Wingman will attempt to recommend to you after grading.
* RANDOMIZE_SUGGESTIONS: If set to True, suggestions will be picked randomly above the cutoff, rather than showing the highest graded.
* QUALITY_CUTOFF: The minimum grade a profile must receive to be recommended to you.
* REJECT_ODD_GENDERS: With this enabled, only male and female profiles will be considered.
* GRADE_WEIGHTS: Total grade weights add up to 1. Alter them to place emphasis on other parts of a profile.
* BAD_SPECIES_LIST: The words in this list will incur a grading penalty if the profile's species contains them.
* AUTOFAIL_DESCRIPTION_LIST: Anything in this list found in a profile's description will result in the profile being discarded.

Dependencies
============

websockets, asyncio
