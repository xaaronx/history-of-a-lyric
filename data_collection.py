import requests
from re import sub
import lyricsgenius as genius

def prep_sdk(auth_code):
    '''
    Bring in genius sdk for more complex searches
    '''
    return genius.Genius(auth_code)

def convert_lyrics_to_query(raw_lyric):
    '''
    Convert lyric to api request URL
    '''
    return 'https://api.genius.com/search/?q={}'.format(sub('\s+','%20', raw_lyric).lower())

def search_api(query, auth_code, max_pages):
    '''
    Search Genius API for all songs on max_pages with certain lyric query
    '''
    headers = {'Authorization': 'Bearer {}'.format(client_access_token)}
    current_page = 1
    next_page = True
    songs = []

    while next_page:
        params = {'page': current_page}
        print('Searching page {}....'.format(current_page))
        result = extract_core_elements_from_api_json(requests.get(query, headers=headers, params=params))
        if result:
            songs += result
            current_page += 1
        else:
            next_page = False
        if current_page>int(max_pages):
            break
    return songs

def extract_core_elements_from_api_json(response):
    '''
    Convert request info to output of artist and song
    '''
    output = []
    for resp in response.json()['response']['hits']:
        try: output.append((resp['result']['title'],
                          resp['result']['primary_artist']['name']))
        except: pass
    return output

def check_for_correct_search(results, lyric):
    '''
    Remove any songs with lyric in artist name
    '''
    return [song for song in results if not lyric.lower() in song[1].lower()]

def collect_songs(title, artist, sdk_object):
    '''
    Collect all song objects
    '''
    song = sdk_object.search_song(title=title, artist=artist)
    try:
        if song.artist==artist and song.title==title: return song
    except: pass

def convert_sdk_output_to_data(song):
    '''
    Return correct features
    '''
    return {'title':song.title, 'artist':song.artist, 'album':song.album,
            'media':song.media, 'year':song.year, 'lyrics':song.lyrics}

def collect_lyrics(lyric, auth_code, pages, path_name):
    '''
    Execute all
    '''
    data = json.dumps([convert_sdk_output_to_data(collect_songs(i[0],i[1], prep_sdk(client_access_token)))
            for i in search_api(convert_lyrics_to_query(lyric), client_access_token, pages)])

    with open(path_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
