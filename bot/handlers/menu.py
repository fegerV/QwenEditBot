"""Menu handlers - main menu and navigation with 8 main sections"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from ..states import UserState
from ..keyboards import (
    edit_photo_submenu_keyboard,
    category_keyboard,
    main_menu_keyboard,
    main_menu_inline_keyboard,
    back_and_main_menu_keyboard,
    fitting_room_instructions_keyboard,
    profile_menu_keyboard,
    knowledge_base_keyboard,
    artistic_styles_root_keyboard,
    artistic_styles_artists_keyboard,
    artistic_styles_digital_artists_keyboard,
    artistic_styles_techniques_keyboard,
    artistic_styles_comics_keyboard,
    artistic_styles_cartoons_keyboard,
    artistic_styles_anime_keyboard,
    artistic_styles_fantasy_keyboard,
    artistic_styles_photographers_keyboard,
    appearance_gender_keyboard,
    appearance_male_keyboard,
    appearance_male_hairstyle_categories_keyboard,
    appearance_male_short_hairstyles_keyboard,
    appearance_male_medium_hairstyles_keyboard,
    appearance_male_long_hairstyles_keyboard,
    appearance_male_beard_keyboard,
    appearance_male_beard_none_keyboard,
    appearance_male_beard_short_keyboard,
    appearance_male_beard_medium_keyboard,
    appearance_male_beard_long_keyboard,
    appearance_male_mustache_keyboard,
    appearance_female_keyboard,
    appearance_female_hairstyle_categories_keyboard,
    appearance_short_hairstyles_keyboard,
    appearance_medium_hairstyles_keyboard,
    appearance_long_hairstyles_keyboard,
    appearance_bangs_keyboard,
    appearance_updo_keyboard,
    appearance_braids_keyboard,
    appearance_stylistic_keyboard,
)
from ..utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


# Female short hairstyles presets
FEMALE_SHORT_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "h_short_pixie": {
        "name": "Пикси",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a pixie haircut.\n"
            "Short neat hairstyle with clean silhouette.\n"
            "Natural hair texture, realistic density."
        ),
    },
    "h_short_pixie_volume": {
        "name": "Пикси с объёмом",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a pixie haircut with added volume.\n"
            "Lifted roots, airy structure, soft volume."
        ),
    },
    "h_short_bob": {
        "name": "Короткий боб",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short bob haircut.\n"
            "Hair length above the jawline, clean shape."
        ),
    },
    "h_short_french_bob": {
        "name": "Французский боб",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a French bob haircut.\n"
            "Slightly messy, natural, effortless Parisian style."
        ),
    },
    "h_short_garcon": {
        "name": "Гарсон",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a garçon haircut.\n"
            "Very short, minimalistic, elegant shape."
        ),
    },
    "h_short_asymmetric": {
        "name": "Короткая асимметричная",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short asymmetrical haircut.\n"
            "One side slightly longer, modern silhouette."
        ),
    },
    "h_short_textured": {
        "name": "Короткая текстурная",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short textured haircut.\n"
            "Visible layers, light messiness, natural movement."
        ),
    },
    "h_short_elongated": {
        "name": "Короткая с удлинёнными прядями",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short haircut with elongated front strands.\n"
            "Front pieces longer, soft framing."
        ),
    },
    "h_short_crown_volume": {
        "name": "Короткая с объёмом на макушке",
        "icon": "✂️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short haircut with volume on the crown.\n"
            "Lifted crown, balanced proportions."
        ),
    },
}


# Female medium length hairstyles presets
FEMALE_MEDIUM_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "h_medium_classic_bob": {
        "name": "Классический боб",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a classic bob haircut.\n"
            "Even length, clean geometric shape."
        ),
    },
    "h_medium_lob": {
        "name": "Удлинённый боб (LOB)",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a long bob (lob) haircut.\n"
            "Length between chin and shoulders."
        ),
    },
    "h_medium_carre": {
        "name": "Каре",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a carré haircut.\n"
            "Straight shape, clear horizontal line."
        ),
    },
    "h_medium_carre_long": {
        "name": "Каре с удлинением",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a bob haircut with longer front strands.\n"
            "Angled silhouette, modern look."
        ),
    },
    "h_medium_layered": {
        "name": "Средняя длина с слоями",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium-length layered haircut.\n"
            "Soft layers for movement and depth."
        ),
    },
    "h_medium_shoulder": {
        "name": "Волосы до плеч",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply shoulder-length hairstyle.\n"
            "Natural fall, balanced volume."
        ),
    },
    "h_medium_textured": {
        "name": "Текстурная средняя длина",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a textured medium-length haircut.\n"
            "Light layers, natural flow."
        ),
    },
    "h_medium_volume": {
        "name": "Средняя длина с объёмом",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium-length hairstyle with added volume.\n"
            "Lifted roots, airy structure."
        ),
    },
    "h_medium_waves": {
        "name": "Средняя длина с мягкими волнами",
        "icon": "🌊",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium-length hairstyle with soft waves.\n"
            "Natural loose waves, relaxed look."
        ),
    },
}


# Female long hairstyles presets
FEMALE_LONG_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "h_long_straight": {
        "name": "Прямые длинные",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long straight hair.\n"
            "Smooth texture, natural shine."
        ),
    },
    "h_long_wavy": {
        "name": "Волнистые длинные",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long wavy hair.\n"
            "Soft natural waves."
        ),
    },
    "h_long_curly": {
        "name": "Кудрявые длинные",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long curly hair.\n"
            "Defined curls, realistic density."
        ),
    },
    "h_long_layered": {
        "name": "Длинные с слоями",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long layered hairstyle.\n"
            "Visible layers for depth and movement."
        ),
    },
    "h_long_volume": {
        "name": "Длинные с объёмом",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long hairstyle with added volume.\n"
            "Lifted roots, full silhouette."
        ),
    },
    "h_long_sleek": {
        "name": "Гладкие длинные",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply sleek long hair.\n"
            "Smooth polished finish."
        ),
    },
    "h_long_natural": {
        "name": "Натуральная текстура",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long hair with natural texture.\n"
            "Minimal styling, realistic look."
        ),
    },
    "h_long_soft_curls": {
        "name": "Длинные с мягкими локонами",
        "icon": "💁",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long hair with soft curls.\n"
            "Loose curls, elegant movement."
        ),
    },
}


# Female bangs presets (can be added to any hairstyle)
FEMALE_BANGS_PRESETS: dict[str, dict[str, str]] = {
    "h_bangs_straight": {
        "name": "Прямая чёлка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add straight bangs.\n"
            "Even line, natural density."
        ),
    },
    "h_bangs_side_swept": {
        "name": "Косая чёлка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add side-swept bangs.\n"
            "Soft diagonal shape."
        ),
    },
    "h_bangs_curtain": {
        "name": "Чёлка-шторка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add curtain bangs.\n"
            "Split in the center, soft framing."
        ),
    },
    "h_bangs_choppy": {
        "name": "Рваная чёлка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add textured choppy bangs.\n"
            "Uneven ends, light look."
        ),
    },
    "h_bangs_long": {
        "name": "Удлинённая чёлка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add long bangs.\n"
            "Blending naturally into the hairstyle."
        ),
    },
    "h_bangs_airy": {
        "name": "Лёгкая воздушная чёлка",
        "icon": "🪮",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Add airy light bangs.\n"
            "Thin, soft, natural."
        ),
    },
}


# Female updo hairstyles presets
FEMALE_UPDO_PRESETS: dict[str, dict[str, str]] = {
    "h_updo_low_bun": {
        "name": "Низкий пучок",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a low bun hairstyle.\n"
            "Clean, elegant shape."
        ),
    },
    "h_updo_high_bun": {
        "name": "Высокий пучок",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a high bun hairstyle.\n"
            "Lifted, neat structure."
        ),
    },
    "h_updo_low_ponytail": {
        "name": "Низкий хвост",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a low ponytail.\n"
            "Relaxed and natural."
        ),
    },
    "h_updo_high_ponytail": {
        "name": "Высокий хвост",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a high ponytail.\n"
            "Tight and lifted."
        ),
    },
    "h_updo_slicked_back": {
        "name": "Гладко убранные волосы",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply slicked-back hair.\n"
            "Smooth, polished finish."
        ),
    },
    "h_updo_half_up": {
        "name": "Полусобранные волосы",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply half-up hairstyle.\n"
            "Top section tied, rest loose."
        ),
    },
    "h_updo_bun_with_framing": {
        "name": "Пучок с прядями у лица",
        "icon": "🎀",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a bun with loose face-framing strands.\n"
            "Soft romantic look."
        ),
    },
}


# Female braids presets
FEMALE_BRAIDS_PRESETS: dict[str, dict[str, str]] = {
    "h_braids_classic": {
        "name": "Классическая коса",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a classic braid.\n"
            "Neat and even weaving."
        ),
    },
    "h_braids_french": {
        "name": "Французская коса",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a French braid.\n"
            "Tight weaving from the crown."
        ),
    },
    "h_braids_dutch": {
        "name": "Голландская коса",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a Dutch braid.\n"
            "Raised braid with inverted weaving."
        ),
    },
    "h_braids_fishtail": {
        "name": "Рыбий хвост",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a fishtail braid.\n"
            "Detailed fine weaving."
        ),
    },
    "h_braids_crown": {
        "name": "Коса вокруг головы",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a crown braid.\n"
            "Wrapped around the head."
        ),
    },
    "h_braids_two": {
        "name": "Две косы",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply two braids.\n"
            "Symmetrical and neat."
        ),
    },
    "h_braids_loose_messy": {
        "name": "Свободная небрежная коса",
        "icon": "🧵",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a loose messy braid.\n"
            "Soft, relaxed texture."
        ),
    },
}


# Styling and mood presets (stylistic directions)
FEMALE_STYLISTIC_PRESETS: dict[str, dict[str, str]] = {
    "h_style_natural": {
        "name": "Натуральный стиль",
        "icon": "🌿",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply a natural hairstyle styling.\n"
            "Minimal styling, natural texture.\n"
            "Slight imperfections allowed.\n"
            "Soft volume, realistic look."
        ),
    },
    "h_style_minimalism": {
        "name": "Минимализм",
        "icon": "▫️",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply a minimalist hairstyle styling.\n"
            "Clean lines, restrained volume.\n"
            "No excessive texture or decoration.\n"
            "Simple and modern look."
        ),
    },
    "h_style_romantic": {
        "name": "Романтический стиль",
        "icon": "💕",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply a romantic hairstyle styling.\n"
            "Soft texture, gentle movement.\n"
            "Light waves or softness around the face.\n"
            "Delicate and airy mood."
        ),
    },
    "h_style_elegant": {
        "name": "Элегантный стиль",
        "icon": "👑",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply an elegant hairstyle styling.\n"
            "Polished finish, controlled volume.\n"
            "Refined and sophisticated look."
        ),
    },
    "h_style_boho": {
        "name": "Бохо",
        "icon": "🌾",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply boho hairstyle styling.\n"
            "Relaxed texture, natural flow.\n"
            "Slight messiness, effortless look."
        ),
    },
    "h_style_glamour": {
        "name": "Гламур",
        "icon": "💎",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply glamorous hairstyle styling.\n"
            "Glossy finish, enhanced volume.\n"
            "Well-defined shape, polished look."
        ),
    },
    "h_style_retro": {
        "name": "Ретро",
        "icon": "🕰",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply retro hairstyle styling.\n"
            "Inspired by classic vintage aesthetics.\n"
            "Structured waves or classic forms."
        ),
    },
    "h_style_modern": {
        "name": "Современный",
        "icon": "⚡",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply modern hairstyle styling.\n"
            "Trendy texture, contemporary presentation.\n"
            "Balanced volume and clean finish."
        ),
    },
    "h_style_editorial": {
        "name": "Модный editorial",
        "icon": "📰",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Do NOT change the hairstyle structure, length or haircut shape.\n"
            "Apply only styling, mood and finishing details.\n"
            "Photorealistic result.\n"
            "Apply editorial hairstyle styling.\n"
            "High-fashion look.\n"
            "Slight exaggeration allowed.\n"
            "Clean but expressive styling."
        ),
    },
}


# Male short hairstyles presets
MALE_SHORT_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "m_short_buzz_cut": {
        "name": "Buzz cut",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's buzz cut haircut.\n"
            "Very short uniform length.\n"
            "Clean and minimal look."
        ),
    },
    "m_short_crew_cut": {
        "name": "Crew cut",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's crew cut haircut.\n"
            "Short sides and back, slightly longer top.\n"
            "Neat and balanced proportions."
        ),
    },
    "m_short_crop": {
        "name": "Short crop",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's short crop haircut.\n"
            "Short textured top, clean sides.\n"
            "Modern and practical look."
        ),
    },
    "m_short_caesar": {
        "name": "Caesar",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's Caesar haircut.\n"
            "Short straight fringe, uniform length.\n"
            "Classic structured shape."
        ),
    },
    "m_short_military": {
        "name": "Military cut",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's military haircut.\n"
            "Very short sides and back, minimal top length.\n"
            "Strict and clean appearance."
        ),
    },
    "m_short_high_tight": {
        "name": "High and tight",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's high and tight haircut.\n"
            "Extremely short sides, compact top.\n"
            "Sharp contrast, clean finish."
        ),
    },
    "m_short_textured": {
        "name": "Textured short",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a very short textured men's haircut.\n"
            "Subtle texture on top, clean sides.\n"
            "Natural realistic finish."
        ),
    },
}


# Male medium length hairstyles presets
MALE_MEDIUM_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "m_medium_short_sides_medium_top": {
        "name": "Short sides, medium top",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's haircut with short sides and medium length top.\n"
            "Balanced proportions.\n"
            "Classic versatile style."
        ),
    },
    "m_medium_textured_crop": {
        "name": "Textured crop",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a textured crop men's haircut.\n"
            "Medium length top with visible texture.\n"
            "Natural and modern look."
        ),
    },
    "m_medium_side_part": {
        "name": "Side part",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's haircut with a clear side part.\n"
            "Medium length top, tidy sides.\n"
            "Clean and professional appearance."
        ),
    },
    "m_medium_ivy_league": {
        "name": "Ivy League",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a men's Ivy League haircut.\n"
            "Neat medium top, tapered sides.\n"
            "Classic academic style."
        ),
    },
    "m_medium_natural": {
        "name": "Natural medium",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a natural medium length men's haircut.\n"
            "Relaxed shape, natural flow.\n"
            "Minimal styling."
        ),
    },
    "m_medium_layered": {
        "name": "Layered medium",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a layered medium length men's haircut.\n"
            "Visible layers for movement and depth.\n"
            "Natural texture."
        ),
    },
    "m_medium_messy": {
        "name": "Messy medium",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply a slightly messy medium length men's haircut.\n"
            "Casual texture, effortless look."
        ),
    },
}


# Male long hairstyles presets
MALE_LONG_HAIRSTYLES_PRESETS: dict[str, dict[str, str]] = {
    "m_long_straight": {
        "name": "Long straight",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long straight men's hair.\n"
            "Smooth natural flow.\n"
            "Even length."
        ),
    },
    "m_long_wavy": {
        "name": "Long wavy",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long wavy men's hair.\n"
            "Soft natural waves.\n"
            "Relaxed shape."
        ),
    },
    "m_long_curly": {
        "name": "Long curly",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply long curly men's hair.\n"
            "Defined natural curls.\n"
            "Balanced volume."
        ),
    },
    "m_long_layered": {
        "name": "Layered long",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply layered long men's hair.\n"
            "Visible layers for depth and movement."
        ),
    },
    "m_long_natural": {
        "name": "Natural long",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply natural long men's hair.\n"
            "Minimal styling.\n"
            "Realistic texture."
        ),
    },
    "m_long_shoulder_length": {
        "name": "Shoulder-length",
        "icon": "💈",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change the hairstyle.\n"
            "Maintain realistic hair texture, volume and proportions.\n"
            "Photorealistic result.\n"
            "Apply shoulder-length men's hair.\n"
            "Balanced length and natural fall."
        ),
    },
}


# Male beard and mustache presets - comprehensive version
MALE_BEARD_NO_BEARD_PRESETS: dict[str, dict[str, str]] = {
    "m_beard_clean_shave": {
        "name": "Clean shave (гладко выбрит)",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a clean shaved look.\n"
            "Completely remove beard and mustache.\n"
            "Smooth natural skin appearance."
        ),
    },
    "m_beard_light_stubble": {
        "name": "Light stubble (лёгкая щетина)",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply light stubble.\n"
            "Very short even facial hair.\n"
            "Natural subtle texture."
        ),
    },
    "m_beard_designer_stubble": {
        "name": "Designer stubble (аккуратная щетина)",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply designer stubble.\n"
            "Short well-groomed facial hair.\n"
            "Clean edges and neat appearance."
        ),
    },
}

MALE_BEARD_SHORT_PRESETS: dict[str, dict[str, str]] = {
    "m_beard_short_boxed": {
        "name": "Short boxed beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short boxed beard.\n"
            "Short even length.\n"
            "Clean defined lines on cheeks and jaw."
        ),
    },
    "m_beard_corporate": {
        "name": "Corporate beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a corporate beard.\n"
            "Short tidy beard suitable for business style.\n"
            "Well-defined contours."
        ),
    },
    "m_beard_short_full": {
        "name": "Short full beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short full beard.\n"
            "Even length across cheeks, jaw and chin.\n"
            "Natural density."
        ),
    },
    "m_beard_tapered_short": {
        "name": "Tapered short beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a tapered short beard.\n"
            "Gradual transition from cheeks to jaw.\n"
            "Clean professional look."
        ),
    },
    "m_beard_short_with_fade": {
        "name": "Short beard with fade",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a short beard with fade.\n"
            "Smooth transition from beard into haircut.\n"
            "Natural blend."
        ),
    },
}

MALE_BEARD_MEDIUM_PRESETS: dict[str, dict[str, str]] = {
    "m_beard_medium_full": {
        "name": "Medium full beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium full beard.\n"
            "Balanced length and volume.\n"
            "Natural realistic texture."
        ),
    },
    "m_beard_medium_boxed": {
        "name": "Medium boxed beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium boxed beard.\n"
            "Structured shape with defined lines.\n"
            "Controlled volume."
        ),
    },
    "m_beard_rounded": {
        "name": "Rounded beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a rounded beard shape.\n"
            "Soft contours.\n"
            "Natural edges."
        ),
    },
    "m_beard_natural_medium": {
        "name": "Natural medium beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a natural medium beard.\n"
            "Slightly uneven realistic growth.\n"
            "Relaxed appearance."
        ),
    },
    "m_beard_medium_with_fade": {
        "name": "Medium beard with fade",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a medium beard with fade.\n"
            "Smooth blending into haircut.\n"
            "Clean cheek lines."
        ),
    },
}

MALE_BEARD_LONG_PRESETS: dict[str, dict[str, str]] = {
    "m_beard_long_full": {
        "name": "Long full beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a long full beard.\n"
            "Full coverage with natural length.\n"
            "Realistic flow and density."
        ),
    },
    "m_beard_long_natural": {
        "name": "Long natural beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a long natural beard.\n"
            "Minimal shaping.\n"
            "Authentic uneven texture."
        ),
    },
    "m_beard_viking": {
        "name": "Viking beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a Viking-style beard.\n"
            "Long thick beard with rugged texture.\n"
            "Powerful masculine look."
        ),
    },
    "m_beard_garibaldi": {
        "name": "Garibaldi beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a Garibaldi beard.\n"
            "Wide rounded bottom.\n"
            "Natural fullness."
        ),
    },
    "m_beard_ducktail": {
        "name": "Ducktail beard",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a ducktail beard.\n"
            "Tapered shape toward the chin.\n"
            "Defined jawline."
        ),
    },
}

MALE_MUSTACHE_PRESETS: dict[str, dict[str, str]] = {
    "m_mustache_none": {
        "name": "No mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Remove mustache completely."
        ),
    },
    "m_mustache_classic": {
        "name": "Classic mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a classic mustache.\n"
            "Natural thickness.\n"
            "Clean shape."
        ),
    },
    "m_mustache_chevron": {
        "name": "Chevron mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a chevron mustache.\n"
            "Thick mustache covering the upper lip.\n"
            "Classic masculine style."
        ),
    },
    "m_mustache_natural": {
        "name": "Natural mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a natural mustache.\n"
            "Soft edges and realistic density."
        ),
    },
    "m_mustache_handlebar": {
        "name": "Handlebar mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a handlebar mustache.\n"
            "Curled ends.\n"
            "Styled yet realistic."
        ),
    },
    "m_mustache_pencil": {
        "name": "Pencil mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a pencil mustache.\n"
            "Thin precise line above the lip.\n"
            "Clean refined look."
        ),
    },
    "m_mustache_english": {
        "name": "English mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply an English mustache.\n"
            "Long ends styled outward.\n"
            "Classic vintage style."
        ),
    },
    "m_mustache_hungarian": {
        "name": "Hungarian mustache",
        "icon": "🧔",
        "price": 30,
        "prompt": (
            "Use the original photo as the primary reference.\n"
            "Preserve the face, facial features, head shape, expression and identity exactly.\n"
            "Do NOT change the face or facial structure.\n"
            "Do NOT change hair color.\n"
            "Only change facial hair.\n"
            "Maintain realistic facial hair density, texture and proportions.\n"
            "Photorealistic result.\n"
            "Apply a Hungarian mustache.\n"
            "Wide thick mustache extending sideways.\n"
            "Bold appearance."
        ),
    },
}


ARTISTIC_STYLE_PRESETS: dict[str, dict[str, str]] = {
    # Classic artists
    "as_style_van_gogh": {
        "name": "Vincent van Gogh",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply the artistic style of Vincent van Gogh,\n"
            "oil painting, expressive swirling brushstrokes,\n"
            "vibrant saturated colors,\n"
            "visible canvas texture.\n"
            "High quality, painterly result."
        ),
    },
    "as_style_monet": {
        "name": "Claude Monet",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply the artistic style of Claude Monet,\n"
            "impressionist painting,\n"
            "soft diffused light,\n"
            "pastel color palette,\n"
            "gentle brushstrokes.\n"
            "High quality, atmospheric result."
        ),
    },
    "as_style_picasso": {
        "name": "Pablo Picasso",
        "icon": "🎨",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "For portraits, loosely preserve facial features.\n"
            "Apply a cubist style inspired by Pablo Picasso,\n"
            "abstract geometric shapes,\n"
            "bold color blocks,\n"
            "fragmented forms.\n"
            "Artistic interpretation, coherent structure."
        ),
    },
    "as_style_dali": {
        "name": "Salvador Dalí",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply the surrealist style inspired by Salvador Dalí,\n"
            "dreamlike atmosphere,\n"
            "distorted reality elements,\n"
            "smooth painterly technique.\n"
            "High quality, surreal but coherent result."
        ),
    },

    # Digital artists
    "as_style_beeple": {
        "name": "Beeple (Mike Winkelmann)",
        "icon": "💻",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply a digital art style inspired by Beeple,\n"
            "futuristic and surreal elements,\n"
            "high-contrast lighting,\n"
            "detailed textures,\n"
            "modern digital aesthetic.\n"
            "High quality digital artwork"
        ),
    },
    "as_style_artgerm": {
        "name": "Artgerm (Stanley Lau)",
        "icon": "💻",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions exactly.\n"
            "Apply the semi-realistic digital art style of Artgerm,\n"
            "smooth painterly shading,\n"
            "clean detailed features,\n"
            "professional illustration quality.\n"
            "High quality, polished result."
        ),
    },
    "as_style_loish": {
        "name": "Loish",
        "icon": "💻",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply a soft colorful illustration style inspired by Loish,\n"
            "smooth gradients,\n"
            "gentle lighting,\n"
            "expressive but simplified forms.\n"
            "High quality illustration."
        ),
    },
    "as_style_ross_tran": {
        "name": "Ross Tran (RossDraws)",
        "icon": "💻",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply a vibrant stylized digital painting style inspired by Ross Tran (RossDraws),\n"
            "dynamic lighting,\n"
            "bold colors,\n"
            "energetic brushwork.\n"
            "High quality digital illustration."
        ),
    },

    # Techniques
    "as_style_tech_oil": {
        "name": "Масляная живопись",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply oil painting technique,\n"
            "rich thick brushstrokes,\n"
            "deep saturated colors,\n"
            "visible canvas texture.\n"
            "High quality painterly result."
        ),
    },
    "as_style_tech_watercolor": {
        "name": "Акварель",
        "icon": "💧",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply watercolor painting technique,\n"
            "soft translucent washes,\n"
            "gentle color bleeding,\n"
            "visible paper texture.\n"
            "Light, atmospheric result."
        ),
    },
    "as_style_tech_pastel": {
        "name": "Пастель",
        "icon": "🖌",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply pastel drawing technique,\n"
            "soft chalk textures,\n"
            "smooth color transitions,\n"
            "matte finish.\n"
            "High quality illustration."
        ),
    },
    "as_style_tech_pencil": {
        "name": "Карандаш",
        "icon": "✏️",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply pencil drawing technique,\n"
            "graphite linework,\n"
            "hand-drawn shading,\n"
            "white paper background.\n"
            "Clean sketch style."
        ),
    },
    "as_style_tech_ink": {
        "name": "Чернила / тушь",
        "icon": "🖋",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply ink drawing technique,\n"
            "bold black lines,\n"
            "high contrast,\n"
            "hand-inked illustration style.\n"
            "Crisp, graphic result."
        ),
    },
    "as_style_tech_digital_painting": {
        "name": "Цифровая живопись",
        "icon": "💻",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply digital painting technique,\n"
            "smooth brushwork,\n"
            "detailed lighting,\n"
            "high-resolution textures.\n"
            "Professional digital artwork."
        ),
    },
    "as_style_tech_concept_art": {
        "name": "Концепт-арт",
        "icon": "🧠",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "Apply concept art technique,\n"
            "cinematic lighting,\n"
            "dramatic atmosphere,\n"
            "detailed forms and environments.\n"
            "Professional illustration quality."
        ),
    },
    "as_style_tech_3d_render": {
        "name": "3D-рендер",
        "icon": "🎮",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply 3D render technique,\n"
            "realistic materials,\n"
            "studio lighting,\n"
            "high detail,\n"
            "photorealistic rendering.\n"
            "Clean, modern 3D result."
        ),
    },
    "as_style_tech_engraving": {
        "name": "Гравюра / офорт",
        "icon": "📰",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply engraving technique,\n"
            "fine linework,\n"
            "cross-hatching,\n"
            "vintage illustration style.\n"
            "High detail monochrome result."
        ),
    },
    "as_style_tech_charcoal": {
        "name": "Уголь",
        "icon": "🪵",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply charcoal drawing technique,\n"
            "rough expressive strokes,\n"
            "deep shadows,\n"
            "textured paper.\n"
            "Dramatic monochrome result."
        ),
    },
    "as_style_tech_markers": {
        "name": "Маркеры",
        "icon": "🖍",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply marker illustration technique,\n"
            "bold saturated colors,\n"
            "visible strokes,\n"
            "graphic illustration style.\n"
            "Clean and vibrant result."
        ),
    },
    "as_style_tech_line_art": {
        "name": "Линейный арт",
        "icon": "📐",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply clean line art technique,\n"
            "precise outlines,\n"
            "minimal shading,\n"
            "illustration style.\n"
            "Sharp and minimal result."
        ),
    },

    # Comics styles
    "as_style_jack_kirby": {
        "name": "💥 Jack Kirby (Classic Marvel)",
        "icon": "💥",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply comic art style inspired by Jack Kirby,\n"
            "bold dynamic lines,\n"
            "powerful anatomy,\n"
            "bright saturated colors,\n"
            "classic Marvel aesthetic.\n"
            "High quality comic illustration."
        ),
    },
    "as_style_frank_miller": {
        "name": "🌑 Frank Miller (Noir / Sin City)",
        "icon": "🌑",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply noir comic style inspired by Frank Miller,\n"
            "high contrast black and white,\n"
            "sharp shadows,\n"
            "minimal color accents.\n"
            "Dramatic graphic illustration."
        ),
    },
    "as_style_moebius": {
        "name": "🌌 Moebius (Jean Giraud)",
        "icon": "🌌",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply comic art style inspired by Moebius (Jean Giraud),\n"
            "clean precise linework,\n"
            "soft pastel colors,\n"
            "surreal and detailed environments.\n"
            "High quality comic illustration."
        ),
    },
    "as_style_jim_lee": {
        "name": "⚡ Jim Lee (Modern DC / Marvel)",
        "icon": "⚡",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply modern comic art style inspired by Jim Lee,\n"
            "sharp detailed linework,\n"
            "dynamic poses,\n"
            "dramatic lighting.\n"
            "High quality comic book illustration."
        ),
    },
    "as_style_alex_ross": {
        "name": "🎨 Alex Ross (Painterly Realism)",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions exactly.\n"
            "Apply painterly comic style inspired by Alex Ross,\n"
            "realistic anatomy,\n"
            "soft dramatic lighting,\n"
            "traditional painted texture.\n"
            "High quality realistic comic artwork."
        ),
    },

    # Cartoons styles
    "as_style_disney_renaissance": {
        "name": "🏰 Disney Renaissance Style",
        "icon": "🏰",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply Disney Renaissance animation style,\n"
            "clean expressive linework,\n"
            "warm vibrant colors,\n"
            "classic hand-drawn animation look.\n"
            "High quality cartoon illustration."
        ),
    },
    "as_style_pixar": {
        "name": "🤖 Pixar Style",
        "icon": "🤖",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply Pixar-style 3D animation look,\n"
            "soft lighting,\n"
            "rounded shapes,\n"
            "detailed textures,\n"
            "friendly expressive character design.\n"
            "High quality stylized 3D render."
        ),
    },
    "as_style_dreamworks": {
        "name": "🐲 DreamWorks Style",
        "icon": "🐲",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply DreamWorks animation style,\n"
            "expressive facial features,\n"
            "dynamic poses,\n"
            "cinematic lighting,\n"
            "stylized proportions.\n"
            "High quality cartoon illustration."
        ),
    },
    "as_style_genndy_tartakovsky": {
        "name": "⚔️ Genndy Tartakovsky",
        "icon": "⚔️",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "Apply animation style inspired by Genndy Tartakovsky,\n"
            "strong silhouettes,\n"
            "minimalistic shapes,\n"
            "flat colors,\n"
            "dramatic contrast.\n"
            "Stylized animated illustration."
        ),
    },
    "as_style_looney_tunes": {
        "name": "🐰 Looney Tunes / Chuck Jones",
        "icon": "🐰",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply classic Looney Tunes cartoon style inspired by Chuck Jones,\n"
            "exaggerated expressions,\n"
            "bold outlines,\n"
            "bright flat colors,\n"
            "playful cartoon proportions.\n"
            "High quality cartoon illustration."
        ),
    },

    # Anime styles
    "as_style_makoto_shinkai": {
        "name": "🌸 Makoto Shinkai Style",
        "icon": "🌸",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity, facial features and proportions.\n"
            "Do not change the pose or expression.\n"
            "Apply anime style inspired by Makoto Shinkai,\n"
            "highly detailed background,\n"
            "cinematic lighting,\n"
            "soft glowing light,\n"
            "realistic anime proportions,\n"
            "vivid colors and atmospheric depth.\n"
            "High quality anime illustration."
        ),
    },
    "as_style_yoshitaka_amano": {
        "name": "🪽 Yoshitaka Amano Style",
        "icon": "🪽",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "For portraits, preserve facial identity in artistic and stylized form.\n"
            "Apply anime illustration style inspired by Yoshitaka Amano,\n"
            "delicate elegant linework,\n"
            "elongated forms,\n"
            "pastel and watercolor tones,\n"
            "ornamental fantasy aesthetics.\n"
            "High quality artistic anime illustration."
        ),
    },
    "as_style_akihiko_yoshida": {
        "name": "⚔️ Akihiko Yoshida Style",
        "icon": "⚔️",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply anime character design style inspired by Akihiko Yoshida,\n"
            "clean expressive lineart,\n"
            "balanced anime proportions,\n"
            "soft shading,\n"
            "fantasy RPG character aesthetics.\n"
            "High quality anime character illustration."
        ),
    },
    "as_style_clamp": {
        "name": "🌙 CLAMP Style",
        "icon": "🌙",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity in stylized anime form.\n"
            "Apply anime style inspired by CLAMP,\n"
            "long slender proportions,\n"
            "large expressive eyes,\n"
            "decorative details,\n"
            "elegant and dramatic anime aesthetics.\n"
            "High quality stylized anime illustration."
        ),
    },
    "as_style_studio_ghibli": {
        "name": "🍃 Studio Ghibli Style (Hayao Miyazaki)",
        "icon": "🍃",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and natural proportions.\n"
            "Do not exaggerate facial features.\n"
            "Apply Studio Ghibli animation style inspired by Hayao Miyazaki,\n"
            "soft hand-drawn look,\n"
            "warm natural colors,\n"
            "gentle lighting,\n"
            "simple expressive character design.\n"
            "High quality anime-style illustration."
        ),
    },

    # Fantasy styles
    "as_style_frank_frazetta": {
        "name": "⚔️ Frank Frazetta",
        "icon": "⚔️",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply epic fantasy painting style inspired by Frank Frazetta,\n"
            "powerful heroic anatomy,\n"
            "dramatic dynamic poses,\n"
            "rich earthy colors,\n"
            "bold expressive brushstrokes,\n"
            "classic heroic fantasy atmosphere.\n"
            "High quality fantasy illustration."
        ),
    },
    "as_style_ralph_mcquarrie": {
        "name": "🚀 Ralph McQuarrie",
        "icon": "🚀",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply fantasy concept art style inspired by Ralph McQuarrie,\n"
            "cinematic lighting,\n"
            "soft painterly brushwork,\n"
            "atmospheric sci-fi fantasy environments,\n"
            "concept art aesthetics.\n"
            "High quality cinematic fantasy artwork."
        ),
    },
    "as_style_greg_rutkowski": {
        "name": "🧙 Greg Rutkowski",
        "icon": "🧙",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply high-fantasy digital painting style inspired by Greg Rutkowski,\n"
            "detailed character design,\n"
            "dramatic lighting,\n"
            "epic fantasy atmosphere,\n"
            "highly detailed textures.\n"
            "High quality fantasy illustration."
        ),
    },
    "as_style_magali_villeneuve": {
        "name": "🪄 Magali Villeneuve",
        "icon": "🪄",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply fantasy illustration style inspired by Magali Villeneuve,\n"
            "elegant character design,\n"
            "soft cinematic lighting,\n"
            "refined painterly details,\n"
            "magical fantasy atmosphere.\n"
            "High quality fantasy artwork."
        ),
    },
    "as_style_brom": {
        "name": "🐉 Brom",
        "icon": "🐉",
        "prompt": (
            "Apply dark fantasy art style inspired by Brom,\n"
            "moody lighting,\n"
            "gothic atmosphere,\n"
            "dark painterly textures."
        ),
    },
    "as_style_wayne_barlowe": {
        "name": "🔥 Wayne Barlowe",
        "icon": "🔥",
        "prompt": (
            "Apply dark fantasy illustration style inspired by Wayne Barlowe,\n"
            "alien demonic forms,\n"
            "otherworldly environments,\n"
            "high detail."
        ),
    },
    "as_style_john_blanche": {
        "name": "🏰 John Blanche",
        "icon": "🏰",
        "prompt": (
            "Apply grimdark fantasy art style inspired by John Blanche,\n"
            "chaotic composition,\n"
            "raw sketchy textures,\n"
            "dark medieval atmosphere."
        ),
    },

    # Photography styles
    "as_style_annie_leibovitz": {
        "name": "📸 Annie Leibovitz",
        "icon": "📸",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Annie Leibovitz,\n"
            "dramatic lighting,\n"
            "carefully composed portrait,\n"
            "moody background,\n"
            "professional studio or location setting.\n"
            "High quality cinematic photograph."
        ),
    },
    "as_style_steve_mccurry": {
        "name": "🌍 Steve McCurry",
        "icon": "🌍",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Steve McCurry,\n"
            "vivid saturated colors,\n"
            "documentary realism,\n"
            "natural lighting,\n"
            "authentic and expressive subjects.\n"
            "High quality realistic photograph."
        ),
    },
    "as_style_peter_lindbergh": {
        "name": "🖤 Peter Lindbergh",
        "icon": "🖤",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Peter Lindbergh,\n"
            "black and white portrait,\n"
            "soft natural lighting,\n"
            "minimalistic background,\n"
            "timeless fashion photography aesthetic.\n"
            "High quality artistic photograph."
        ),
    },
    "as_style_helmut_newton": {
        "name": "⚡ Helmut Newton",
        "icon": "⚡",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Helmut Newton,\n"
            "high contrast black and white,\n"
            "provocative fashion poses,\n"
            "dramatic lighting,\n"
            "strong geometric composition.\n"
            "High quality stylized photograph."
        ),
    },
    "as_style_richard_avedon": {
        "name": "✨ Richard Avedon",
        "icon": "✨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Richard Avedon,\n"
            "clean white background,\n"
            "studio lighting,\n"
            "minimalist composition,\n"
            "sharp detailed facial features.\n"
            "High quality professional portrait."
        ),
    },
    "as_style_mario_testino": {
        "name": "📸 Mario Testino",
        "icon": "📸",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Mario Testino,\n"
            "fashion editorial photography,\n"
            "clean elegant composition,\n"
            "soft professional studio lighting,\n"
            "natural yet polished look,\n"
            "vibrant but balanced colors.\n"
            "High quality fashion photograph."
        ),
    },
    "as_style_sebastiao_salgado": {
        "name": "🌍 Sebastião Salgado",
        "icon": "🌍",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Sebastião Salgado,\n"
            "dramatic black and white photography,\n"
            "high contrast,\n"
            "strong emphasis on texture and emotion,\n"
            "documentary realism,\n"
            "natural lighting.\n"
            "High quality fine art photograph."
        ),
    },
    "as_style_dorothea_lange": {
        "name": "🕊 Dorothea Lange",
        "icon": "🕊",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Dorothea Lange,\n"
            "documentary photography,\n"
            "emotional and human-centered composition,\n"
            "natural lighting,\n"
            "authentic realistic atmosphere,\n"
            "soft tonal contrast.\n"
            "High quality documentary photograph."
        ),
    },
    "as_style_tim_walker": {
        "name": "🎭 Tim Walker",
        "icon": "🎭",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Tim Walker,\n"
            "fantastical fashion photography,\n"
            "surreal and imaginative atmosphere,\n"
            "bold colors,\n"
            "creative set design,\n"
            "cinematic lighting.\n"
            "High quality artistic photograph."
        ),
    },
    "as_style_ansel_adams": {
        "name": "🏔 Ansel Adams",
        "icon": "🏔",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply photographic style inspired by Ansel Adams,\n"
            "black and white photography,\n"
            "high sharpness and clarity,\n"
            "strong tonal range,\n"
            "emphasis on light, shadow and depth,\n"
            "fine art landscape aesthetic.\n"
            "High quality fine art photograph."
        ),
    },
}


async def _start_art_style_flow(
    callback: types.CallbackQuery,
    state: FSMContext,
    style_key: str,
):
    style = ARTISTIC_STYLE_PRESETS.get(style_key)
    if not style:
        await callback.answer("Стиль не найден", show_alert=True)
        return

    await state.update_data(
        selected_preset={
            "name": style["name"],
            "icon": style.get("icon", "🎨"),
            "price": 30,
        },
        prompt=style["prompt"],
    )
    await state.set_state(UserState.awaiting_image_for_preset)

    from ..keyboards import cancel_keyboard

    icon = style.get("icon", "")
    name = style.get("name", "")
    display_name = f"{name}".strip()

    await callback.message.edit_text(
        f"✅ Выбран стиль: {display_name}\n\n"
        f"Стоимость: 30 баллов\n\n"
        "📸 Теперь загрузите фото для обработки:",
        reply_markup=cancel_keyboard(),
    )

    await callback.answer()


# ===== NEW MENU STRUCTURE - 8 MAIN SECTIONS =====

# 1. 🎨 Художественные стили
@router.message(UserState.main_menu, F.text == "🎨 Художественные стили")
async def btn_artistic_styles(message: types.Message, state: FSMContext):
    """Handle 'Художественные стили' button"""
    try:
        await message.answer(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in artistic_styles button: {e}")
        await send_error_message(message)


# 2. 🧝‍ Изменить образ
@router.message(UserState.main_menu, F.text == "🧝‍ Изменить образ")
async def btn_change_appearance(message: types.Message, state: FSMContext):
    """Handle 'Изменить образ' button"""
    try:
        await message.answer(
            "🧝‍ Изменить образ\n\n"
            "Выберите пол:\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=appearance_gender_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in change_appearance button: {e}")
        await send_error_message(message)


# 3. 👕 ПРИМЕРОЧНАЯ (Fitting room with 2 photos)
@router.message(UserState.main_menu, F.text == "👕 ПРИМЕРОЧНАЯ")
async def btn_fitting_room(message: types.Message, state: FSMContext):
    """Handle 'ПРИМЕРОЧНАЯ' button - 2 photo workflow"""
    try:
        instructions = (
            "👕 ПРИМЕРОЧНАЯ\n\n"
            "Здесь вы можете примерить любую одежду на свое фото!\n\n"
            "📸 Вам понадобится 2 фото:\n\n"
            "1️⃣ Фото с ВАМИ\n"
            "Подойдет:\n"
            "• фото по пояс или во весь рост\n"
            "• обычное фото с телефона\n"
            "• можно в зеркале, дома, на улице\n"
            "❗ Главное — чтобы было хорошо видно тело.\n\n"
            "2️⃣ Фото ОДЕЖДЫ\n"
            "Просто:\n"
            "• откройте любой маркетплейс (Ozon, Wildberries, Lamoda и т.д.)\n"
            "• скачайте фото понравившейся одежды\n"
            "• платье, костюм, куртка, рубашка — что угодно\n\n"
            "💡 После загрузки 2 фото, нейросеть создаст реалистичное фото в новой одежде!\n\n"
            "Стоимость: 30 баллов"
        )
        
        await message.answer(
            instructions,
            reply_markup=fitting_room_instructions_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in fitting_room button: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "start_fitting")
async def callback_start_fitting(callback: types.CallbackQuery, state: FSMContext):
    """Start fitting room workflow - ask for first photo"""
    try:
        await state.set_state(UserState.awaiting_first_fitting_photo)
        
        await callback.message.edit_text(
            "📸 Загрузите ПЕРВОЕ фото — фото с ВАМИ (по пояс или во весь рост)\n\n"
            "Убедитесь, что хорошо видно тело.",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in start_fitting callback: {e}")
        await callback.answer("Произошла ошибка")


@router.message(UserState.awaiting_first_fitting_photo, F.photo)
async def handle_first_fitting_photo(message: types.Message, state: FSMContext):
    """Handle first photo in fitting room workflow"""
    try:
        # Store first photo
        photo_id = message.photo[-1].file_id
        await state.update_data(first_photo_id=photo_id)
        
        # Move to second photo state
        await state.set_state(UserState.awaiting_second_fitting_photo)
        
        await message.answer(
            "✅ Первое фото получено!\n\n"
            "📸 Теперь загрузите ВТОРОЕ фото — фото ОДЕЖДЫ\n\n"
            "Это может быть скриншот с маркетплейса или фото одежды.",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
    except Exception as e:
        logger.error(f"Error handling first fitting photo: {e}")
        await send_error_message(message)


@router.message(UserState.awaiting_second_fitting_photo, F.photo)
async def handle_second_fitting_photo(message: types.Message, state: FSMContext):
    """Handle second photo and create job with special prompt"""
    try:
        # Import api_client from main module
        from ..main import api_client
        from ..utils import download_telegram_photo
        import tempfile
        from pathlib import Path
        
        # Store second photo ID
        second_photo_id = message.photo[-1].file_id
        data = await state.get_data()
        first_photo_id = data.get('first_photo_id')
        
        if not first_photo_id:
            await message.answer("❌ Ошибка: не найдено первое фото. Начните сначала.")
            await state.clear()
            await state.set_state(UserState.main_menu)
            return
        
        # Special prompt for fitting room
        fitting_prompt = (
            "Use photo 1 as the primary subject reference. "
            "Preserve the face, facial features, skin texture, head shape and overall identity from photo 1 exactly. "
            "Use photo 2 as clothing reference only. "
            "Take only the clothing item from photo 2. "
            "Do not transfer the person, face, body shape, pose, hair or background from photo 2. "
            "Dress the person from photo 1 in the clothing from photo 2. "
            "Ensure the clothing fits naturally to the body proportions of the person from photo 1. "
            "Maintain realistic fabric folds, texture, proportions and lighting. "
            "Do not change the hairstyle, face, facial expression or body shape from photo 1. "
            "Photorealistic result, high realism, natural lighting."
        )
        
        await message.answer("📥 Загружаю фото и подготавливаю примерку...")
        
        # Download both photos
        first_photo_data = await download_telegram_photo(message.bot, first_photo_id)
        second_photo_data = await download_telegram_photo(message.bot, second_photo_id)
        
        if not first_photo_data or not second_photo_data:
            await message.answer("❌ Ошибка при загрузке фото. Попробуйте снова.")
            return

        # Create temporary files for both images
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f2:
            f1.write(first_photo_data)
            f2.write(second_photo_data)
            f1_path = Path(f1.name)
            f2_path = Path(f2.name)

        try:
            # Prepare files for upload
            with open(f1_path, 'rb') as f1_file, open(f2_path, 'rb') as f2_file:
                f1_content = f1_file.read()
                f2_content = f2_file.read()
            
            f1_tuple = (f1_path.name, f1_content, 'image/jpeg')
            f2_tuple = (f2_path.name, f2_content, 'image/jpeg')
            
            # Create job via API with both photos
            job_data = await api_client.create_job(
                telegram_id=message.from_user.id,
                image_file=f1_tuple,
                prompt=fitting_prompt,
                second_image_file=f2_tuple
            )
            
            job_id = job_data.get('id')
            
            await message.answer(
                f"✅ Фото приняты! Начинаем примерку...\n\n"
                f"ID задачи: {job_id}\n"
                f"Результат будет готов в течение нескольких минут.\n\n"
                f"С вашего баланса списано 30 баллов.",
                reply_markup=main_menu_keyboard()
            )
            await state.clear()
            await state.set_state(UserState.main_menu)
            
        finally:
            # Clean up temporary files
            f1_path.unlink(missing_ok=True)
            f2_path.unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Error handling second fitting photo: {e}")
        from ..utils import send_error_message
        await send_error_message(message)
        await state.clear()
        await state.set_state(UserState.main_menu)


# 4. ✨ Редактировать фото (existing functionality)
@router.message(UserState.main_menu, F.text == "✨ Редактировать фото")
async def btn_edit_photo(message: types.Message, state: FSMContext):
    """Handle 'Редактировать фото' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        
        await message.answer(
            "Как вы хотите редактировать фото?",
            reply_markup=edit_photo_submenu_keyboard()  # Already has Back and Main Menu buttons
        )
        
    except Exception as e:
        logger.error(f"Error in edit_photo button: {e}")
        await send_error_message(message)


# 5. ✍️ Свой промпт (existing functionality)
@router.message(UserState.main_menu, F.text == "✍️ Свой промпт")
async def btn_custom_prompt(message: types.Message, state: FSMContext):
    """Handle 'Свой промпт' button"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(message, state)
        
    except Exception as e:
        logger.error(f"Error in custom_prompt button: {e}")
        await send_error_message(message)


# 6. 📚 База знаний
@router.message(UserState.main_menu, F.text == "📚 База знаний")
async def btn_knowledge_base(message: types.Message, state: FSMContext):
    """Handle 'База знаний' button"""
    try:
        welcome_text = (
            "📚 База знаний\n\n"
            "Здесь будут полезные статьи и гайды по:\n"
            "• Промптам и стилям редактирования\n"
            "• Подбору одежды и fashion\n"
            "• Художественным техникам\n"
            "• Фотосъемке для нейросетей\n\n"
            "Скоро добавим первые материалы!"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=knowledge_base_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in knowledge_base button: {e}")
        await send_error_message(message)


# 7. 👩 Профиль (enhanced balance functionality)
@router.message(UserState.main_menu, F.text == "👩 Профиль")
async def btn_profile(message: types.Message, state: FSMContext):
    """Handle 'Профиль' button - show balance, payment history, promo codes"""
    try:
        from ..main import api_client
        
        # Get user balance from backend
        balance = await api_client.get_balance(message.from_user.id)
        
        if balance is None:
            balance = 0
        
        profile_text = (
            f"👩 Ваш Профиль\n\n"
            f"💰 Баланс: {balance} баллов\n\n"
            f"Стоимость генерации 1 фото: 30 баллов\n"
            f"Курс: 1 балл = 1 рубль\n\n"
            f"📊 Статистика:\n"
            f"• Приветственный бонус: 100 баллов\n"
            f"• Еженедельный бонус: 10 баллов (каждую пятницу)\n"
        )
        
        await message.answer(
            profile_text,
            reply_markup=profile_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in profile button: {e}")
        await send_error_message(message)


# 8. ℹ️ Помощь (existing functionality)
@router.message(UserState.main_menu, F.text == "ℹ️ Помощь")
async def btn_help(message: types.Message):
    """Handle 'Помощь' button"""
    try:
        from .help import show_help
        await show_help(message)
        
    except Exception as e:
        logger.error(f"Error in help button: {e}")
        await send_error_message(message)


# ===== CALLBACK HANDLERS FOR NAVIGATION =====


# Inline keyboard callbacks
@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'back to menu' callback"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_inline_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back_to_menu callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_photo")
async def callback_edit_photo(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit photo' submenu"""
    try:
        await callback.message.edit_text(
            "✨ Редактировать фото\n\n"
            "Выберите действие:",
            reply_markup=edit_photo_submenu_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in edit_photo callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "custom_prompt")
async def callback_custom_prompt_main(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'custom prompt' from main menu"""
    try:
        await state.set_state(UserState.waiting_for_custom_prompt)
        await callback.message.edit_text(
            "✍️ Введите свой промпт\n\n"
            "Опишите, как вы хотите изменить фото. Будьте детальны!"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in custom_prompt callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "help")
async def callback_help(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'help' menu"""
    try:
        help_text = (
            "ℹ️ СПРАВКА И ПОМОЩЬ\n\n"
            "🎨 Художественные стили\n"
            "Примените классические художественные стили к вашему фото\n\n"
            "🧝‍ Изменить образ\n"
            "Измените прическу, борода, усы для мужчин и женщин\n\n"
            "👕 ПРИМЕРОЧНАЯ\n"
            "Попробуйте одежду и аксессуары (нужны 2 фото)\n\n"
            "✨ Редактировать фото\n"
            "Выберите пресет или используйте свой промпт\n\n"
            "✍️ Свой промпт\n"
            "Создайте собственное описание изменений\n\n"
            "📚 База знаний\n"
            "Советы по созданию хороших промптов\n\n"
            "👩 Профиль\n"
            "Ваш баланс и история"
        )
        
        await callback.message.edit_text(
            help_text,
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in help callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "back_to_balance")
async def callback_back_to_balance(callback: types.CallbackQuery):
    """Handle 'back to balance' callback"""
    try:
        from .balance import callback_balance
        await callback_balance(callback)
        
    except Exception as e:
        logger.error(f"Error in back_to_balance callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_preset")
async def callback_edit_preset(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with preset' callback"""
    try:
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=category_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_preset callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_custom")
async def callback_edit_custom(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with custom prompt' callback"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(callback.message, state, is_callback=True)
        
        await callback.message.delete()
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_custom callback: {e}")
        await callback.answer("Произошла ошибка")


# ===== NEW CALLBACK HANDLERS FOR DISABLED FEATURES =====

@router.callback_query(F.data == "category_artistic")
async def callback_artistic_styles(callback: types.CallbackQuery, state: FSMContext):
    """Handle artistic styles callback"""
    try:
        await callback.message.edit_text(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles callback: {e}")
        await callback.answer("Произошла ошибка")


# Artistic styles section navigation

@router.callback_query(F.data == "as_root")
async def callback_artistic_styles_root(callback: types.CallbackQuery, state: FSMContext):
    """Show artistic styles root menu"""
    try:
        await callback.message.edit_text(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard(),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_root callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "as_artists")
async def callback_artistic_styles_artists(callback: types.CallbackQuery, state: FSMContext):
    """Show artists submenu"""
    try:
        await callback.message.edit_text(
            "🎨 Художники\n\nВыберите художника:",
            reply_markup=artistic_styles_artists_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_artists callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_artists_digital")
async def callback_artistic_styles_digital_artists(callback: types.CallbackQuery, state: FSMContext):
    """Show digital artists submenu"""
    try:
        await callback.message.edit_text(
            "💻 Цифровые художники\n\nВыберите художника:",
            reply_markup=artistic_styles_digital_artists_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_digital_artists callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_technique")
async def callback_artistic_styles_technique(callback: types.CallbackQuery, state: FSMContext):
    """Show techniques submenu"""
    try:
        await callback.message.edit_text(
            "✏️ Техника\n\nВыберите технику:",
            reply_markup=artistic_styles_techniques_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_technique callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_comics")
async def callback_artistic_styles_comics(callback: types.CallbackQuery, state: FSMContext):
    """Show comics submenu"""
    try:
        await callback.message.edit_text(
            "⚡ Комиксы\n\nВыберите стиль комиксов:",
            reply_markup=artistic_styles_comics_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_comics callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_cartoons")
async def callback_artistic_styles_cartoons(callback: types.CallbackQuery, state: FSMContext):
    """Show cartoons submenu"""
    try:
        await callback.message.edit_text(
            "🐰 Мультфильмы\n\nВыберите стиль мультфильмов:",
            reply_markup=artistic_styles_cartoons_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_cartoons callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_anime")
async def callback_artistic_styles_anime(callback: types.CallbackQuery, state: FSMContext):
    """Show anime submenu"""
    try:
        await callback.message.edit_text(
            "🌸 Аниме\n\nВыберите стиль аниме:",
            reply_markup=artistic_styles_anime_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_anime callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_fantasy")
async def callback_artistic_styles_fantasy(callback: types.CallbackQuery, state: FSMContext):
    """Show fantasy submenu"""
    try:
        await callback.message.edit_text(
            "🧙 Фэнтези\n\nВыберите стиль фэнтези:",
            reply_markup=artistic_styles_fantasy_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_fantasy callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "as_photographers")
async def callback_artistic_styles_photographers(callback: types.CallbackQuery, state: FSMContext):
    """Show photographers submenu"""
    try:
        await callback.message.edit_text(
            "📸 Фотографы\n\nВыберите стиль фотографа:",
            reply_markup=artistic_styles_photographers_keyboard(),
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in artistic_styles_photographers callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data.startswith("as_style_"))
async def callback_artistic_style_selected(callback: types.CallbackQuery, state: FSMContext):
    """Select artistic style (artist/technique) and switch to photo upload"""
    try:
        await _start_art_style_flow(callback, state, callback.data)
    except Exception as e:
        logger.error(f"Error in artistic style selection: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "fitting_room")
async def callback_fitting_room(callback: types.CallbackQuery, state: FSMContext):
    """Handle fitting room callback from inline menu"""
    try:
        instructions = (
            "👕 ПРИМЕРОЧНАЯ\n\n"
            "Здесь вы можете примерить любую одежду на свое фото!\n\n"
            "📸 Вам понадобится 2 фото:\n\n"
            "1️⃣ Фото с ВАМИ\n"
            "Подойдет:\n"
            "• фото по пояс или во весь рост\n"
            "• обычное фото с телефона\n"
            "• можно в зеркале, дома, на улице\n"
            "❗ Главное — чтобы было хорошо видно тело.\n\n"
            "2️⃣ Фото ОДЕЖДЫ\n"
            "Просто:\n"
            "• откройте любой маркетплейс (Ozon, Wildberries, Lamoda и т.д.)\n"
            "• скачайте фото понравившейся одежды\n"
            "• платье, костюм, куртка, рубашка — что угодно\n\n"
            "💡 После загрузки 2 фото, нейросеть создаст реалистичное фото в новой одежде!\n\n"
            "Стоимость: 30 баллов"
        )
        
        await callback.message.edit_text(
            instructions,
            reply_markup=fitting_room_instructions_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in fitting_room callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_gender")
async def callback_appearance_gender(callback: types.CallbackQuery, state: FSMContext):
    """Handle appearance gender selection callback"""
    try:
        await callback.message.edit_text(
            "🧝‍ Изменить образ\n\n"
            "Выберите пол:\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=appearance_gender_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_gender callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male")
async def callback_appearance_male(callback: types.CallbackQuery, state: FSMContext):
    """Handle male appearance menu"""
    try:
        await callback.message.edit_text(
            "👨 Мужской образ\n\n"
            "Выберите раздел:",
            reply_markup=appearance_male_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_hair")
async def callback_appearance_male_hair(callback: types.CallbackQuery, state: FSMContext):
    """Handle male hairstyles menu"""
    try:
        await callback.message.edit_text(
            "💇 Мужские прически\n\n"
            "Выберите категорию:",
            reply_markup=appearance_male_hairstyle_categories_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_hair callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_hair_short")
async def callback_appearance_male_hair_short(callback: types.CallbackQuery, state: FSMContext):
    """Handle short hairstyles for men"""
    try:
        await callback.message.edit_text(
            "✂️ Короткие стрижки\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_short_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_hair_short callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_hair_medium")
async def callback_appearance_male_hair_medium(callback: types.CallbackQuery, state: FSMContext):
    """Handle medium length hairstyles for men"""
    try:
        await callback.message.edit_text(
            "🌊 Средняя длина\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_medium_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_hair_medium callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_hair_long")
async def callback_appearance_male_hair_long(callback: types.CallbackQuery, state: FSMContext):
    """Handle long hairstyles for men"""
    try:
        await callback.message.edit_text(
            "💁 Длинные волосы\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_long_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_hair_long callback: {e}")
        await callback.answer("Произошла ошибка")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "appearance_male_beard")
async def callback_appearance_male_beard(callback: types.CallbackQuery, state: FSMContext):
    """Handle male beard and mustache categories"""
    try:
        await callback.message.edit_text(
            "🧔 Борода и Усы\n\n"
            "Выберите категорию:",
            reply_markup=appearance_male_beard_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_beard callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_beard_none")
async def callback_appearance_male_beard_none(callback: types.CallbackQuery, state: FSMContext):
    """Handle male beard without beard (stubble) styles"""
    try:
        await callback.message.edit_text(
            "🧔 БЕЗ БОРОДЫ\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_beard_none_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_beard_none callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_beard_short")
async def callback_appearance_male_beard_short(callback: types.CallbackQuery, state: FSMContext):
    """Handle male short beard styles"""
    try:
        await callback.message.edit_text(
            "🧔 КОРОТКАЯ БОРОДА\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_beard_short_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_beard_short callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_beard_medium")
async def callback_appearance_male_beard_medium(callback: types.CallbackQuery, state: FSMContext):
    """Handle male medium beard styles"""
    try:
        await callback.message.edit_text(
            "🧔 СРЕДНЯЯ БОРОДА\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_beard_medium_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_beard_medium callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_beard_long")
async def callback_appearance_male_beard_long(callback: types.CallbackQuery, state: FSMContext):
    """Handle male long beard styles"""
    try:
        await callback.message.edit_text(
            "🧔 ДЛИННАЯ БОРОДА\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_beard_long_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_beard_long callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_male_mustache")
async def callback_appearance_male_mustache(callback: types.CallbackQuery, state: FSMContext):
    """Handle male mustache styles"""
    try:
        await callback.message.edit_text(
            "👨‍🦰 УСЫ\n\n"
            "Выберите стиль:",
            reply_markup=appearance_male_mustache_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_male_mustache callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female")
async def callback_appearance_female(callback: types.CallbackQuery, state: FSMContext):
    """Handle female appearance menu"""
    try:
        await callback.message.edit_text(
            "👩 Женский образ\n\n"
            "Выберите раздел:",
            reply_markup=appearance_female_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair")
async def callback_appearance_female_hair(callback: types.CallbackQuery, state: FSMContext):
    """Handle female hairstyles menu"""
    try:
        await callback.message.edit_text(
            "💇 Прически\n\n"
            "Выберите категорию:",
            reply_markup=appearance_female_hairstyle_categories_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_short")
async def callback_appearance_female_hair_short(callback: types.CallbackQuery, state: FSMContext):
    """Handle short hairstyles"""
    try:
        await callback.message.edit_text(
            "✂️ Короткие причёски\n\n"
            "Выберите стиль:",
            reply_markup=appearance_short_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_short callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_medium")
async def callback_appearance_female_hair_medium(callback: types.CallbackQuery, state: FSMContext):
    """Handle medium length hairstyles"""
    try:
        await callback.message.edit_text(
            "🌊 Средняя длина волос\n\n"
            "Выберите стиль:",
            reply_markup=appearance_medium_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_medium callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_long")
async def callback_appearance_female_hair_long(callback: types.CallbackQuery, state: FSMContext):
    """Handle long hairstyles"""
    try:
        await callback.message.edit_text(
            "💁 Длинные волосы\n\n"
            "Выберите стиль:",
            reply_markup=appearance_long_hairstyles_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_long callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_bangs")
async def callback_appearance_female_hair_bangs(callback: types.CallbackQuery, state: FSMContext):
    """Handle bangs hairstyles"""
    try:
        await callback.message.edit_text(
            "🪮 Чёлки\n\n"
            "Выберите вид чёлки:",
            reply_markup=appearance_bangs_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_bangs callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_updo")
async def callback_appearance_female_hair_updo(callback: types.CallbackQuery, state: FSMContext):
    """Handle updo hairstyles"""
    try:
        await callback.message.edit_text(
            "🎀 Убранные волосы\n\n"
            "Выберите стиль:",
            reply_markup=appearance_updo_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_updo callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_braids")
async def callback_appearance_female_hair_braids(callback: types.CallbackQuery, state: FSMContext):
    """Handle braids hairstyles"""
    try:
        await callback.message.edit_text(
            "🧵 Косы\n\n"
            "Выберите вид косы:",
            reply_markup=appearance_braids_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_braids callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "appearance_female_hair_styles")
async def callback_appearance_female_hair_styles(callback: types.CallbackQuery, state: FSMContext):
    """Handle stylistic hairstyles"""
    try:
        await callback.message.edit_text(
            "✨ Стилистические направления\n\n"
            "Выберите стиль оформления:",
            reply_markup=appearance_stylistic_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in appearance_female_hair_styles callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("hairstyle_"))
async def callback_hairstyle_selected(callback: types.CallbackQuery, state: FSMContext):
    """Handle hairstyle preset selection"""
    try:
        hairstyle_id = callback.data.replace("hairstyle_", "")
        logger.info(f"Selected hairstyle ID: {hairstyle_id}")
        
        # Find hairstyle in all preset dictionaries
        hairstyle = (
            FEMALE_SHORT_HAIRSTYLES_PRESETS.get(hairstyle_id) or 
            FEMALE_MEDIUM_HAIRSTYLES_PRESETS.get(hairstyle_id) or 
            FEMALE_LONG_HAIRSTYLES_PRESETS.get(hairstyle_id) or
            FEMALE_BANGS_PRESETS.get(hairstyle_id) or
            FEMALE_UPDO_PRESETS.get(hairstyle_id) or
            FEMALE_BRAIDS_PRESETS.get(hairstyle_id) or
            FEMALE_STYLISTIC_PRESETS.get(hairstyle_id) or
            MALE_SHORT_HAIRSTYLES_PRESETS.get(hairstyle_id) or
            MALE_MEDIUM_HAIRSTYLES_PRESETS.get(hairstyle_id) or
            MALE_LONG_HAIRSTYLES_PRESETS.get(hairstyle_id) or
            MALE_BEARD_NO_BEARD_PRESETS.get(hairstyle_id) or
            MALE_BEARD_SHORT_PRESETS.get(hairstyle_id) or
            MALE_BEARD_MEDIUM_PRESETS.get(hairstyle_id) or
            MALE_BEARD_LONG_PRESETS.get(hairstyle_id) or
            MALE_MUSTACHE_PRESETS.get(hairstyle_id)
        )
        
        if not hairstyle:
            logger.warning(f"Hairstyle not found for ID: {hairstyle_id}")
            await callback.answer("Причёска не найдена", show_alert=True)
            return
        
        logger.info(f"Found hairstyle: {hairstyle.get('name')}")
        await _start_hairstyle_flow(callback, state, hairstyle)
        
    except Exception as e:
        logger.error(f"Error in hairstyle selection: {e}", exc_info=True)
        await callback.answer("Произошла ошибка", show_alert=True)


async def _start_hairstyle_flow(
    callback: types.CallbackQuery,
    state: FSMContext,
    hairstyle: dict
):
    """Helper function to start hairstyle editing flow"""
    try:
        await state.update_data(
            selected_preset={
                "name": hairstyle["name"],
                "icon": hairstyle.get("icon", "✂️"),
                "price": hairstyle.get("price", 30),
            },
            prompt=hairstyle["prompt"],
        )
        await state.set_state(UserState.awaiting_image_for_preset)
        
        from ..keyboards import cancel_keyboard
        
        icon = hairstyle.get("icon", "")
        name = hairstyle.get("name", "")
        display_name = f"{name}".strip()
        
        await callback.message.edit_text(
            f"✅ Выбран стиль: {display_name}\n\n"
            f"Стоимость: 30 баллов\n\n"
            f"📸 Теперь загрузите фото для обработки:",
            reply_markup=cancel_keyboard(),
        )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in hairstyle flow: {e}", exc_info=True)
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "change_appearance")
async def callback_change_appearance(callback: types.CallbackQuery, state: FSMContext):
    """Handle change appearance callback"""
    try:
        await callback.message.edit_text(
            "🧝‍ Изменить образ\n\n"
            "Кнопка временно не активна. Подразделы находятся в разработке.\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=main_menu_inline_keyboard()
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in change_appearance callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "knowledge_base")
async def callback_knowledge_base(callback: types.CallbackQuery, state: FSMContext):
    """Handle knowledge base callback"""
    try:
        welcome_text = (
            "📚 База знаний\n\n"
            "Здесь будут полезные статьи и гайды по:\n"
            "• Промптам и стилям редактирования\n"
            "• Подбору одежды и fashion\n"
            "• Художественным техникам\n"
            "• Фотосъемке для нейросетей\n\n"
            "Скоро добавим первые материалы!"
        )
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=knowledge_base_keyboard()
        )
        # Don't call callback.answer() to avoid timeout issues
    except Exception as e:
        logger.error(f"Error in knowledge_base callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "profile")
async def callback_profile(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile callback"""
    try:
        from ..main import api_client
        
        # Get user balance from backend
        balance = await api_client.get_balance(callback.from_user.id)
        
        if balance is None:
            balance = 0
        
        profile_text = (
            f"👩 Ваш Профиль\n\n"
            f"💰 Баланс: {balance} баллов\n\n"
            f"Стоимость генерации 1 фото: 30 баллов\n"
            f"Курс: 1 балл = 1 рубль\n\n"
            f"📊 Статистика:\n"
            f"• Приветственный бонус: 100 баллов\n"
            f"• Еженедельный бонус: 10 баллов (каждую пятницу)\n"
        )
        
        await callback.message.edit_text(
            profile_text,
            reply_markup=profile_menu_keyboard()
        )
        # Don't call callback.answer() to avoid timeout issues
        
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            # Callback is too old, just log the error
            logger.warning("Callback too old, cannot send error message")


# Knowledge base subcategories (placeholders)
@router.callback_query(F.data == "kb_prompts")
async def callback_kb_prompts(callback: types.CallbackQuery):
    """Handle knowledge base - prompts section"""
    try:
        await callback.answer("📖 Раздел 'Промпты и стили' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_prompts callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "kb_fashion")
async def callback_kb_fashion(callback: types.CallbackQuery):
    """Handle knowledge base - fashion section"""
    try:
        await callback.answer("👗 Раздел 'Одежда и fashion' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_fashion callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "kb_art")
async def callback_kb_art(callback: types.CallbackQuery):
    """Handle knowledge base - art techniques section"""
    try:
        await callback.answer("🎭 Раздел 'Художественные техники' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_art callback: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            logger.warning("Callback too old, cannot send error message")


@router.callback_query(F.data == "disabled")
async def callback_disabled_feature(callback: types.CallbackQuery):
    """Handle disabled feature callback"""
    try:
        await callback.answer("🔒 Эта функция временно отключена для тестирования", show_alert=True)
    except Exception as e:
        logger.error(f"Error handling disabled feature: {e}")
        try:
            await callback.answer("Произошла ошибка")
        except Exception:
            logger.warning("Callback too old, cannot send error message")
