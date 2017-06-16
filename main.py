from __init__ import GelbooruViewer, GelbooruPicture

if __name__ == "__main__":
    viewer = GelbooruViewer()
    for pic in viewer.get(limit=10):
        print(pic)
