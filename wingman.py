import requests
import json, re
import xml.etree.ElementTree as ET
from collections import defaultdict
import sys, getopt
import websockets, asyncio
from random import shuffle

#Program settings
USERNAME = ""
PASSWORD = ""
CHARACTER = ""
CHANNEL = ""
HOST = "chat.f-list.net"
PORT = 9722
SERVICE_NAME = "Wingman"
SERVICE_VERSION = 1.1
MY_CHARACTERS = []
SUGGESTIONS_TO_MAKE = 10
RANDOMIZE_SUGGESTIONS = False
REJECT_ODD_GENDERS = True
QUALITY_CUTOFF = 80

#Character grading settings
GRADE_WEIGHTS = {'profile play' : 0.01,
                 'bad species' : 0.04,
                 'bbcode abuse' : 0.05,
                 'punctuation' : 0.05,
                 'name punctuation' : 0.05,
                 'no images' : 0.1,
                 'literacy' : 0.125,
                 'custom kinks' : 0.125,
                 'description length' : 0.15,
                 'kink matching' : 0.3
                 }
BAD_SPECIES_LIST = ['Human', 'Homo Sapiens', 'Angel', 'Pony', 'Sergal']
AUTOFAIL_DESCRIPTION_LIST = ['everypony', 'murr', 'yiff', 'latex', ' owo ', ' uwu ', ' ._. ', ' >.< ', ' :3 ', ' >:3 ', 'Ponyville']
BBCODE_TAG_LIST = {'[b]' : 4,
                   '[big]' : 2,
                   '[indent]' : 4,
                   '[collapse=' : 4,
                   '[color=' : 8
                   }
EXPECTED_NUMBER_CUSTOM_KINKS = 5
EXPECTED_MAXIMUM_CUSTOM_KINKS = 100
EXPECTED_DESCRIPTION_LENGTH = 2500
EXPECTED_MATCHING_KINKS = 50
LINEBREAK_PER_CHARACTERS = 150
SPELLING_ERROR_PER_CHARACTERS = 2500
UNDERKINKING_BONUS_FLOOR = 5
OVERKINKING_PENALTY_FLOOR = 200
OVERKINKING_MODIFIER = 5
MAX_EXTRA_CREDIT = 1.2
PICTURE_IS_WORTH = 1000

#Caches
TICKET = None
INFO_LIST = None
MAP_LIST = None
SPELLCHECK = None
CHARACTER_LIST = None

def post_json(url, forms = {}):
        resp = requests.post(url, data = forms)
        return resp.json()

def request_ticket():
        forms = {"account" : USERNAME, "password" : PASSWORD}
        ticket_json = post_json('https://www.f-list.net/json/getApiTicket.php', forms)
        if ticket_json['error'] == '':
                return ticket_json['ticket']
        else:
                print_error(ticket_json['error'])
                return 0

def print_error(text):
        print('Error: ',text)
        if text == 'Invalid ticket.':
                global TICKET
                TICKET = None

def ticket():
        global TICKET
        if TICKET == None:
                TICKET = request_ticket()
        return TICKET

def request_character(name, ticket):
        forms = {"account" : USERNAME, "ticket" : ticket, "name" : name}
        character_json = post_json('https://www.f-list.net/json/api/character-data.php', forms)
        return character_json

def cap_grade(num_points, max_points):
        grade = num_points/max_points
        overflow_grade = grade - 1
        if overflow_grade > 0:
                grade = 1
                overflow_grade *= (MAX_EXTRA_CREDIT-1)
                grade += (overflow_grade if overflow_grade < (MAX_EXTRA_CREDIT-1) else (MAX_EXTRA_CREDIT-1))
        return grade

def get_info_by_name(name):
        global INFO_LIST
        if INFO_LIST == None:
                INFO_LIST = post_json('https://www.f-list.net/json/api/info-list.php')
        for info in INFO_LIST['info']['3']['items']:
                if info['name'] == name:
                        return str(info['id'])
        return -1

def get_infotag(name):
        global MAP_LIST
        if MAP_LIST == None:
                MAP_LIST = post_json('https://www.f-list.net/json/api/mapping-list.php')
        for tag in MAP_LIST['listitems']:
                if tag['value'] == name:
                        return tag['id']
        return -1

def spellcheck_api(text):
        text = re.sub("[\[].*?[\]]", "", text)
        global SPELLCHECK
        if SPELLCHECK == None:
                SPELLCHECK = requests.post('http://service.afterthedeadline.com/stats', data = {'key' : 'flists20170418', 'data' : text})
        spellcheck_xml = ET.fromstring(SPELLCHECK.text)
        errors = 0
        for node in spellcheck_xml:
                if node[0].text == 'spell' and node[1].text != 'raw':
                        errors += int(node[2].text)
        length = (len(text) if len(text) >= SPELLING_ERROR_PER_CHARACTERS else SPELLING_ERROR_PER_CHARACTERS)
        return length/(1 if errors < 1 else errors)

def grade_character(json, my_json):
        if json['error'] != '':
                print_error(json['error'])
                return -1
        if my_json['error'] != '':
                print_error(my_json['error'])
                return -1
        if REJECT_ODD_GENDERS and not get_info_by_name('Gender') in json['infotags']:
                return 0
        elif REJECT_ODD_GENDERS and json['infotags'][get_info_by_name('Gender')] != get_infotag('Male') and\
                   json['infotags'][get_info_by_name('Gender')] != get_infotag('Female') and REJECT_ODD_GENDERS:
                        return 0
        if get_info_by_name('Orientation') in json['infotags']:
                if json['infotags'][get_info_by_name('Orientation')] == get_infotag('Gay') and my_json['infotags'][get_info_by_name('Orientation')] == get_infotag('Straight'):
                        return 0 
                elif (json['infotags'][get_info_by_name('Orientation')] == get_infotag('Gay') or my_json['infotags'][get_info_by_name('Orientation')] == get_infotag('Gay')) and\
                     get_info_by_name('Gender') in my_json['infotags'] and get_info_by_name('Gender') in json['infotags'] and\
                     ((my_json['infotags'][get_info_by_name('Gender')] == get_infotag('Male') and json['infotags'][get_info_by_name('Gender')] == get_infotag('Female')) or\
                     (my_json['infotags'][get_info_by_name('Gender')] == get_infotag('Female') and json['infotags'][get_info_by_name('Gender')] == get_infotag('Male'))):
                        return 0 
                elif (json['infotags'][get_info_by_name('Orientation')] == get_infotag('Straight') or my_json['infotags'][get_info_by_name('Orientation')] == get_infotag('Straight')) and\
                     get_info_by_name('Gender') in my_json['infotags'] and get_info_by_name('Gender') in json['infotags'] and\
                     my_json['infotags'][get_info_by_name('Gender')] == json['infotags'][get_info_by_name('Gender')]:
                        return 0 
                elif my_json['infotags'][get_info_by_name('Orientation')] == get_infotag('Bi - female preference') and get_info_by_name('Gender') in json['infotags'] and\
                     json['infotags'][get_info_by_name('Gender')] == get_infotag('Male'):
                        return 0 
                elif my_json['infotags'][get_info_by_name('Orientation')] == get_infotag('Bi - male preference') and get_info_by_name('Gender') in json['infotags'] and\
                     json['infotags'][get_info_by_name('Gender')] == get_infotag('Female'):
                        return 0 
                
        grades = defaultdict(int)
        grades['bad species'] = GRADE_WEIGHTS['bad species']
        if not get_info_by_name('Species') in json['infotags']:
                grades['bad species'] = 0
        else:
                for species in BAD_SPECIES_LIST:
                        if species.upper() in json['infotags'][get_info_by_name('Species')].upper():
                                grades['bad species'] = 0
                                
        name = json['name']
        grades['name punctuation'] = (0 if ' ' in name or '-' in name else 1) * GRADE_WEIGHTS['name punctuation']
        
        images = json['images']
        grades['no images'] = (0 if len(images) == 0 else 1) * GRADE_WEIGHTS['no images']
        
        custom_kinks = json['custom_kinks']
        grades['custom kinks'] = cap_grade(len(custom_kinks), EXPECTED_NUMBER_CUSTOM_KINKS) * GRADE_WEIGHTS['custom kinks']
        
        description = json['description']
        
        description_notags = re.sub("[\[].*?[\]]", "", description)
        for autofail_word in AUTOFAIL_DESCRIPTION_LIST:
                if autofail_word.upper() in description.upper():
                        return 0
        tags_overused = 1.5
        for tag, max_use in BBCODE_TAG_LIST.items():
                used = description.upper().count(tag.upper())
                if used > max_use:
                        tags_overused -= (used-max_use)/(max_use*2)
        if tags_overused < 0:
                tags_overused = 0
        grades['bbcode abuse'] = cap_grade(tags_overused, 1) * GRADE_WEIGHTS['bbcode abuse']
        
        grades['punctuation'] = (0 if ('!!' in description or '??' in description) else 1) * GRADE_WEIGHTS['punctuation']
        
        grades['profile play'] = (0 if '[icon]'.upper() in description.upper() or '[user]'.upper() in description.upper() else 1) * GRADE_WEIGHTS['profile play']

        description_length = len(description_notags)
        inline_modifier = description.count('[/img]') * PICTURE_IS_WORTH
        linebreaks_allowed = (description_length+inline_modifier)/LINEBREAK_PER_CHARACTERS
        linebreaks = re.sub("[\[].*?[\]]", "", re.sub("(\[quote\]|\r\n\[url).*?(\[\/quote\]|\[\/url\])","",description, flags = re.DOTALL)).count('\n')
        linebreak_to_text_ratio = linebreaks_allowed / (1 if linebreaks < 1 else linebreaks)
        grades['description length'] = cap_grade(description_length, EXPECTED_DESCRIPTION_LENGTH) * linebreak_to_text_ratio * GRADE_WEIGHTS['description length']
        if grades['description length'] > 1.2*GRADE_WEIGHTS['description length']:
                grades['description length'] = 1.2*GRADE_WEIGHTS['description length']

        grades['literacy'] = cap_grade(spellcheck_api(description_notags), SPELLING_ERROR_PER_CHARACTERS) * GRADE_WEIGHTS['literacy']
        
        kinks = json['kinks']
        my_kinks = my_json['kinks']
        matches = 0
        num_mismatches = 0
        if not len(kinks) <= UNDERKINKING_BONUS_FLOOR:
                for kink, rating in my_kinks.items():
                        if kink in kinks:
                                if kinks[kink] == rating:
                                        matches += 1
                                elif (rating == 'fave' and kinks[kink] == 'yes') or (rating == 'yes' and kinks[kink] == 'fave'):
                                        matches += 0.75
                                elif (rating == 'maybe' and kinks[kink] == 'yes') or (rating == 'maybe' and kinks[kink] == 'fave'):
                                        matches += 0.25
                                elif (rating == 'no' and kinks[kink] == 'fave') or (rating == 'fave' and kinks[kink] == 'no'):
                                        matches -= 0.5 * ((len(kinks)/OVERKINKING_PENALTY_FLOOR)*OVERKINKING_MODIFIER if len(kinks) > OVERKINKING_PENALTY_FLOOR else 1)
                                elif (rating == 'no' and kinks[kink] == 'yes') or (rating == 'yes' and kinks[kink] == 'no'):
                                        matches -= 0.25 * ((len(kinks)/OVERKINKING_PENALTY_FLOOR)*OVERKINKING_MODIFIER if len(kinks) > OVERKINKING_PENALTY_FLOOR else 1)
                grades['kink matching'] = cap_grade(matches, EXPECTED_MATCHING_KINKS) * GRADE_WEIGHTS['kink matching']
        else:
                normal_grade = cap_grade(len(custom_kinks), EXPECTED_MATCHING_KINKS*2) * GRADE_WEIGHTS['kink matching']
                grades['kink matching'] =  (normal_grade if len(custom_kinks) <= EXPECTED_MAXIMUM_CUSTOM_KINKS else (normal_grade - (len(custom_kinks)/EXPECTED_MAXIMUM_CUSTOM_KINKS) if normal_grade - (len(custom_kinks)/EXPECTED_MAXIMUM_CUSTOM_KINKS) > 0 else 0))
        total_grade = 0
        for rubric, grade in grades.items():
                #print(rubric + ': ' + str(grade))
                total_grade += grade
        return (0 if total_grade < 0 else total_grade * 100)

async def hello(ticket):
        async with websockets.connect('ws://{0}:{1}'.format(HOST, PORT)) as websocket:
                identify = "IDN {{ \"method\": \"ticket\", \"account\": \"{0}\", \"ticket\": \"{1}\", \"character\": \"{4}\", \"cname\": \"{2}\", \"cversion\": \"{3}\" }}".format(USERNAME, ticket, SERVICE_NAME, SERVICE_VERSION, CHARACTER)
                #print("<< {}".format(identify))
                await websocket.send(identify)
                join = "JCH {{\"channel\": \"{0}\"}}".format(CHANNEL)
                #print("<< {}".format(join))
                await websocket.send(join)
                while True:
                        receive = await websocket.recv()
                        if receive.startswith('ERR'):
                                print("<< {}".format(receive))
                        if receive.startswith('ICH'):
                                global CHARACTER_LIST
                                CHARACTER_LIST = receive[4:]
                                websocket.close()
                                return

if __name__ == '__main__':
        '''my_character = request_character(CHARACTER, ticket())
        character = request_character("chris waterwolf", ticket())
        print('Grade: ',grade_character(character,my_character))'''
        asyncio.get_event_loop().run_until_complete(hello(ticket()))
        print("Successfully grabbed profile list. {0} is grading them now.".format(SERVICE_NAME))
        chars = json.loads(CHARACTER_LIST)
        my_character = request_character(CHARACTER, ticket())
        graded_characters = defaultdict(int)
        cur_char = 0
        for char in chars['users']:
                num_dashes = int(50*(cur_char/len(chars['users'])))
                num_spaces = int(50*((len(chars['users'])-cur_char)/len(chars['users'])))
                while num_dashes+num_spaces < 50:
                        num_dashes += 1
                sys.stdout.write("\r[" + "-"*num_dashes + " "*num_spaces + "]")
                sys.stdout.flush()
                if not char['identity'] in MY_CHARACTERS:
                        try:
                                while True:
                                        character = request_character(char['identity'], ticket())
                                        graded_characters[char['identity']] = grade_character(character,my_character)
                                        if graded_characters[char['identity']] >= 0:
                                                cur_char += 1
                                                break
                        except Exception as e:
                                print("Couldn't grade {0}: \n{1}".format(char['identity'],e))
        print()
        top_chars = sorted(graded_characters, key = (lambda x: graded_characters[x]), reverse = True)
        if graded_characters[top_chars[0]] < QUALITY_CUTOFF:
                print("I couldn't find anyone worth your time, {0}. :( Try again later?".format(CHARACTER))
        else:
                cutoff_chars = []
                for char in top_chars:
                        if graded_characters[char] >= QUALITY_CUTOFF:
                                cutoff_chars.append(char)
                print('\nAll done, {0}. Consider checking out these profiles: '.format(CHARACTER))
                if RANDOMIZE_SUGGESTIONS:
                        shuffle(cutoff_chars)
                for _ in range(SUGGESTIONS_TO_MAKE):
                        if len(cutoff_chars) > _ :
                                top = cutoff_chars[_]
                                print('{0} (Grade: {1})'.format(top, graded_characters[top]))
