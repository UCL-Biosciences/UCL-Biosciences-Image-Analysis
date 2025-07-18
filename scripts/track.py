import pandas as pd
from skimage.measure import regionprops, label
import trackpy as tp

def extract_centroids(masks):
    centroids = []
    for t, mask in enumerate(masks):
        labelled = label(mask)
        props = regionprops(labelled)
        for prop in props:
            y, x = prop.centroid
            centroids.append({'frame': t, 'x': x, 'y': y, 'particle': None})
    return pd.DataFrame(centroids)

def track_particles(df, search_range=10, memory=2):
    linked_df = tp.link_df(df, search_range=search_range, memory=memory)
    linked_df['vx'] = linked_df.groupby('particle')['x'].diff()
    linked_df['vy'] = linked_df.groupby('particle')['y'].diff()
    linked_df['speed'] = (linked_df['vx']**2 + linked_df['vy']**2)**0.5
    return linked_df
