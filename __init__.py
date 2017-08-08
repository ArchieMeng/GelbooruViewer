from xml.etree import ElementTree
import requests
from threading import Lock, Thread
import logging
from time import time, sleep
from lru import LRU


class GelbooruPicture:
    def __init__(
            self,
            width,
            height,
            score,
            source,
            preview_url,
            sample_url,
            file_url,
            created_at,
            creator_id,
            tags: list,
            picture_id,  # the id attributes in api xml, conflicts with python built-in id method
            rating: str
    ):
        self.width = width
        self.height = height
        self.score = score
        self.source = source
        self.preview_url = preview_url
        self.sample_url = sample_url
        self.file_url = file_url
        self.created_at = created_at
        self.creator_id = creator_id
        self.tags = tags
        self.picture_id = picture_id
        self.rating = rating

    def __str__(self):
        return '''
        <====================================id:{picture_id}==============================================>
        size: {width}*{height}
        time: {time}
        score: {score}
        source: {source}
        preview url: {preview_url}
        file url: {file_url}
        tags: {tags}
        rating: {rating}
        <=======================================end=====================================================>
        '''.format(
            picture_id=self.picture_id,
            width=self.width,
            height=self.height,
            time=self.created_at,
            score=self.score,
            source=self.source,
            preview_url=self.preview_url,
            file_url=self.file_url,
            tags=self.tags,
            rating=self.rating
        )


class GelbooruViewer:
    API_URL = "https://gelbooru.com/index.php?page=dapi&s=post&q=index"
    MAX_ID = 1
    MAX_ID_LOCK = Lock()
    MAX_CACHE_SIZE = 64
    MAX_CACHE_TIME = 60  # minutes

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                'Accept': 'application/json, application/xml',
                'Accept-Language': 'en-US',
                'User-Agent': 'Mozilla/5.0 GelbooruViewer/1.0 (+https://github.com/ArchieMeng/GelbooruViewer)'
            }
        )
        # only cache for get_all with tags while pid is 0!!!
        self.cache = LRU(GelbooruViewer.MAX_CACHE_SIZE)
        self.cache_lock = Lock()
        # occasionally update cache
        self.last_cache_used = time()
        self.update_cache_thread = Thread(target=self._update_cache_loop, daemon=True)
        self.update_cache_thread.start()

        # get latest image to update MAX_ID
        self.get(limit=0)

    def _update_cache_loop(self):
        """
        Occasionally refresh cache. Clear cache if unused for a long time.
        :return:
        """
        minutes = 30
        while True:
            sleep(60 * minutes)
            if time() - self.last_cache_used > self.MAX_CACHE_TIME * 60:
                self.cache.clear()
                continue
            with self.cache_lock:
                keys = self.cache.keys()
            threads = []
            count = 0
            for key in keys:
                if count and count % 4 == 0:
                    for thread in threads:
                        thread.join()
                    threads = []
                count += 1
                thread = Thread(
                    target=self.get_all,
                    args=(key.split('+'), 0, 500, 5, False)
                )
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    def get_raw_content(self, **kwargs):
        content = None
        with self.session as session:
            with session.get(GelbooruViewer.API_URL, params=kwargs) as response:
                try:
                    content = response.content
                except Exception as e:
                    logging.error(str(e))
                    pass
        return content

    def get(self, **kwargs)->list:
        """
        use Gelbooru api to fetch picture info.

        :param kwargs: allowed args includes
        limit: How many posts you want to retrieve. There is a hard limit of 100 posts per request.

        pid: The page number.

        cid: Change ID of the post.
        This is in Unix time so there are likely others with the same value if updated at the same time.

        tags: The tags to search for. Any tag combination that works on the web site will work here.
        This includes all the meta-tags. See cheatsheet for more information.

        :return: a list of type GelbooruPicture, if sth wrong happened, a empty list will be return
        """
        attempt = 0
        content = None
        while attempt < 3 and content is None:
            attempt += 1
            content = self.get_raw_content(**kwargs)

        if content is None:
            return []
        if isinstance(content, bytes):
            xml_str = content.decode('utf-8')
        else:
            xml_str = content

        root = ElementTree.fromstring(xml_str)
        posts = root.findall('post')
        picture_list = []

        if posts:
            cur_max_id = int(posts[0].attrib['id'])
            with GelbooruViewer.MAX_ID_LOCK:
                GelbooruViewer.MAX_ID = max(GelbooruViewer.MAX_ID, cur_max_id)

        for post in posts:
            info = post.attrib
            picture_list.append(
                GelbooruPicture(
                    info['width'],
                    info['height'],
                    info['score'],
                    info['source'],
                    "https:"+info['preview_url'],
                    "https:"+info['sample_url'],
                    "https:"+info['file_url'],
                    info['created_at'],
                    info['creator_id'],
                    [tag for tag in info['tags'].split(' ') if tag and not tag.isspace()],
                    info['id'],
                    info['rating']
                )
            )
        return picture_list

    def get_all(self, tags: list, pid=0, num=None, thread_limit=5, use_cache=True) -> list:
        """
        regardless of official request limit amount, use threading to request amount you want

        :param use_cache: whether prefer internal cache

        :param thread_limit: amount of threads running at the same time

        :param tags: tags must be provided

        :param pid: beginning pid

        :param num: num of picture you want.
        This function might return less pictures if Gelbooru hasn't got enough picture

        :return: list of GelbooruPicture

        """
        tags.sort()
        if use_cache and pid == 0:
            with self.cache_lock:
                key = '+'.join(tags)
                if key in self.cache:
                    self.last_cache_used = time()
                    if not num:
                        return self.cache[key]
                    else:
                        return self.cache[key][:num]

        content = self.get_raw_content(tags=tags, limit=0)
        xml_str = content.decode('utf-8')
        root = ElementTree.fromstring(xml_str)
        total = int(root.attrib['count'])
        if isinstance(num, int):
            if num > 0:
                # if total amount is too large, use num instead.
                total = min(total, num)
        picture_list = []

        def _get(tags, pid):
            content = self.get_raw_content(tags=tags, limit=100, pid=pid)
            xml_string = content.decode()
            posts = ElementTree.fromstring(xml_string).findall('post')
            for post in posts:
                info = post.attrib
                picture_list.append(
                    GelbooruPicture(
                        info['width'],
                        info['height'],
                        info['score'],
                        info['source'],
                        "https:" + info['preview_url'],
                        "https:" + info['sample_url'],
                        "https:" + info['file_url'],
                        info['created_at'],
                        info['creator_id'],
                        [tag for tag in info['tags'].split(' ') if tag and not tag.isspace()],
                        info['id'],
                        info['rating']
                    )
                )
        if tags:
            threads = []
            for i in range(pid, int(total / 100) + 1):
                if i and i % thread_limit == 0:
                    # stop and wait threads to finish
                    for thread in threads:
                        thread.join()
                    threads = []
                thread = Thread(target=_get, args=[tags, i])
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            if pid == 0:
                with self.cache_lock:
                    self.last_cache_used = time()
                    key = '+'.join(tags)
                    self.cache[key] = picture_list
            return picture_list
        else:
            return []

    def __del__(self):
        self.session.close()
