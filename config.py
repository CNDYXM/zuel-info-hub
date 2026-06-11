"""ZUEL 信息聚合 - 配置文件"""

# 数据刷新间隔（分钟）
SCHEDULE_INTERVALS = {
    "morning": "08:00",
    "noon": "12:00",
    "evening": "20:00",
}

# 监听端口
PORT = 5000

# 信息来源站点配置
# 每个站点配置：名称、分类、首页URL、列表选择器、标题/链接/日期提取规则
SOURCES = [
    # ── 校级核心 ──
    {"name": "文澜新闻网", "category": "综合新闻", "url": "https://wellan.zuel.edu.cn"},
    {"name": "学校官网", "category": "综合新闻", "url": "https://www.zuel.edu.cn"},
    {"name": "教务部", "category": "通知公告", "url": "https://jwc.zuel.edu.cn"},
    {"name": "研究生院", "category": "通知公告", "url": "https://yjsy.zuel.edu.cn"},
    # ── 各学院 ──
    {"name": "知识产权学院", "category": "通知公告", "url": "https://ipschool.zuel.edu.cn"},
    {"name": "法学院", "category": "通知公告", "url": "https://law.zuel.edu.cn"},
    {"name": "会计学院", "category": "通知公告", "url": "https://kjxy.zuel.edu.cn"},
    {"name": "金融学院", "category": "通知公告", "url": "https://finance.zuel.edu.cn"},
    {"name": "工商管理学院", "category": "通知公告", "url": "https://gsxy.zuel.edu.cn"},
    {"name": "经济学院", "category": "通知公告", "url": "https://jjxy.zuel.edu.cn"},
    {"name": "公共管理学院", "category": "通知公告", "url": "https://ggglxy.zuel.edu.cn"},
    {"name": "统计与数学学院", "category": "通知公告", "url": "https://tsxy.zuel.edu.cn"},
    {"name": "信息工程学院", "category": "通知公告", "url": "https://xagx.zuel.edu.cn"},
    {"name": "外国语学院", "category": "通知公告", "url": "https://wgyxy.zuel.edu.cn"},
    {"name": "新闻与文化传播学院", "category": "通知公告", "url": "https://xwcb.zuel.edu.cn"},
    {"name": "哲学院", "category": "通知公告", "url": "https://zxy.zuel.edu.cn"},
    {"name": "马克思主义学院", "category": "通知公告", "url": "https://mkszyxy.zuel.edu.cn"},
    {"name": "刑事司法学院", "category": "通知公告", "url": "https://cjs.zuel.edu.cn"},
    {"name": "中韩新媒体学院", "category": "通知公告", "url": "https://zhxmt.zuel.edu.cn"},
    {"name": "文澜学院", "category": "通知公告", "url": "https://wls.zuel.edu.cn"},
    # ── 其他部门 ──
    {"name": "体育部", "category": "通知公告", "url": "https://tyb.zuel.edu.cn"},
    {"name": "创业学院", "category": "通知公告", "url": "https://cyxy.zuel.edu.cn"},
    {"name": "学生资助管理中心", "category": "通知公告", "url": "https://xszz.zuel.edu.cn"},
    {"name": "心理咨询中心", "category": "通知公告", "url": "https://xlzx.zuel.edu.cn"},
]

# 分类显示名称映射（以知识产权学院分类体系为基准）
CATEGORY_NAMES = {
    "综合新闻": "🏛️ 综合新闻",
    "通知公告": "📋 通知公告",
    "教科动态": "📖 教科动态",
    "讲座预告": "🎤 讲座预告",
    "师生远方": "👤 学子风采",
    "党建工作": "🚩 党建工作",
    "规章制度": "📜 规章制度",
    "就业招聘": "💼 就业招聘",
    "志愿服务": "❤️ 志愿服务",
}

# 按站点 + URL cID 编码的精准分类（优先级最高）
SITE_CAT_MAP = {
    "知识产权学院": {
        "17084": "通知公告", "17083": "综合新闻", "17080": "师生远方",
        "17078": "党建工作", "17077": "教科动态",
        "17596": "讲座预告", "17473": "规章制度",
    },
    "法学院": {
        "16280": "综合新闻", "16281": "通知公告", "16305": "讲座预告",
        "16263": "党建工作", "16259": "教科动态",
        "16266": "师生远方", "16267": "师生远方", "16268": "师生远方",
    },
}

# 自动分类关键词（按优先级从高到低）
# 无法匹配的默认归入"通知公告"
CLASSIFY_RULES = [
    ("志愿服务", ["志愿", "志协", "义工", "公益", "献血", "支教", "志愿者"]),
    ("讲座预告", ["讲座", "沙龙", "讲坛", "论坛", "学术报告", "报告会", "公开课"]),
    ("就业招聘", ["招聘", "就业", "宣讲会", "双选", "实习", "求职", "简历", "面试"]),
    ("教科动态", ["教学", "教科", "课程", "教材", "选课", "考试", "成绩", "培养方案", "实践教学"]),
    ("党建工作", ["党建", "党委", "支部", "党员", "组织", "巡察", "联学"]),
    ("规章制度", ["规章", "制度", "办法", "规定", "条例", "准则", "细则"]),
    ("师生远方", ["学子", "学生风采", "风采", "优秀", "榜样", "表彰", "毕业"]),
    ("综合新闻", ["召开", "举行", "举办", "开展", "推进", "签约", "揭牌", "考察", "访问", "交流", "合作", "庆祝", "纪念", "会议"]),
    ("通知公告", ["通知", "公示", "公告", "通报", "决定", "征集", "声明", "提醒", "须知", "报送", "截止"]),
]
