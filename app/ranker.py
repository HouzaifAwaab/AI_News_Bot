from datetime import datetime

def compute_score(url, title, source_id, published, stars=0, upvotes=0):
    base = 1
    if title:
        base += min(3, len(title) / 30)
    return base + stars + upvotes
