import pickle
import streamlit as st

types_color = {
    "artist": "#1f78b4",
    "song": "#33a02c",
    "album": "#6a3d9a",
    "label": "#e31a1c",
}

def renderEntityItem(id, label, type):
    color = types_color[type]
    badge = f"<span style='background-color:{color};color:white;padding:2px 6px;border-radius:6px;font-size:0.8em;margin-right:6px'>{type.capitalize()}</span>"
    url = f"?id={id}"
    st.markdown(f"{badge}<a href='{url}' style='text-decoration:none;font-weight:bold'>{label}</a>", unsafe_allow_html=True)

def renderQueryPage():
    query = st.text_input("Enter your search query here (artist, song, album, label):")
    total_nodes = G.number_of_nodes()
    st.write(f"Total entities in the graph: {total_nodes}")
    if query:
        results = []
        for node in G.nodes(data=True):
            if query.lower() in node[1]['label'].lower():
                print(node)
                results.append(node)
        if not results:
            st.write(f"No results found for '{query}'...")
        else:
            st.write("Results :")
            for r in results:
                renderEntityItem(r[0], r[1]['label'], r[1]['type'])

def renderEntityPage(entity_id):
    node = G.nodes.get(entity_id)
    if node:
        st.header(f"{node['type'].capitalize()} Details")
        st.write(f"**Label:** {node['label']}")
        st.write(f"**Type:** {node['type']}")
        st.write(f"**ID:** {entity_id}")
        # calculate centrality in the graph
        centrality = G.degree(entity_id)
        st.write(f"**Centrality:** {centrality}")
        st.link_button("Back to search", "/")
        # add all related nodes
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
    if selected_id:
        renderEntityPage(selected_id)
    else:
        renderQueryPage()
