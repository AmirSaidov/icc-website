"""
Тестовые данные для `python manage.py seed` (SPEC.md, 5.4).

Переводимые значения — кортежи (ru, en, zh). zh = None — записи без китайского
перевода (проверка is_translated: false). Все организации, адреса и телефоны вымышлены.
"""

LOREM = (
    "<p>Центр промышленной кооперации помогает предприятиям Кыргызстана находить партнёров, "
    "выходить на новые рынки и развивать совместные производства.</p>",
    "<p>The Industrial Cooperation Centre helps Kyrgyz companies find partners, enter new "
    "markets and develop joint production.</p>",
    "<p>工业合作中心帮助吉尔吉斯斯坦企业寻找合作伙伴、开拓新市场并发展合资生产。</p>",
)

SYSTEM_PAGES = {
    "home": {
        "title": ("Главная", "Home", "首页"),
        "content": ("", "", ""),
        "meta_title": (
            "Центр промышленной кооперации при ТПП КР",
            "Industrial Cooperation Centre at the CCI of the Kyrgyz Republic",
            "吉尔吉斯共和国工商会工业合作中心",
        ),
        "meta_description": (
            "Поиск партнёров, деловые миссии и промышленная кооперация с Китаем и другими странами.",
            "Partner search, business missions and industrial cooperation with China and other countries.",
            "寻找合作伙伴、商务考察以及与中国和其他国家的工业合作。",
        ),
        "show_in_menu": False,
    },
    "about": {
        "title": ("О Центре", "About the Centre", "关于中心"),
        "content": (
            "<h2>Кто мы</h2>" + LOREM[0] + "<p>Центр работает при Торгово-промышленной палате "
            "Кыргызской Республики.</p>",
            "<h2>Who we are</h2>" + LOREM[1] + "<p>The Centre operates under the Chamber of "
            "Commerce and Industry of the Kyrgyz Republic.</p>",
            "<h2>我们是谁</h2>" + LOREM[2] + "<p>中心隶属于吉尔吉斯共和国工商会。</p>",
        ),
        "show_in_menu": True,
    },
    "cooperation": {
        "title": ("Сотрудничество", "Cooperation", "合作"),
        "content": (
            "<h2>Международное сотрудничество</h2><p>Проекты с партнёрами из Китая и стран региона.</p>",
            "<h2>International cooperation</h2><p>Projects with partners from China and the region.</p>",
            "<h2>国际合作</h2><p>与中国及本地区国家合作伙伴的项目。</p>",
        ),
        "show_in_menu": True,
    },
}

CONTACTS = {
    "official_name": (
        "Центр промышленной кооперации при Торгово-промышленной палате Кыргызской Республики",
        "Industrial Cooperation Centre at the Chamber of Commerce and Industry of the Kyrgyz Republic",
        "吉尔吉斯共和国工商会工业合作中心",
    ),
    "address": (
        "720000, г. Бишкек, ул. Примерная, 1 (тестовый адрес)",
        "1 Primernaya St., Bishkek 720000 (test address)",
        "比什凯克市示例街1号，720000（测试地址）",
    ),
    "work_hours": ("Пн–Пт, 9:00–18:00", "Mon–Fri, 9:00–18:00", "周一至周五 9:00–18:00"),
    "phones": [
        {"label_ru": "Приёмная", "label_en": "Reception", "label_zh": "接待处", "number": "+996 312 000 000"},
        {
            "label_ru": "Отдел кооперации",
            "label_en": "Cooperation department",
            "label_zh": "合作部",
            "number": "+996 312 000 001",
        },
    ],
    "email": "info@example.kg",
    "map_lat": "42.874600",
    "map_lng": "74.612200",
    "socials": [
        {"type": "telegram", "url": "https://t.me/example"},
        {"type": "facebook", "url": "https://facebook.com/example"},
    ],
}

HOME_BLOCKS = [
    {
        "type": "hero",
        "title": ("Центр промышленной кооперации", "Industrial Cooperation Centre", "工业合作中心"),
        "text": (
            "Помогаем предприятиям Кыргызстана находить партнёров за рубежом",
            "We help Kyrgyz companies find partners abroad",
            "帮助吉尔吉斯斯坦企业寻找海外合作伙伴",
        ),
        "button_text": ("Наши услуги", "Our services", "我们的服务"),
        "button_link": "/services",
        "image": True,
    },
    {
        "type": "about",
        "title": ("О Центре", "About the Centre", "关于中心"),
        "text": (
            "Центр создан при Торгово-промышленной палате для развития промышленной кооперации.",
            "The Centre was established at the Chamber of Commerce to develop industrial cooperation.",
            "中心由工商会设立，旨在发展工业合作。",
        ),
        "button_text": ("Подробнее", "Learn more", "了解更多"),
        "button_link": "/about",
        "image": True,
    },
    {
        "type": "advantages",
        "title": ("Почему мы", "Why us", "我们的优势"),
        "text": (
            "Проверенные партнёры, сопровождение сделок, поддержка на трёх языках.",
            "Verified partners, deal support, assistance in three languages.",
            "可靠的合作伙伴、交易全程支持、三种语言服务。",
        ),
        "button_text": ("", "", ""),
        "button_link": "",
        "image": False,
    },
    {
        "type": "kg_china",
        "title": ("Кыргызстан — Китай", "Kyrgyzstan — China", "吉尔吉斯斯坦—中国"),
        "text": (
            "Особое направление работы — кооперация с предприятиями Китая.",
            "A special focus of our work is cooperation with Chinese enterprises.",
            "我们工作的重点之一是与中国企业合作。",
        ),
        "button_text": ("Сотрудничество", "Cooperation", "合作"),
        "button_link": "/cooperation",
        "image": True,
    },
    {
        "type": "cta",
        "title": ("Станьте партнёром", "Become a partner", "成为合作伙伴"),
        "text": (
            "Оставьте заявку — мы подберём партнёров под вашу задачу.",
            "Leave a request and we will find partners for your project.",
            "提交申请，我们将为您匹配合适的合作伙伴。",
        ),
        "button_text": ("Оставить заявку", "Send a request", "提交申请"),
        "button_link": "/contacts",
        "image": False,
    },
]

DIRECTIONS = [
    ("cooperation", ("Промышленная кооперация", "Industrial cooperation", "工业合作"),
     ("Связываем производителей для совместной работы.", "We connect manufacturers to work together.",
      "连接制造商开展合作。")),
    ("partnership", ("Поиск партнёров", "Partner search", "寻找合作伙伴"),
     ("Подбираем надёжных партнёров за рубежом.", "We find reliable partners abroad.",
      "为您寻找可靠的海外合作伙伴。")),
    ("joint-production", ("Совместные производства", "Joint production", "合资生产"),
     ("Помогаем запускать совместные предприятия.", "We help launch joint ventures.",
      "协助建立合资企业。")),
    ("localization", ("Локализация производства", "Production localization", "生产本地化"),
     ("Содействуем переносу производств в Кыргызстан.", "We support relocating production to Kyrgyzstan.",
      "协助将生产转移到吉尔吉斯斯坦。")),
    ("subcontracting", ("Субконтрактация", "Subcontracting", "分包合作"),
     ("Находим исполнителей для производственных заказов.", "We find contractors for production orders.",
      "为生产订单寻找承包商。")),
    ("consulting", ("Консалтинг", "Consulting", "咨询服务"),
     ("Консультируем по выходу на зарубежные рынки.", "We advise on entering foreign markets.",
      "为进入国外市场提供咨询。")),
    ("b2b-meetings", ("B2B-встречи", "B2B meetings", "B2B洽谈"),
     ("Организуем переговоры с потенциальными партнёрами.", "We organise talks with potential partners.",
      "组织与潜在合作伙伴的洽谈。")),
    ("export", ("Содействие экспорту", "Export promotion", "出口促进"),
     ("Помогаем выводить продукцию на экспорт.", "We help bring products to export markets.",
      "帮助产品进入出口市场。")),
]

SERVICES = [
    (("Подбор партнёров в Китае", "Partner search in China", "在中国寻找合作伙伴"),
     ("Поиск и проверка производителей и поставщиков.", "Finding and vetting manufacturers and suppliers.",
      "寻找并核实制造商和供应商。")),
    (("Организация деловых миссий", "Business mission organization", "组织商务考察"),
     ("Программа визитов, встречи, сопровождение.", "Visit programme, meetings and support.",
      "考察日程、会议安排和全程陪同。")),
    (("Проведение B2B-переговоров", "B2B negotiations", "组织B2B谈判"),
     ("Подготовка и модерация переговоров.", "Preparing and moderating negotiations.",
      "谈判的准备与主持。")),
    (("Проверка контрагентов", "Counterparty due diligence", "合作方资信调查"),
     ("Проверка репутации и документов партнёра.", "Checking a partner's reputation and documents.",
      "核查合作方的信誉和文件。")),
    (("Консультации по локализации", "Localization consulting", "本地化咨询"),
     ("Расчёт и сопровождение проектов локализации.", "Planning and supporting localization projects.",
      "本地化项目的测算与支持。")),
    (("Сопровождение экспортных контрактов", "Export contract support", "出口合同支持"),
     ("Помощь на всех этапах экспортной сделки.", "Assistance at every stage of an export deal.",
      "在出口交易各阶段提供协助。")),
    # Без китайского перевода — для проверки is_translated: false
    (("Перевод деловой документации", "Business document translation", None),
     ("Перевод договоров и презентаций.", "Translating contracts and presentations.", None)),
]

NEWS_CATEGORIES = [
    ("center", ("Новости Центра", "Centre news", "中心新闻")),
    ("missions", ("Деловые миссии", "Business missions", "商务考察")),
    ("partnership", ("Партнёрство", "Partnership", "合作伙伴关系")),
]

# (категория, дней назад, заголовок, анонс)
NEWS = [
    ("missions", 2, ("Деловая миссия в Урумчи", "Business mission to Urumqi", "乌鲁木齐商务考察"),
     ("Предприниматели Кыргызстана провели переговоры с компаниями Синьцзяна.",
      "Kyrgyz entrepreneurs held talks with companies from Xinjiang.",
      "吉尔吉斯斯坦企业家与新疆企业进行了洽谈。")),
    ("partnership", 6,
     ("Центр подписал меморандум с торговой палатой Синьцзяна",
      "The Centre signed a memorandum with the Xinjiang Chamber of Commerce",
      "中心与新疆商会签署合作备忘录"),
     ("Стороны договорились о совместной работе по поиску партнёров.",
      "The parties agreed to work together on partner search.",
      "双方同意在寻找合作伙伴方面开展合作。")),
    ("center", 10,
     ("Итоги B2B-сессии с производителями Казахстана",
      "Results of the B2B session with Kazakh manufacturers",
      "与哈萨克斯坦制造商B2B洽谈会成果"),
     ("Проведено более 40 встреч, подписано 5 соглашений.",
      "More than 40 meetings were held and 5 agreements signed.",
      "共举行40多场会谈，签署5项协议。")),
    ("missions", 15,
     ("Открыт приём заявок на выставку в Гуанчжоу",
      "Applications open for the Guangzhou exhibition",
      "广州展览会开始接受报名"),
     ("Центр формирует делегацию кыргызстанских компаний.",
      "The Centre is forming a delegation of Kyrgyz companies.",
      "中心正在组建吉尔吉斯斯坦企业代表团。")),
    ("center", 21, ("Семинар по локализации производства", "Seminar on production localization", "生产本地化研讨会"),
     ("Эксперты рассказали о мерах поддержки локализации.",
      "Experts presented support measures for localization.",
      "专家介绍了支持本地化的措施。")),
    ("partnership", 28,
     ("Новый партнёр в сфере сельхозтехники", "New partner in agricultural machinery", "农业机械领域新合作伙伴"),
     ("К сети партнёров Центра присоединилась компания из Китая.",
      "A company from China has joined the Centre's partner network.",
      "一家中国企业加入了中心的合作伙伴网络。")),
    ("missions", 35,
     ("Делегация провинции Шэньси посетила Бишкек", "Shaanxi delegation visited Bishkek", "陕西省代表团访问比什凯克"),
     ("Обсуждались проекты в лёгкой промышленности.",
      "Projects in light industry were discussed.",
      "双方讨论了轻工业领域的项目。")),
    ("center", 42,
     ("Центр запустил реестр запросов на кооперацию",
      "The Centre launched a register of cooperation requests",
      "中心推出合作需求登记"),
     ("Предприятия могут оставить запрос на поиск партнёра.",
      "Companies can submit a partner search request.",
      "企业可以提交寻找合作伙伴的需求。")),
    ("center", 50, ("Круглый стол по экспорту в Китай", "Round table on exports to China", "对华出口圆桌会议"),
     ("Участники обсудили требования китайского рынка.",
      "Participants discussed the requirements of the Chinese market.",
      "与会者讨论了中国市场的要求。")),
    ("center", 60, ("Подведены итоги первого полугодия", "First half-year results", "上半年工作总结"),
     ("Центр провёл 12 мероприятий и 150 B2B-встреч.",
      "The Centre held 12 events and 150 B2B meetings.",
      "中心举办了12场活动和150场B2B洽谈。")),
    # Без китайского перевода — для проверки is_translated: false
    ("center", 70, ("Встреча с предпринимателями Оша", "Meeting with Osh entrepreneurs", None),
     ("Обсудили участие компаний юга страны в программах Центра.",
      "Participation of southern companies in the Centre's programmes was discussed.", None)),
    ("partnership", 80,
     ("Соглашение о совместном производстве стройматериалов",
      "Agreement on joint production of building materials",
      "建材合资生产协议签署"),
     ("Проект предусматривает запуск завода в Чуйской области.",
      "The project provides for launching a plant in the Chui region.",
      "该项目计划在楚河州建设工厂。")),
]

LOCATIONS = {
    "urumqi": ("Урумчи", "Urumqi", "乌鲁木齐"),
    "bishkek": ("Бишкек", "Bishkek", "比什凯克"),
    "almaty": ("Алматы", "Almaty", "阿拉木图"),
    "online": ("Онлайн", "Online", "线上"),
    "guangzhou": ("Гуанчжоу", "Guangzhou", "广州"),
}

# (тип, начало: дней от сегодня, длительность в днях или None, место, заголовок, анонс)
EVENTS = [
    ("mission", -60, 3, "urumqi",
     ("Бизнес-миссия в Синьцзян", "Business mission to Xinjiang", "新疆商务考察团"),
     ("Визиты на предприятия и переговоры.", "Company visits and negotiations.", "参观企业并进行洽谈。")),
    ("forum", -30, None, "bishkek",
     ("Форум «Кыргызстан — Китай: промышленная кооперация»",
      "Kyrgyzstan–China Industrial Cooperation Forum",
      "吉尔吉斯斯坦—中国工业合作论坛"),
     ("Пленарная сессия и отраслевые секции.", "Plenary session and industry panels.", "全体会议和行业分会。")),
    ("exhibition", -20, 2, "bishkek",
     ("Выставка «Сделано в Кыргызстане»", "Made in Kyrgyzstan Exhibition", "吉尔吉斯斯坦制造展"),
     ("Продукция местных производителей.", "Products of local manufacturers.", "本地制造商产品展示。")),
    ("b2b", -10, None, "almaty",
     ("B2B-встречи с компаниями Казахстана", "B2B meetings with Kazakh companies", "与哈萨克斯坦企业B2B洽谈"),
     ("Переговоры по поставкам и кооперации.", "Talks on supplies and cooperation.", "关于供货与合作的洽谈。")),
    ("other", 7, None, "online",
     ("Вебинар по экспортным процедурам", "Webinar on export procedures", "出口程序网络研讨会"),
     ("Таможня, сертификация, логистика.", "Customs, certification, logistics.", "海关、认证与物流。")),
    ("mission", 20, 5, "guangzhou",
     ("Бизнес-миссия в Гуанчжоу", "Business mission to Guangzhou", "广州商务考察团"),
     ("Участие в выставке и деловые встречи.", "Exhibition participation and business meetings.",
      "参加展览会并举行商务会谈。")),
    ("forum", 45, 1, "bishkek",
     ("Инвестиционный форум в Бишкеке", "Bishkek Investment Forum", "比什凯克投资论坛"),
     ("Презентация инвестиционных проектов.", "Presentation of investment projects.", "投资项目推介。")),
    ("b2b", 75, None, "bishkek",
     ("B2B-сессия по субконтрактации", "Subcontracting B2B session", "分包合作B2B洽谈会"),
     ("Встречи заказчиков и исполнителей.", "Meetings of customers and contractors.", "采购方与承包商会面。")),
]

COUNTRIES = [
    ("CN", ("Китай", "China", "中国"),
     ("Ключевой партнёр Кыргызстана в промышленной кооперации.",
      "Kyrgyzstan's key partner in industrial cooperation.",
      "吉尔吉斯斯坦工业合作的主要伙伴。")),
    ("KZ", ("Казахстан", "Kazakhstan", "哈萨克斯坦"),
     ("Партнёр по Евразийскому экономическому союзу.",
      "Partner in the Eurasian Economic Union.",
      "欧亚经济联盟伙伴。")),
]

# (код страны, согласие на публикацию, сайт, название, описание)
PARTNERS = [
    ("CN", True, "https://example.com/silkroad",
     ("Торговая компания «Шёлковый путь» (демо)", "Silk Road Trading Co. (demo)", "丝路贸易有限公司（演示）"),
     ("Оптовая торговля и логистика.", "Wholesale trade and logistics.", "批发贸易与物流。")),
    ("CN", True, "https://example.com/tianshan",
     ("«Тяньшань Машинери» (демо)", "Tianshan Machinery (demo)", "天山机械（演示）"),
     ("Производство сельхозтехники.", "Agricultural machinery manufacturing.", "农业机械制造。")),
    ("KZ", True, "https://example.com/agro",
     ("ТОО «Алматы Агро Экспорт» (демо)", "Almaty Agro Export LLP (demo)", "阿拉木图农业出口公司（演示）"),
     ("Экспорт сельхозпродукции.", "Export of agricultural products.", "农产品出口。")),
    # Без согласия на публикацию — не должен попадать в API
    ("CN", False, "https://example.com/electronics",
     ("«Шэньчжэнь Электроникс» (демо)", "Shenzhen Electronics (demo)", "深圳电子（演示）"),
     ("Электронные компоненты.", "Electronic components.", "电子元器件。")),
]

# (код страны, дней назад, индексы партнёров, заголовок, анонс)
PROJECTS = [
    ("CN", 10, [0, 1],
     ("Совместное производство стройматериалов в Чуйской области",
      "Joint production of building materials in the Chui region",
      "楚河州建材合资生产"),
     ("Запуск завода мощностью 100 тыс. тонн в год.",
      "Launching a plant with a capacity of 100,000 tonnes per year.",
      "建设年产10万吨的工厂。")),
    ("CN", 40, [1, 3],
     ("Локализация сборки сельхозтехники", "Localization of agricultural machinery assembly", "农业机械组装本地化"),
     ("Сборка тракторов из машинокомплектов.", "Assembling tractors from machine kits.", "用散件组装拖拉机。")),
    ("KZ", 80, [2],
     ("Экспорт сельхозпродукции в Казахстан", "Agricultural exports to Kazakhstan", "向哈萨克斯坦出口农产品"),
     ("Поставки овощей и фруктов по долгосрочным контрактам.",
      "Supplying vegetables and fruit under long-term contracts.",
      "根据长期合同供应蔬菜和水果。")),
]

GALLERY_CAPTIONS = [
    ("Открытие встречи", "Opening of the meeting", "会议开幕"),
    ("Переговоры", "Negotiations", "洽谈"),
    ("Подписание соглашения", "Signing of the agreement", "签署协议"),
]

PROGRAM_TITLE = ("Программа", "Programme", "日程安排")
REGULATIONS_TITLE = ("Положение о Центре", "Regulations of the Centre", "中心章程")

SEED_USERS = [
    # username, группа, superuser
    ("admin", "Администратор", True),
    ("editor", "Редактор", False),
]
