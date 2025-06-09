# required:
#   - networkx, matplotlib, scipy: graph
#   - pyvis: graph visualization
#   - requests: API calls

import networkx as nx
from pyvis.network import Network
import requests
import pickle
import json

# Load graph to update it - or create a new one
try:
    with open("graph.pkl", "rb") as f:
        G = pickle.load(f)
except FileNotFoundError:
    G = nx.Graph()

types_color = {
    "artist": "#1f78b4",
    "song": "#33a02c",
    "album": "#6a3d9a",
    "label": "#e31a1c",
}

nodes_added = 0

def print_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

def request(path, query, limit=1):
    """Make a GET request to musicbrainz with given route and optional parameters."""
    headers = {
        "User-Agent": "IR_Assignment/1.0 (geg.valentin@gmail.com)"
    }
    params = {
        "query": query,
        "fmt": "json",
        "limit": limit
    }
    response = requests.get(f"https://musicbrainz.org/ws/2/{path}/", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error fetching data:", response.status_code)
        return None

def add_node(node_id, label, type, otherInfo={}):
    """Add a node to the graph with the given ID, label, and type."""
    if G.nodes.get(node_id):
        return node_id
    for n in G.nodes(data=True):
        if n[1]['label'].lower() == label.lower():
            return n[0]
    print(f"Adding {type}: {label}")
    G.add_node(node_id, label=label, color=types_color[type], type=type, **otherInfo)
    global nodes_added
    nodes_added += 1
    return node_id

def load_artist_by_name(artist_name, limit=1):
    data = request("artist", f'artist:"{artist_name}"', limit)
    if data is None:
        return None
    for rec in data.get('artists', []):
        artist_id = rec['id']
        artist_name = rec['name']
        artist_id = add_node(artist_id, label=artist_name, type="artist", otherInfo={'country': rec.get('country', 'unknown'), 'gender': rec.get('gender', 'unknown')})
        load_artist_songs(artist_id, limit)

def load_artist_songs(artist_id, limit=1, depth=0):
    data = request("release", f'arid:"{artist_id}"', limit)
    if data is None:
        return []

    for rec in data.get('releases', []):
        #print_json(rec)
        song_id = rec['id']
        song_title = rec['title']
        #print(rec)
        print("  " * depth + f"Song: {song_title}")
        # Add song node
        song_id = add_node(song_id, label=song_title, type="song")
        G.add_edge(song_id, artist_id)

        # Add album node
        if "primary-type" in rec['release-group'] and rec['release-group']['primary-type'] == 'Album':
            album_id = rec['release-group']['id']
            album_title = rec['release-group']['title']
            album_id = add_node(album_id, label=album_title, type="album")
            G.add_edge(album_id, artist_id)
        #print(rec["label-info"])

        # Add label nodes
        for label in rec.get('label-info', []):
            if 'label' in label:
                label_id = label['label']['id']
                label_name = label['label']['name']
                if label_name == '[no label]':
                    continue
                label_id = add_node(label_id, label=label_name, type="label")
                G.add_edge(label_id, artist_id)

        # Add artist credits
        artist_credits = rec.get('artist-credit', [])
        for credit in artist_credits:
            if 'artist' in credit:
                artist_credit_id = credit['artist']['id']
                if not G.has_node(artist_credit_id):
                    artist_credit_name = credit['artist']['name']
                    artist_credit_id = add_node(artist_credit_id, label=artist_credit_name, type="artist")
                    G.add_edge(song_id, artist_credit_id)
                    if limit > 0:
                       load_artist_songs(artist_credit_id, limit - 1, depth+1)

def drawAndSave():
    # Draw graph
    nx.draw(G, with_labels=True)

    # Show graph with pyvis
    net = Network(notebook=True)
    net.from_nx(G)
    net.show("graph.html")

    # Save graph
    with open("graph.pkl", "wb") as f:
        pickle.dump(G, f)

try:
    while True:
        # Get artist name prompt
        artist_name = input("Enter artist name to load (or 'exit' to quit): ")
        if artist_name.lower() == 'exit':
            break
        # Load artist by name
        print(f"Loading artist: {artist_name}")
        load_artist_by_name(artist_name, 10)
        print(f"Total nodes added: {nodes_added}")
        nodes_added = 0
        drawAndSave()
except KeyboardInterrupt:
    print('Interrupted by user, saving graph...')
    print(f"Total nodes added: {nodes_added}")
    drawAndSave()
