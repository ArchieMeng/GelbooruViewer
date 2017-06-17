from xml.etree import ElementTree
from aiohttp import ClientSession
import asyncio
import logging


class GelbooruPicture:
    """
    A gelbooru picture model
    attribution includes:
            max_id: int, 
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
            picture_id,
            rating: str
    """
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
    EXTRA_HEADERS = {
        'Accept': 'application/json, application/xml',
        'Accept-Language': 'en-US',
        'User-Agent': 'Mozilla/5.0 GelbooruViewer/1.0 (+https://github.com/ArchieMeng/GelbooruViewer)'
    }
    MAX_ID = 1
    MAX_ID_LOCK = asyncio.Lock()

    def __init__(self):
        self.get(limit=1)

    async def async_get(self, url, params):
        async with ClientSession() as session:
            async with session.get(url, params=params, headers=GelbooruViewer.EXTRA_HEADERS) as response:
                return await response.read()

    async def async_set_max_id(self, max_id):
        async with GelbooruViewer.MAX_ID_LOCK as lock:
            if GelbooruViewer.MAX_ID < max_id:
                GelbooruViewer.MAX_ID = max_id

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

        id: The post id.

        :return: a list of type GelbooruPicture, if sth wrong happened, a empty list will be return
        """
        attempt = 0
        content = None
        while attempt < 5:
            attempt += 1
            try:
                loop = asyncio.get_event_loop()
                content = loop.run_until_complete(self.async_get(GelbooruViewer.API_URL, kwargs))
                break
            except Exception as e:
                logging.error(str(e))

        if content is None:
            return []

        xml_str = content.decode('utf-8')
        root = ElementTree.fromstring(xml_str)
        posts = root.findall('post')
        picture_list = []
        print("GET {title} : {content}".format(title=root.tag, content=root.attrib))

        if posts:
            cur_max_id = int(posts[0].attrib['id'])
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.async_set_max_id(cur_max_id))

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