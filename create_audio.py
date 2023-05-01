import yaml
import requests
from pydub import AudioSegment
from pydub.silence import split_on_silence

def load_lyrics_from_yaml(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        lyrics = yaml.safe_load(file)
    return lyrics

def translate_text_to_speech(text, language='ja', filename="output.mp3"):
    url = 'https://translate.google.com/translate_tts'
    params = {
        'ie': 'UTF-8',
        'q': text,
        'tl': language,
        'client': 'tw-ob'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        with open('./assets/'+filename, 'wb') as file:
            file.write(response.content)
        print(f'Saved {filename} successfully.')
    else:
        print('Error:', response.status_code)

def split_audio_by_silence(number, audio_file, min_silence_duration=500):
    audio = AudioSegment.from_file('./assets/'+ audio_file, format='mp3')
    chunks = split_on_silence(audio, min_silence_len=min_silence_duration, silence_thresh=-70)

    for i, chunk in enumerate(chunks):
        chunk.export(f'./assets/{number+1:02}_{i+1:02}.mp3', format='mp3')
        print(f'Saved {number+1:02}_{i+1:02}.mp3 successfully.')

lyrics_file = 'lyrics.yaml'
lyrics = load_lyrics_from_yaml(lyrics_file)

for i, song in enumerate(lyrics):
    print("===")
    original_text = song['original'].strip()
    #tokens_text = ' '.join(song['tokens'])
    tokens_text = song['hiragana'].strip()
    print(tokens_text.count(','), "Tokens")
    
    sentence_filename = f'{i+1:02}.mp3'
    pauses_filename = f'{i+1:02}_pauses.mp3'
    
    translate_text_to_speech(original_text, 'ja', sentence_filename)
    translate_text_to_speech(tokens_text, 'ja', pauses_filename)
    
    print(f'Saved {sentence_filename} and {pauses_filename}.')
    
    split_audio_by_silence(i, pauses_filename, min_silence_duration=150)
