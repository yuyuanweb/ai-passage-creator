"""文章相关常量"""


class ArticleConstant:
    """文章相关常量"""
    
    # SSE 连接超时时间（毫秒）：30分钟
    SSE_TIMEOUT_MS = 30 * 60 * 1000
    
    # SSE 重连时间（毫秒）：3秒
    SSE_RECONNECT_TIME_MS = 3000
    
    # Pexels API 地址
    PEXELS_API_URL = "https://api.pexels.com/v1/search"
    
    # Pexels 每页返回数量
    PEXELS_PER_PAGE = 1
    
    # Pexels 图片方向：横向
    PEXELS_ORIENTATION_LANDSCAPE = "landscape"
    
    # Picsum 随机图片 URL 模板
    PICSUM_URL_TEMPLATE = "https://picsum.photos/800/600?random={}"
    
    # Bing 图片搜索地址（第 5 期新增）
    BING_IMAGE_SEARCH_URL = "https://cn.bing.com/images/async"
    
    # 表情包关键词后缀（程序固定拼接）
    EMOJI_PACK_SUFFIX = "表情包"
    
    # Bing 图片搜索每批最大数量
    BING_MAX_IMAGES = 30
    
    # SVG 文件前缀
    SVG_FILE_PREFIX = "svg-chart"
    
    # SVG 默认宽度
    SVG_DEFAULT_WIDTH = 800
    
    # SVG 默认高度
    SVG_DEFAULT_HEIGHT = 600
