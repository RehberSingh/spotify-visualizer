from flask import Flask, session, request, redirect , render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import re
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/charts',methods = ['POST'])
def click():
    uri = str(request.form.get('uri'))
    lst = re.split(r'\/|\?|=', uri)
    id_index = lst.index('playlist')+1
    id = lst[id_index]
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    def split_list(input_list):
        sublist_size = 100
        sublists = []
        for i in range(0, len(input_list), sublist_size):
            sublist = input_list[i:i + sublist_size]
            sublists.append(sublist)
        return sublists
    
    def get_playlist_name():
        name = sp.playlist(id , fields='name')
        return name['name']

    def get_playlist_items():
        tracks = []
        results = sp.playlist_tracks(id ,  limit=100, offset=0 , fields="next,items(track(id,name))")
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        return tracks
 
    def get_track_ids(playlists):
        track_ids = []
        for items in playlists:
            track_ids.append(items['track']['id'])
        return split_list(track_ids)
    
    def get_track_names(playlists):
        track_names = []
        for items in playlists:
            track_names.append(items['track']['name'])
        return track_names
    

    def get_track_analysis(track_ids):
        audio_features = []
        for ids in track_ids:
            result = sp.audio_features(ids)
            audio_features.extend(result)
        return audio_features
    
    def tempo_line_graph(audio_features):#async
        tempo = []
        for features in audio_features:
            if features:
                tempo.append(features['tempo'])
            else:
                tempo.append(100)
        return tempo
    
    def danceability_line_graph(audio_features):#async
        danceability = []
        for features in audio_features:
            if features:
                danceability.append(features['danceability'])
            else:
                danceability.append(0.5)
        return danceability
    
    def energy_line_graph(audio_features):#async
        energy = []
        for features in audio_features:
            if features:
                energy.append(features['energy'])
            else:
                energy.append(0.5)
        return energy
    
    def scatterplot(tempo , danceability , tracknames):
        if len(tempo) != len(danceability) or len(tempo) != len(tracknames):
            raise ValueError("All lists must have the same length.")
        
        scatterplot = []

        for x, y, name in zip(tempo, danceability, tracknames):
            data_dict = {'x': x, 'y': y, 'name': name}
            scatterplot.append(data_dict)

        return scatterplot

    def no_of_tracks(track_names):
        list = []
        for i in range(len(track_names)):
            list.append(i)
        return list
    name =  get_playlist_name()
    playlists = get_playlist_items()
    tracknames = get_track_names(playlists)
    track_ids = get_track_ids(playlists)
    list = no_of_tracks(tracknames)
    audio_features = get_track_analysis(track_ids)
    tempo = tempo_line_graph(audio_features)
    danceability = danceability_line_graph(audio_features)
    energy = energy_line_graph(audio_features)
    tempo_danceability_scatterplot = scatterplot(tempo , danceability , tracknames)
    energy_danceability_scatterplot = scatterplot(energy , danceability , tracknames)
    tempo_energy_scatterplot = scatterplot(tempo , energy , tracknames)
    return render_template('stats.html' , tempo = tempo, name = tracknames , danceability = danceability , energy = energy , tempo_danceability_scatterplot = tempo_danceability_scatterplot , tempo_energy_scatterplot = tempo_energy_scatterplot , energy_danceability_scatterplot = energy_danceability_scatterplot , playlist_name = name)
    

if __name__ == '__main__':
    app.run(debug=False , host=0.0.0.0)