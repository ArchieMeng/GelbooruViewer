from __init__ import GelbooruViewer
from time import sleep, time
from pickle import dump

if __name__ == "__main__":
    viewer = GelbooruViewer()
    tags = ['1da']
    limit = 50
    t1 = time()
    pictures = viewer.get_all_generator(tags, num=500)
    print(pictures)
    if pictures:
        for i, picture in enumerate(pictures):
            if i == 10:
                print("get result and stop")
                break
        t2 = time()
        print(t2 - t1, "s")
        # sleep(15)
        t3 = time()
        pictures = viewer.get_all_generator(tags, num=500)
        print(len([*pictures]))
        t4 = time()
        print("times: 1:{}s 2:{}s".format(t2-t1, t4-t3))
    else:
        print("tag:", tags, "not found")
