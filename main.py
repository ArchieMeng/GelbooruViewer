from __init__ import GelbooruViewer
from time import sleep, time
from pickle import dump

if __name__ == "__main__":
    viewer = GelbooruViewer()
    tags = ['weiss']
    t1 = time()
    pictures = viewer.get_all(tags=tags, num=500)
    print(len(pictures), pictures)
    t2 = time()
    pictures = viewer.get_all(tags=tags, num=500)
    print(len(pictures), pictures)
    t3 = time()
    print(len(pictures), "times: 1:{}s 2:{}s".format(t2-t1, t3-t2))
    sleep(60)
    print(viewer.get_all(tags=tags))
    with open('-'.join(tags) + '.pickle', 'wb') as wf:
        dump(pictures, wf, protocol=2)
