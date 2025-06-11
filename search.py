import pickle
import streamlit as st
from rapidfuzz import fuzz

types_color = {
    "artist": "#1f78b4",
    "song": "#33a02c",
    "album": "#6a3d9a",
    "label": "#e31a1c",
}

def renderTypeBadge(type):
    return f"<span style='background-color:{types_color[type]};color:white;padding:2px 6px;border-radius:6px;font-size:0.8em;margin-right:6px'>{type.capitalize()}</span>"

def renderEntityItem(id, label, type):
    badge = renderTypeBadge(type)
    url = f"?id={id}"
    st.markdown(f"{badge}<a href='{url}' target='_self' style='font-size:1.3em;text-decoration:none;font-weight:bold'>{label}</a>", unsafe_allow_html=True)
    related = list(G.neighbors(id))
    # List related nodes
    if related:
        related_labels = [G.nodes.get(r_id, {}).get('label', '') for r_id in related]
        related_links = [f"<a href='?id={r_id}' style='color:gray'>{label}</a>" for r_id, label in zip(related, related_labels)]
        related_str = ", ".join(related_links)
        st.markdown(f"<span style='font-size:em;color:gray'>{related_str}</span>", unsafe_allow_html=True)

def renderGraphPage():
    total_nodes = G.number_of_nodes()
    with open("graph.html", "rb") as f:
        graph_html = f.read().decode("utf-8")
        st.write(f"{total_nodes} entities")
        st.components.v1.html(graph_html, height=600, scrolling=True)
                
def renderQueryPage():
    query = st.text_input("Enter your search query here (artist, song, album, label):")
    if query:
        result_scores = {}
        for node in G.nodes(data=True):
            id = node[0]
            label = node[1]['label']
            score = fuzz.partial_ratio(query.lower(), label.lower())
            if score > 80:
                result_scores[id] = score
        if not result_scores:
            st.write(f"No results found for '{query}'...")
        else:
            result_list = list(result_scores.keys())
            result_list.sort(key=lambda x: result_scores[x], reverse=True)
            st.write(f"{len(result_list)} results :")
            for n_id in result_list:
                n = G.nodes.get(n_id)
                renderEntityItem(n_id, n['label'], n['type'])

def renderEntityPage(entity_id):
    node = G.nodes.get(entity_id)
    if node:
        st.header(f"{node['type'].capitalize()} Details")
        st.write(f"<u>Name:</u> {node['label']}", unsafe_allow_html=True)
        st.write(f"<u>Type:</u> {renderTypeBadge(node['type'])}", unsafe_allow_html=True)
        st.write(f"<u>ID:</u> *{entity_id}*", unsafe_allow_html=True)
        st.write(f"<u>{G.degree(entity_id)} direct relationships</u>", unsafe_allow_html=True)
        st.markdown("<a href='/' target='_self' style='text-decoration:none'><- Back to Search</a>", unsafe_allow_html=True)
        # Add all related nodes
        st.subheader("Related Entities")
        related_nodes = list(G.neighbors(entity_id))
        if related_nodes:
            for related_id in related_nodes:
                related_node = G.nodes.get(related_id)
                if related_node:
                    renderEntityItem(related_id, related_node['label'], related_node['type'])
    else:
        st.write("No details found for this ID.")

if __name__ == "__main__":
    # Load graph
    try:
        with open("graph.pkl", "rb") as f:
            G = pickle.load(f)
    except FileNotFoundError:
        print("Graph file not found. Please make sure 'graph.pkl' exists in the current directory.")
        exit(1)
    st.set_page_config(page_title="Music Search", layout="wide")
    st.title("Music Search")
    params = st.query_params
    selected_id = params.get("id", None)
    if selected_id == "graph":
        renderGraphPage()
    else:
        st.link_button(f"Open Graph ({G.number_of_nodes()} entities)", "?id=graph")
        if selected_id:
            renderEntityPage(selected_id)
        else:
            renderQueryPage()
