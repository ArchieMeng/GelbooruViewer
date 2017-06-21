# GelbooruViewer

GelbooruViewer is a python package used to fetch picture info from [gelbooru](https://gelbooru.com) by official api.

### Tech
GelbooruViewer contains class GelbooruPicture (a model class of picture info) 
and GelbooruViewer (a tool to fetch pictures and return list[GelbooruPicture])

Gelbooru uses some algorithm and open source library to enhance performance:

* threading - use multi-threading to speed up GET method.
* [lru-dict](https://github.com/amitdev/lru-dict) - C-implentment Python LRU cache library 


And of course GelbooruViewer itself is open source with a [public repository](https://github.com/ArchieMeng/GelbooruViewer) on GitHub.

### Installation

Gelbooru requires [Python3](https://www.python.org/) 3.5+ and requests to run.

Install the dependencies ,
and install lru-dict by pip or just clone and install it by yourself if you want to use cache ( Experimental ).

In Debian or Ubuntu system
```sh
$ sudo apt update && sudo apt install libpython3-dev python3-pip
$ sudo pip3 install lru-dict requests
$ git clone https://github.com/ArchieMeng/GelbooruViewer.git
```

In other system, just install library list above. I don't know how to operate that in other system. So just add to this readme if u know, and give me a push request.

## Sample code

```Python
>> from GelbooruViewer import GelbooruPicture, GelbooruViewer
>> viewer = GelbooruViewer()
>> tags = ['1girl', 'long_hair']
>> pictures = viewer.get(tags=tags) # simple get method with official limit=100, only 100 pictures per call.
>> pictures = viewer.get_all(tags=tags, num=500) # multi-threading method with out limit. with cache enabled by default.
>> pictures = viewer.get_all(tags=tags, num=500, use_cache=False) # with cache disabled.
>> for picture in pictures: # print all pictures
...    print(picture) # print picture object, which is an instance of GelbooruPicture.
...
>>
```

### Todos

 - cache request result for more type of params. current version just cache get_all with tags set and pid equal 0
 - make LRU cache drop cache by cache memory size instead of cache amount size

License
----

GPL-3.0


**Free Software, Hell Yeah!**


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
