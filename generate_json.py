import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('replay_file', help='.StormReplay file to load')
args = parser.parse_args()

print "Parsing Game Events...this may take 30+ seconds."
result = subprocess.check_output(['python', 'heroprotocol/heroprotocol.py', '--details', '--json', '--gameevents', args.replay_file])
print "Generating statistics and timeline."

lines = []
lines = [json.loads(line) for line in result.splitlines()]

hero_map = {'Valla': {308: 'MultiShot(W)', 307: 'Hungering Arrow(Q)', 310: 'Vault(E)', 112: 'Mount(Z)'}}

abil_map = {308: 'MultiShot', 307: 'Hungering Arrow', 310: 'Vault', 311: 'Strafe', 309: 'Rain of Vengeance',
            490: 'Bone Shield', 494: 'Spectral Scythe',
            112: 'Mount',
           }

abils = {}
timeline = []
for event in lines:
    if event.get('_event') == "NNet.Game.SCmdEvent":
        if event.get('_userid')['m_userId'] == 0:
            if event.get('m_abil'):
                abil = event.get('m_abil')
                abil_id = abil['m_abilLink']
                abil_name = abil_map.get(abil_id, abil_id)
                # Increment counter for each ability.
                abils[abil_id] = abils.get(abil_id, 0) + 1
                if abil_id in hero_map['Valla'].keys():
                    timeline.append({'group': abil_id, 'start': event.get('_gameloop')})
                    # Debug command.
                    # print "{0} - {1}".format(abil, event.get('_gameloop'))

# Build JSON data structure for import to report html.
groups = []
for key in hero_map['Valla'].keys():
    groups.append({'id': key, 'content': hero_map['Valla'][key]})

# Find player name.
player_name = ''
player_list = lines[0]['m_playerList']

# Check if Valla's in the replay and pull out her player name.
for player in player_list:
    if player['m_hero'] == u'Valla':
        player_name = player['m_name']

if not player_name:
    sys.exit('No hero named Valla found in replay.')

details = {'mapname': lines[0]['m_title'],
           'heroname': 'Valla',
           'playername': player_name,
           'multishot': [[abils[308], 67]]
          }

json_structure = {'details': details,
                  'groups': groups,
                  'timeline': timeline,
                  'abils': abils,
                 }

# Write json data to file.
json_filename = args.replay_file + '.json'
print "Writing data to {0}".format(json_filename)
with open(json_filename, 'w') as outfile:
    json.dump(json_structure, outfile)

