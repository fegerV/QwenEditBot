# Описание всех промптов

Этот документ содержит описание всех промптов, используемых в системе.

**Дата создания:** 1769455562.0054548

**Всего промптов:** 170


## 1. Промпты из базы данных (Seed Presets) - УСТАРЕВШИЕ

**⚠️ Внимание:** Эти промпты используются через старую систему пресетов (API `/presets/`) и могут быть устаревшими. 

Основные промпты находятся в `menu.py` (см. раздел 2).

Эти промпты загружаются в базу данных при первой инициализации через функцию `seed_presets_if_empty()` и используются в `bot/handlers/presets.py` для старой функциональности выбора пресетов по категориям.


### Категория: animation

#### 💥 Comic Book

**Промпт:**
```
Convert the image into a comic book style with bold outlines, flat colors, and a graphic illustrated look.
```

**Источник:** database.py (seed presets)

**Порядок:** 1


#### 🇯🇵 Anime

**Промпт:**
```
Transform the image into an anime style illustration with clean lines, expressive features, and vibrant colors.
```

**Источник:** database.py (seed presets)

**Порядок:** 2


#### 🧸 Cartoon

**Промпт:**
```
Convert the image into a cartoon style with simplified shapes, bright colors, and a playful illustrated look.
```

**Источник:** database.py (seed presets)

**Порядок:** 3



### Категория: enhancement

#### ✨ Improve Quality

**Промпт:**
```
Improve image quality by enhancing details, colors, and lighting while keeping the original style and composition unchanged.
```

**Источник:** database.py (seed presets)

**Порядок:** 1



### Категория: lighting

#### 🌞 Soft Light

**Промпт:**
```
Adjust the image to have soft, natural lighting with smooth shadows and a warm, pleasant atmosphere.
```

**Источник:** database.py (seed presets)

**Порядок:** 1


#### 🌙 Dark Mood

**Промпт:**
```
Create a dark and moody atmosphere with low-key lighting, deep shadows, and cinematic contrast.
```

**Источник:** database.py (seed presets)

**Порядок:** 2


#### 🌅 Golden Hour

**Промпт:**
```
Apply golden hour lighting with warm tones, soft highlights, and a sunset-like atmosphere.
```

**Источник:** database.py (seed presets)

**Порядок:** 3



### Категория: portrait

#### 📸 Studio Portrait

**Промпт:**
```
Enhance the image into a professional studio portrait with soft lighting, realistic skin texture, and natural colors, preserving facial identity.
```

**Источник:** database.py (seed presets)

**Порядок:** 1


#### 🎬 Cinematic Portrait

**Промпт:**
```
Convert the portrait into a cinematic style with dramatic lighting, shallow depth of field, and a movie-like atmosphere, while keeping the person's identity.
```

**Источник:** database.py (seed presets)

**Порядок:** 2


#### 🧑‍🎨 Artistic Portrait

**Промпт:**
```
Create an artistic portrait with expressive lighting and painterly details, preserving facial features and overall composition.
```

**Источник:** database.py (seed presets)

**Порядок:** 3



### Категория: product

#### 🛒 E-commerce

**Промпт:**
```
Transform the image into a clean professional product photo with neutral background, even lighting, and sharp details suitable for an online store.
```

**Источник:** database.py (seed presets)

**Порядок:** 1


#### 🌟 Premium Product

**Промпт:**
```
Enhance the product image with dramatic lighting, glossy reflections, and a premium advertising look, keeping the product shape unchanged.
```

**Источник:** database.py (seed presets)

**Порядок:** 2



### Категория: styles

#### 🖌 Oil Painting

**Промпт:**
```
Convert the image into an oil painting style with visible brush strokes, rich colors, and a classical artistic feel, while preserving the original composition.
```

**Источник:** database.py (seed presets)

**Порядок:** 1


#### 💧 Watercolor

**Промпт:**
```
Convert the image into a watercolor painting with soft edges, light color bleeding, and a hand-painted artistic look, preserving the main details.
```

**Источник:** database.py (seed presets)

**Порядок:** 2


#### ✏️ Pencil Sketch

**Промпт:**
```
Transform the image into a detailed pencil sketch with clear linework and shading, like a hand-drawn illustration.
```

**Источник:** database.py (seed presets)

**Порядок:** 3


#### 🖋 Ink Drawing

**Промпт:**
```
Convert the image into an ink drawing with bold black outlines, high contrast, and a clean hand-drawn style.
```

**Источник:** database.py (seed presets)

**Порядок:** 4



## 2. Промпты из menu.py - ОСНОВНЫЕ

**✅ Это основные промпты системы!**

Эти промпты определены напрямую в коде (`bot/handlers/menu.py`) и используются для всех основных функций бота:
- 🧝‍ Изменить образ (прически, бороды, усы)
- 🎨 Художественные стили
- 👕 Примерочная
- И другие функции

Они не хранятся в базе данных и работают напрямую из кода.


### Категория: female_short_hairstyles

#### 🎮 3D-рендер

**Ключ:** `as_style_tech_3d_render`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply 3D render technique,\n" realistic materials,\n" studio lighting,\n" high detail,\n" photorealistic rendering.\n" Clean, modern 3D result.
```

**Источник:** menu.py


#### 💻 Artgerm (Stanley Lau)

**Ключ:** `as_style_artgerm`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions exactly.\n" Apply the semi-realistic digital art style of Artgerm,\n" smooth painterly shading,\n" clean detailed features,\n" professional illustration quality.\n" High quality, polished result.
```

**Источник:** menu.py


#### 💻 Beeple (Mike Winkelmann)

**Ключ:** `as_style_beeple`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply a digital art style inspired by Beeple,\n" futuristic and surreal elements,\n" high-contrast lighting,\n" detailed textures,\n" modern digital aesthetic.\n" High quality digital artwork
```

**Источник:** menu.py


#### 💈 Buzz cut

**Ключ:** `m_short_buzz_cut`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's buzz cut haircut.\n" Very short uniform length.\n" Clean and minimal look.
```

**Источник:** menu.py


#### 💈 Caesar

**Ключ:** `m_short_caesar`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's Caesar haircut.\n" Short straight fringe, uniform length.\n" Classic structured shape.
```

**Источник:** menu.py


#### 🧔 Chevron mustache

**Ключ:** `m_mustache_chevron`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a chevron mustache.\n" Thick mustache covering the upper lip.\n" Classic masculine style.
```

**Источник:** menu.py


#### 🧔 Classic mustache

**Ключ:** `m_mustache_classic`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a classic mustache.\n" Natural thickness.\n" Clean shape.
```

**Источник:** menu.py


#### 🎨 Claude Monet

**Ключ:** `as_style_monet`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply the artistic style of Claude Monet,\n" impressionist painting,\n" soft diffused light,\n" pastel color palette,\n" gentle brushstrokes.\n" High quality, atmospheric result.
```

**Источник:** menu.py


#### 🧔 Clean shave (гладко выбрит)

**Ключ:** `m_beard_clean_shave`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a clean shaved look.\n" Completely remove beard and mustache.\n" Smooth natural skin appearance.
```

**Источник:** menu.py


#### 🧔 Corporate beard

**Ключ:** `m_beard_corporate`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a corporate beard.\n" Short tidy beard suitable for business style.\n" Well-defined contours.
```

**Источник:** menu.py


#### 💈 Crew cut

**Ключ:** `m_short_crew_cut`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's crew cut haircut.\n" Short sides and back, slightly longer top.\n" Neat and balanced proportions.
```

**Источник:** menu.py


#### 🧔 Designer stubble (аккуратная щетина)

**Ключ:** `m_beard_designer_stubble`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply designer stubble.\n" Short well-groomed facial hair.\n" Clean edges and neat appearance.
```

**Источник:** menu.py


#### 🧔 Ducktail beard

**Ключ:** `m_beard_ducktail`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a ducktail beard.\n" Tapered shape toward the chin.\n" Defined jawline.
```

**Источник:** menu.py


#### 🧔 English mustache

**Ключ:** `m_mustache_english`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply an English mustache.\n" Long ends styled outward.\n" Classic vintage style.
```

**Источник:** menu.py


#### 🧔 Garibaldi beard

**Ключ:** `m_beard_garibaldi`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a Garibaldi beard.\n" Wide rounded bottom.\n" Natural fullness.
```

**Источник:** menu.py


#### 🧔 Handlebar mustache

**Ключ:** `m_mustache_handlebar`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a handlebar mustache.\n" Curled ends.\n" Styled yet realistic.
```

**Источник:** menu.py


#### 💈 High and tight

**Ключ:** `m_short_high_tight`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's high and tight haircut.\n" Extremely short sides, compact top.\n" Sharp contrast, clean finish.
```

**Источник:** menu.py


#### 🧔 Hungarian mustache

**Ключ:** `m_mustache_hungarian`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a Hungarian mustache.\n" Wide thick mustache extending sideways.\n" Bold appearance.
```

**Источник:** menu.py


#### 💈 Ivy League

**Ключ:** `m_medium_ivy_league`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's Ivy League haircut.\n" Neat medium top, tapered sides.\n" Classic academic style.
```

**Источник:** menu.py


#### 💈 Layered long

**Ключ:** `m_long_layered`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply layered long men's hair.\n" Visible layers for depth and movement.
```

**Источник:** menu.py


#### 💈 Layered medium

**Ключ:** `m_medium_layered`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a layered medium length men's haircut.\n" Visible layers for movement and depth.\n" Natural texture.
```

**Источник:** menu.py


#### 🧔 Light stubble (лёгкая щетина)

**Ключ:** `m_beard_light_stubble`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply light stubble.\n" Very short even facial hair.\n" Natural subtle texture.
```

**Источник:** menu.py


#### 💻 Loish

**Ключ:** `as_style_loish`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" For portraits, preserve facial identity.\n" Apply a soft colorful illustration style inspired by Loish,\n" smooth gradients,\n" gentle lighting,\n" expressive but simplified forms.\n" High quality illustration.
```

**Источник:** menu.py


#### 💈 Long curly

**Ключ:** `m_long_curly`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long curly men's hair.\n" Defined natural curls.\n" Balanced volume.
```

**Источник:** menu.py


#### 🧔 Long full beard

**Ключ:** `m_beard_long_full`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a long full beard.\n" Full coverage with natural length.\n" Realistic flow and density.
```

**Источник:** menu.py


#### 🧔 Long natural beard

**Ключ:** `m_beard_long_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a long natural beard.\n" Minimal shaping.\n" Authentic uneven texture.
```

**Источник:** menu.py


#### 💈 Long straight

**Ключ:** `m_long_straight`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long straight men's hair.\n" Smooth natural flow.\n" Even length.
```

**Источник:** menu.py


#### 💈 Long wavy

**Ключ:** `m_long_wavy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long wavy men's hair.\n" Soft natural waves.\n" Relaxed shape.
```

**Источник:** menu.py


#### 🧔 Medium beard with fade

**Ключ:** `m_beard_medium_with_fade`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a medium beard with fade.\n" Smooth blending into haircut.\n" Clean cheek lines.
```

**Источник:** menu.py


#### 🧔 Medium boxed beard

**Ключ:** `m_beard_medium_boxed`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a medium boxed beard.\n" Structured shape with defined lines.\n" Controlled volume.
```

**Источник:** menu.py


#### 🧔 Medium full beard

**Ключ:** `m_beard_medium_full`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a medium full beard.\n" Balanced length and volume.\n" Natural realistic texture.
```

**Источник:** menu.py


#### 💈 Messy medium

**Ключ:** `m_medium_messy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a slightly messy medium length men's haircut.\n" Casual texture, effortless look.
```

**Источник:** menu.py


#### 💈 Military cut

**Ключ:** `m_short_military`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's military haircut.\n" Very short sides and back, minimal top length.\n" Strict and clean appearance.
```

**Источник:** menu.py


#### 💈 Natural long

**Ключ:** `m_long_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply natural long men's hair.\n" Minimal styling.\n" Realistic texture.
```

**Источник:** menu.py


#### 💈 Natural medium

**Ключ:** `m_medium_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a natural medium length men's haircut.\n" Relaxed shape, natural flow.\n" Minimal styling.
```

**Источник:** menu.py


#### 🧔 Natural medium beard

**Ключ:** `m_beard_natural_medium`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a natural medium beard.\n" Slightly uneven realistic growth.\n" Relaxed appearance.
```

**Источник:** menu.py


#### 🧔 Natural mustache

**Ключ:** `m_mustache_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a natural mustache.\n" Soft edges and realistic density.
```

**Источник:** menu.py


#### 🧔 No mustache

**Ключ:** `m_mustache_none`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Remove mustache completely.
```

**Источник:** menu.py


#### 🎨 Pablo Picasso

**Ключ:** `as_style_picasso`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original composition of the image.\n" For portraits, loosely preserve facial features.\n" Apply a cubist style inspired by Pablo Picasso,\n" abstract geometric shapes,\n" bold color blocks,\n" fragmented forms.\n" Artistic interpretation, coherent structure.
```

**Источник:** menu.py


#### 🧔 Pencil mustache

**Ключ:** `m_mustache_pencil`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a pencil mustache.\n" Thin precise line above the lip.\n" Clean refined look.
```

**Источник:** menu.py


#### 💻 Ross Tran (RossDraws)

**Ключ:** `as_style_ross_tran`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original composition of the image.\n" For portraits, preserve facial identity.\n" Apply a vibrant stylized digital painting style inspired by Ross Tran (RossDraws),\n" dynamic lighting,\n" bold colors,\n" energetic brushwork.\n" High quality digital illustration.
```

**Источник:** menu.py


#### 🧔 Rounded beard

**Ключ:** `m_beard_rounded`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a rounded beard shape.\n" Soft contours.\n" Natural edges.
```

**Источник:** menu.py


#### 🎨 Salvador Dalí

**Ключ:** `as_style_dali`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity.\n" Apply the surrealist style inspired by Salvador Dalí,\n" dreamlike atmosphere,\n" distorted reality elements,\n" smooth painterly technique.\n" High quality, surreal but coherent result.
```

**Источник:** menu.py


#### 🧔 Short beard with fade

**Ключ:** `m_beard_short_with_fade`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a short beard with fade.\n" Smooth transition from beard into haircut.\n" Natural blend.
```

**Источник:** menu.py


#### 🧔 Short boxed beard

**Ключ:** `m_beard_short_boxed`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a short boxed beard.\n" Short even length.\n" Clean defined lines on cheeks and jaw.
```

**Источник:** menu.py


#### 💈 Short crop

**Ключ:** `m_short_crop`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's short crop haircut.\n" Short textured top, clean sides.\n" Modern and practical look.
```

**Источник:** menu.py


#### 🧔 Short full beard

**Ключ:** `m_beard_short_full`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a short full beard.\n" Even length across cheeks, jaw and chin.\n" Natural density.
```

**Источник:** menu.py


#### 💈 Short sides, medium top

**Ключ:** `m_medium_short_sides_medium_top`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's haircut with short sides and medium length top.\n" Balanced proportions.\n" Classic versatile style.
```

**Источник:** menu.py


#### 💈 Shoulder-length

**Ключ:** `m_long_shoulder_length`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply shoulder-length men's hair.\n" Balanced length and natural fall.
```

**Источник:** menu.py


#### 💈 Side part

**Ключ:** `m_medium_side_part`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a men's haircut with a clear side part.\n" Medium length top, tidy sides.\n" Clean and professional appearance.
```

**Источник:** menu.py


#### 🧔 Tapered short beard

**Ключ:** `m_beard_tapered_short`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a tapered short beard.\n" Gradual transition from cheeks to jaw.\n" Clean professional look.
```

**Источник:** menu.py


#### 💈 Textured crop

**Ключ:** `m_medium_textured_crop`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a textured crop men's haircut.\n" Medium length top with visible texture.\n" Natural and modern look.
```

**Источник:** menu.py


#### 💈 Textured short

**Ключ:** `m_short_textured`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a very short textured men's haircut.\n" Subtle texture on top, clean sides.\n" Natural realistic finish.
```

**Источник:** menu.py


#### 🧔 Viking beard

**Ключ:** `m_beard_viking`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change facial hair.\n" Maintain realistic facial hair density, texture and proportions.\n" Photorealistic result.\n" Apply a Viking-style beard.\n" Long thick beard with rugged texture.\n" Powerful masculine look.
```

**Источник:** menu.py


#### 🎨 Vincent van Gogh

**Ключ:** `as_style_van_gogh`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply the artistic style of Vincent van Gogh,\n" oil painting, expressive swirling brushstrokes,\n" vibrant saturated colors,\n" visible canvas texture.\n" High quality, painterly result.
```

**Источник:** menu.py


#### 💧 Акварель

**Ключ:** `as_style_tech_watercolor`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply watercolor painting technique,\n" soft translucent washes,\n" gentle color bleeding,\n" visible paper texture.\n" Light, atmospheric result.
```

**Источник:** menu.py


#### 🌾 Бохо

**Ключ:** `h_style_boho`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply boho hairstyle styling.\n" Relaxed texture, natural flow.\n" Slight messiness, effortless look.
```

**Источник:** menu.py


#### 💁 Волнистые длинные

**Ключ:** `h_long_wavy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long wavy hair.\n" Soft natural waves.
```

**Источник:** menu.py


#### 🌊 Волосы до плеч

**Ключ:** `h_medium_shoulder`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply shoulder-length hairstyle.\n" Natural fall, balanced volume.
```

**Источник:** menu.py


#### 🎀 Высокий пучок

**Ключ:** `h_updo_high_bun`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a high bun hairstyle.\n" Lifted, neat structure.
```

**Источник:** menu.py


#### 🎀 Высокий хвост

**Ключ:** `h_updo_high_ponytail`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a high ponytail.\n" Tight and lifted.
```

**Источник:** menu.py


#### ✂️ Гарсон

**Ключ:** `h_short_garcon`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a garçon haircut.\n" Very short, minimalistic, elegant shape.
```

**Источник:** menu.py


#### 💁 Гладкие длинные

**Ключ:** `h_long_sleek`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply sleek long hair.\n" Smooth polished finish.
```

**Источник:** menu.py


#### 🎀 Гладко убранные волосы

**Ключ:** `h_updo_slicked_back`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply slicked-back hair.\n" Smooth, polished finish.
```

**Источник:** menu.py


#### 💎 Гламур

**Ключ:** `h_style_glamour`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply glamorous hairstyle styling.\n" Glossy finish, enhanced volume.\n" Well-defined shape, polished look.
```

**Источник:** menu.py


#### 🧵 Голландская коса

**Ключ:** `h_braids_dutch`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a Dutch braid.\n" Raised braid with inverted weaving.
```

**Источник:** menu.py


#### 📰 Гравюра / офорт

**Ключ:** `as_style_tech_engraving`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply engraving technique,\n" fine linework,\n" cross-hatching,\n" vintage illustration style.\n" High detail monochrome result.
```

**Источник:** menu.py


#### 🧵 Две косы

**Ключ:** `h_braids_two`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply two braids.\n" Symmetrical and neat.
```

**Источник:** menu.py


#### 💁 Длинные с мягкими локонами

**Ключ:** `h_long_soft_curls`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long hair with soft curls.\n" Loose curls, elegant movement.
```

**Источник:** menu.py


#### 💁 Длинные с объёмом

**Ключ:** `h_long_volume`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long hairstyle with added volume.\n" Lifted roots, full silhouette.
```

**Источник:** menu.py


#### 💁 Длинные с слоями

**Ключ:** `h_long_layered`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long layered hairstyle.\n" Visible layers for depth and movement.
```

**Источник:** menu.py


#### ✏️ Карандаш

**Ключ:** `as_style_tech_pencil`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity.\n" Apply pencil drawing technique,\n" graphite linework,\n" hand-drawn shading,\n" white paper background.\n" Clean sketch style.
```

**Источник:** menu.py


#### 🌊 Каре

**Ключ:** `h_medium_carre`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a carré haircut.\n" Straight shape, clear horizontal line.
```

**Источник:** menu.py


#### 🌊 Каре с удлинением

**Ключ:** `h_medium_carre_long`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a bob haircut with longer front strands.\n" Angled silhouette, modern look.
```

**Источник:** menu.py


#### 🧵 Классическая коса

**Ключ:** `h_braids_classic`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a classic braid.\n" Neat and even weaving.
```

**Источник:** menu.py


#### 🌊 Классический боб

**Ключ:** `h_medium_classic_bob`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a classic bob haircut.\n" Even length, clean geometric shape.
```

**Источник:** menu.py


#### 🧠 Концепт-арт

**Ключ:** `as_style_tech_concept_art`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original composition of the image.\n" Apply concept art technique,\n" cinematic lighting,\n" dramatic atmosphere,\n" detailed forms and environments.\n" Professional illustration quality.
```

**Источник:** menu.py


#### ✂️ Короткая асимметричная

**Ключ:** `h_short_asymmetric`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a short asymmetrical haircut.\n" One side slightly longer, modern silhouette.
```

**Источник:** menu.py


#### ✂️ Короткая с объёмом на макушке

**Ключ:** `h_short_crown_volume`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a short haircut with volume on the crown.\n" Lifted crown, balanced proportions.
```

**Источник:** menu.py


#### ✂️ Короткая с удлинёнными прядями

**Ключ:** `h_short_elongated`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a short haircut with elongated front strands.\n" Front pieces longer, soft framing.
```

**Источник:** menu.py


#### ✂️ Короткая текстурная

**Ключ:** `h_short_textured`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a short textured haircut.\n" Visible layers, light messiness, natural movement.
```

**Источник:** menu.py


#### ✂️ Короткий боб

**Ключ:** `h_short_bob`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a short bob haircut.\n" Hair length above the jawline, clean shape.
```

**Источник:** menu.py


#### 🧵 Коса вокруг головы

**Ключ:** `h_braids_crown`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a crown braid.\n" Wrapped around the head.
```

**Источник:** menu.py


#### 🪮 Косая чёлка

**Ключ:** `h_bangs_side_swept`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add side-swept bangs.\n" Soft diagonal shape.
```

**Источник:** menu.py


#### 💁 Кудрявые длинные

**Ключ:** `h_long_curly`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long curly hair.\n" Defined curls, realistic density.
```

**Источник:** menu.py


#### 📐 Линейный арт

**Ключ:** `as_style_tech_line_art`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply clean line art technique,\n" precise outlines,\n" minimal shading,\n" illustration style.\n" Sharp and minimal result.
```

**Источник:** menu.py


#### 🪮 Лёгкая воздушная чёлка

**Ключ:** `h_bangs_airy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add airy light bangs.\n" Thin, soft, natural.
```

**Источник:** menu.py


#### 🖍 Маркеры

**Ключ:** `as_style_tech_markers`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply marker illustration technique,\n" bold saturated colors,\n" visible strokes,\n" graphic illustration style.\n" Clean and vibrant result.
```

**Источник:** menu.py


#### 🎨 Масляная живопись

**Ключ:** `as_style_tech_oil`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply oil painting technique,\n" rich thick brushstrokes,\n" deep saturated colors,\n" visible canvas texture.\n" High quality painterly result.
```

**Источник:** menu.py


#### ▫️ Минимализм

**Ключ:** `h_style_minimalism`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply a minimalist hairstyle styling.\n" Clean lines, restrained volume.\n" No excessive texture or decoration.\n" Simple and modern look.
```

**Источник:** menu.py


#### 📰 Модный editorial

**Ключ:** `h_style_editorial`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply editorial hairstyle styling.\n" High-fashion look.\n" Slight exaggeration allowed.\n" Clean but expressive styling.
```

**Источник:** menu.py


#### 💁 Натуральная текстура

**Ключ:** `h_long_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long hair with natural texture.\n" Minimal styling, realistic look.
```

**Источник:** menu.py


#### 🌿 Натуральный стиль

**Ключ:** `h_style_natural`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply a natural hairstyle styling.\n" Minimal styling, natural texture.\n" Slight imperfections allowed.\n" Soft volume, realistic look.
```

**Источник:** menu.py


#### 🎀 Низкий пучок

**Ключ:** `h_updo_low_bun`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a low bun hairstyle.\n" Clean, elegant shape.
```

**Источник:** menu.py


#### 🎀 Низкий хвост

**Ключ:** `h_updo_low_ponytail`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a low ponytail.\n" Relaxed and natural.
```

**Источник:** menu.py


#### 🖌 Пастель

**Ключ:** `as_style_tech_pastel`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity.\n" Apply pastel drawing technique,\n" soft chalk textures,\n" smooth color transitions,\n" matte finish.\n" High quality illustration.
```

**Источник:** menu.py


#### ✂️ Пикси

**Ключ:** `h_short_pixie`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a pixie haircut.\n" Short neat hairstyle with clean silhouette.\n" Natural hair texture, realistic density.
```

**Источник:** menu.py


#### ✂️ Пикси с объёмом

**Ключ:** `h_short_pixie_volume`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a pixie haircut with added volume.\n" Lifted roots, airy structure, soft volume.
```

**Источник:** menu.py


#### 🎀 Полусобранные волосы

**Ключ:** `h_updo_half_up`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply half-up hairstyle.\n" Top section tied, rest loose.
```

**Источник:** menu.py


#### 🪮 Прямая чёлка

**Ключ:** `h_bangs_straight`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add straight bangs.\n" Even line, natural density.
```

**Источник:** menu.py


#### 💁 Прямые длинные

**Ключ:** `h_long_straight`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply long straight hair.\n" Smooth texture, natural shine.
```

**Источник:** menu.py


#### 🎀 Пучок с прядями у лица

**Ключ:** `h_updo_bun_with_framing`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a bun with loose face-framing strands.\n" Soft romantic look.
```

**Источник:** menu.py


#### 🪮 Рваная чёлка

**Ключ:** `h_bangs_choppy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add textured choppy bangs.\n" Uneven ends, light look.
```

**Источник:** menu.py


#### 🕰 Ретро

**Ключ:** `h_style_retro`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply retro hairstyle styling.\n" Inspired by classic vintage aesthetics.\n" Structured waves or classic forms.
```

**Источник:** menu.py


#### 💕 Романтический стиль

**Ключ:** `h_style_romantic`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply a romantic hairstyle styling.\n" Soft texture, gentle movement.\n" Light waves or softness around the face.\n" Delicate and airy mood.
```

**Источник:** menu.py


#### 🧵 Рыбий хвост

**Ключ:** `h_braids_fishtail`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a fishtail braid.\n" Detailed fine weaving.
```

**Источник:** menu.py


#### 🧵 Свободная небрежная коса

**Ключ:** `h_braids_loose_messy`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a loose messy braid.\n" Soft, relaxed texture.
```

**Источник:** menu.py


#### ⚡ Современный

**Ключ:** `h_style_modern`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply modern hairstyle styling.\n" Trendy texture, contemporary presentation.\n" Balanced volume and clean finish.
```

**Источник:** menu.py


#### 🌊 Средняя длина с мягкими волнами

**Ключ:** `h_medium_waves`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a medium-length hairstyle with soft waves.\n" Natural loose waves, relaxed look.
```

**Источник:** menu.py


#### 🌊 Средняя длина с объёмом

**Ключ:** `h_medium_volume`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a medium-length hairstyle with added volume.\n" Lifted roots, airy structure.
```

**Источник:** menu.py


#### 🌊 Средняя длина с слоями

**Ключ:** `h_medium_layered`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a medium-length layered haircut.\n" Soft layers for movement and depth.
```

**Источник:** menu.py


#### 🌊 Текстурная средняя длина

**Ключ:** `h_medium_textured`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a textured medium-length haircut.\n" Light layers, natural flow.
```

**Источник:** menu.py


#### 🪵 Уголь

**Ключ:** `as_style_tech_charcoal`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity.\n" Apply charcoal drawing technique,\n" rough expressive strokes,\n" deep shadows,\n" textured paper.\n" Dramatic monochrome result.
```

**Источник:** menu.py


#### 🪮 Удлинённая чёлка

**Ключ:** `h_bangs_long`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add long bangs.\n" Blending naturally into the hairstyle.
```

**Источник:** menu.py


#### 🌊 Удлинённый боб (LOB)

**Ключ:** `h_medium_lob`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a long bob (lob) haircut.\n" Length between chin and shoulders.
```

**Источник:** menu.py


#### 🧵 Французская коса

**Ключ:** `h_braids_french`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a French braid.\n" Tight weaving from the crown.
```

**Источник:** menu.py


#### ✂️ Французский боб

**Ключ:** `h_short_french_bob`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Apply a French bob haircut.\n" Slightly messy, natural, effortless Parisian style.
```

**Источник:** menu.py


#### 💻 Цифровая живопись

**Ключ:** `as_style_tech_digital_painting`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply digital painting technique,\n" smooth brushwork,\n" detailed lighting,\n" high-resolution textures.\n" Professional digital artwork.
```

**Источник:** menu.py


#### 🖋 Чернила / тушь

**Ключ:** `as_style_tech_ink`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" For portraits, preserve facial identity.\n" Apply ink drawing technique,\n" bold black lines,\n" high contrast,\n" hand-inked illustration style.\n" Crisp, graphic result.
```

**Источник:** menu.py


#### 🪮 Чёлка-шторка

**Ключ:** `h_bangs_curtain`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Only change the hairstyle.\n" Maintain realistic hair texture, volume and proportions.\n" Photorealistic result.\n" Add curtain bangs.\n" Split in the center, soft framing.
```

**Источник:** menu.py


#### 👑 Элегантный стиль

**Ключ:** `h_style_elegant`

**Цена:** 30 баллов

**Промпт:**
```
Use the original photo as the primary reference.\n" Preserve the face, facial features, head shape, expression and identity exactly.\n" Do NOT change the face or facial structure.\n" Do NOT change hair color.\n" Do NOT change the hairstyle structure, length or haircut shape.\n" Apply only styling, mood and finishing details.\n" Photorealistic result.\n" Apply an elegant hairstyle styling.\n" Polished finish, controlled volume.\n" Refined and sophisticated look.
```

**Источник:** menu.py


#### ⚔️ ⚔️ Akihiko Yoshida Style

**Ключ:** `as_style_akihiko_yoshida`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply anime character design style inspired by Akihiko Yoshida,\n" clean expressive lineart,\n" balanced anime proportions,\n" soft shading,\n" fantasy RPG character aesthetics.\n" High quality anime character illustration.
```

**Источник:** menu.py


#### ⚔️ ⚔️ Frank Frazetta

**Ключ:** `as_style_frank_frazetta`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply epic fantasy painting style inspired by Frank Frazetta,\n" powerful heroic anatomy,\n" dramatic dynamic poses,\n" rich earthy colors,\n" bold expressive brushstrokes,\n" classic heroic fantasy atmosphere.\n" High quality fantasy illustration.
```

**Источник:** menu.py


#### ⚔️ ⚔️ Genndy Tartakovsky

**Ключ:** `as_style_genndy_tartakovsky`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original composition of the image.\n" Apply animation style inspired by Genndy Tartakovsky,\n" strong silhouettes,\n" minimalistic shapes,\n" flat colors,\n" dramatic contrast.\n" Stylized animated illustration.
```

**Источник:** menu.py


#### ⚡ ⚡ Helmut Newton

**Ключ:** `as_style_helmut_newton`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Helmut Newton,\n" high contrast black and white,\n" provocative fashion poses,\n" dramatic lighting,\n" strong geometric composition.\n" High quality stylized photograph.
```

**Источник:** menu.py


#### ⚡ ⚡ Jim Lee (Modern DC / Marvel)

**Ключ:** `as_style_jim_lee`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply modern comic art style inspired by Jim Lee,\n" sharp detailed linework,\n" dynamic poses,\n" dramatic lighting.\n" High quality comic book illustration.
```

**Источник:** menu.py


#### ✨ ✨ Richard Avedon

**Ключ:** `as_style_richard_avedon`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Richard Avedon,\n" clean white background,\n" studio lighting,\n" minimalist composition,\n" sharp detailed facial features.\n" High quality professional portrait.
```

**Источник:** menu.py


#### 🌌 🌌 Moebius (Jean Giraud)

**Ключ:** `as_style_moebius`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity.\n" Apply comic art style inspired by Moebius (Jean Giraud),\n" clean precise linework,\n" soft pastel colors,\n" surreal and detailed environments.\n" High quality comic illustration.
```

**Источник:** menu.py


#### 🌍 🌍 Sebastião Salgado

**Ключ:** `as_style_sebastiao_salgado`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Sebastião Salgado,\n" dramatic black and white photography,\n" high contrast,\n" strong emphasis on texture and emotion,\n" documentary realism,\n" natural lighting.\n" High quality fine art photograph.
```

**Источник:** menu.py


#### 🌍 🌍 Steve McCurry

**Ключ:** `as_style_steve_mccurry`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Steve McCurry,\n" vivid saturated colors,\n" documentary realism,\n" natural lighting,\n" authentic and expressive subjects.\n" High quality realistic photograph.
```

**Источник:** menu.py


#### 🌑 🌑 Frank Miller (Noir / Sin City)

**Ключ:** `as_style_frank_miller`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" For portraits, preserve facial identity.\n" Apply noir comic style inspired by Frank Miller,\n" high contrast black and white,\n" sharp shadows,\n" minimal color accents.\n" Dramatic graphic illustration.
```

**Источник:** menu.py


#### 🌙 🌙 CLAMP Style

**Ключ:** `as_style_clamp`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity in stylized anime form.\n" Apply anime style inspired by CLAMP,\n" long slender proportions,\n" large expressive eyes,\n" decorative details,\n" elegant and dramatic anime aesthetics.\n" High quality stylized anime illustration.
```

**Источник:** menu.py


#### 🌸 🌸 Makoto Shinkai Style

**Ключ:** `as_style_makoto_shinkai`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity, facial features and proportions.\n" Do not change the pose or expression.\n" Apply anime style inspired by Makoto Shinkai,\n" highly detailed background,\n" cinematic lighting,\n" soft glowing light,\n" realistic anime proportions,\n" vivid colors and atmospheric depth.\n" High quality anime illustration.
```

**Источник:** menu.py


#### 🍃 🍃 Studio Ghibli Style (Hayao Miyazaki)

**Ключ:** `as_style_studio_ghibli`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and natural proportions.\n" Do not exaggerate facial features.\n" Apply Studio Ghibli animation style inspired by Hayao Miyazaki,\n" soft hand-drawn look,\n" warm natural colors,\n" gentle lighting,\n" simple expressive character design.\n" High quality anime-style illustration.
```

**Источник:** menu.py


#### 🎨 🎨 Alex Ross (Painterly Realism)

**Ключ:** `as_style_alex_ross`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions exactly.\n" Apply painterly comic style inspired by Alex Ross,\n" realistic anatomy,\n" soft dramatic lighting,\n" traditional painted texture.\n" High quality realistic comic artwork.
```

**Источник:** menu.py


#### 🎭 🎭 Tim Walker

**Ключ:** `as_style_tim_walker`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Tim Walker,\n" fantastical fashion photography,\n" surreal and imaginative atmosphere,\n" bold colors,\n" creative set design,\n" cinematic lighting.\n" High quality artistic photograph.
```

**Источник:** menu.py


#### 🏔 🏔 Ansel Adams

**Ключ:** `as_style_ansel_adams`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Ansel Adams,\n" black and white photography,\n" high sharpness and clarity,\n" strong tonal range,\n" emphasis on light, shadow and depth,\n" fine art landscape aesthetic.\n" High quality fine art photograph.
```

**Источник:** menu.py


#### 🏰 🏰 Disney Renaissance Style

**Ключ:** `as_style_disney_renaissance`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply Disney Renaissance animation style,\n" clean expressive linework,\n" warm vibrant colors,\n" classic hand-drawn animation look.\n" High quality cartoon illustration.
```

**Источник:** menu.py


#### 🏰 🏰 John Blanche

**Ключ:** `as_style_john_blanche`

**Цена:** 30 баллов

**Промпт:**
```
Apply grimdark fantasy art style inspired by John Blanche,\n" chaotic composition,\n" raw sketchy textures,\n" dark medieval atmosphere.
```

**Источник:** menu.py


#### 🐉 🐉 Brom

**Ключ:** `as_style_brom`

**Цена:** 30 баллов

**Промпт:**
```
Apply dark fantasy art style inspired by Brom,\n" moody lighting,\n" gothic atmosphere,\n" dark painterly textures.
```

**Источник:** menu.py


#### 🐰 🐰 Looney Tunes / Chuck Jones

**Ключ:** `as_style_looney_tunes`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" Apply classic Looney Tunes cartoon style inspired by Chuck Jones,\n" exaggerated expressions,\n" bold outlines,\n" bright flat colors,\n" playful cartoon proportions.\n" High quality cartoon illustration.
```

**Источник:** menu.py


#### 🐲 🐲 DreamWorks Style

**Ключ:** `as_style_dreamworks`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original structure of the image.\n" For portraits, preserve facial identity.\n" Apply DreamWorks animation style,\n" expressive facial features,\n" dynamic poses,\n" cinematic lighting,\n" stylized proportions.\n" High quality cartoon illustration.
```

**Источник:** menu.py


#### 💥 💥 Jack Kirby (Classic Marvel)

**Ключ:** `as_style_jack_kirby`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply comic art style inspired by Jack Kirby,\n" bold dynamic lines,\n" powerful anatomy,\n" bright saturated colors,\n" classic Marvel aesthetic.\n" High quality comic illustration.
```

**Источник:** menu.py


#### 📸 📸 Annie Leibovitz

**Ключ:** `as_style_annie_leibovitz`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Annie Leibovitz,\n" dramatic lighting,\n" carefully composed portrait,\n" moody background,\n" professional studio or location setting.\n" High quality cinematic photograph.
```

**Источник:** menu.py


#### 📸 📸 Mario Testino

**Ключ:** `as_style_mario_testino`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Mario Testino,\n" fashion editorial photography,\n" clean elegant composition,\n" soft professional studio lighting,\n" natural yet polished look,\n" vibrant but balanced colors.\n" High quality fashion photograph.
```

**Источник:** menu.py


#### 🔥 🔥 Wayne Barlowe

**Ключ:** `as_style_wayne_barlowe`

**Цена:** 30 баллов

**Промпт:**
```
Apply dark fantasy illustration style inspired by Wayne Barlowe,\n" alien demonic forms,\n" otherworldly environments,\n" high detail.
```

**Источник:** menu.py


#### 🕊 🕊 Dorothea Lange

**Ключ:** `as_style_dorothea_lange`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Dorothea Lange,\n" documentary photography,\n" emotional and human-centered composition,\n" natural lighting,\n" authentic realistic atmosphere,\n" soft tonal contrast.\n" High quality documentary photograph.
```

**Источник:** menu.py


#### 🖤 🖤 Peter Lindbergh

**Ключ:** `as_style_peter_lindbergh`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply photographic style inspired by Peter Lindbergh,\n" black and white portrait,\n" soft natural lighting,\n" minimalistic background,\n" timeless fashion photography aesthetic.\n" High quality artistic photograph.
```

**Источник:** menu.py


#### 🚀 🚀 Ralph McQuarrie

**Ключ:** `as_style_ralph_mcquarrie`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply fantasy concept art style inspired by Ralph McQuarrie,\n" cinematic lighting,\n" soft painterly brushwork,\n" atmospheric sci-fi fantasy environments,\n" concept art aesthetics.\n" High quality cinematic fantasy artwork.
```

**Источник:** menu.py


#### 🤖 🤖 Pixar Style

**Ключ:** `as_style_pixar`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply Pixar-style 3D animation look,\n" soft lighting,\n" rounded shapes,\n" detailed textures,\n" friendly expressive character design.\n" High quality stylized 3D render.
```

**Источник:** menu.py


#### 🧙 🧙 Greg Rutkowski

**Ключ:** `as_style_greg_rutkowski`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply high-fantasy digital painting style inspired by Greg Rutkowski,\n" detailed character design,\n" dramatic lighting,\n" epic fantasy atmosphere,\n" highly detailed textures.\n" High quality fantasy illustration.
```

**Источник:** menu.py


#### 🪄 🪄 Magali Villeneuve

**Ключ:** `as_style_magali_villeneuve`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original content and structure of the image.\n" For portraits, preserve facial identity and proportions.\n" Apply fantasy illustration style inspired by Magali Villeneuve,\n" elegant character design,\n" soft cinematic lighting,\n" refined painterly details,\n" magical fantasy atmosphere.\n" High quality fantasy artwork.
```

**Источник:** menu.py


#### 🪽 🪽 Yoshitaka Amano Style

**Ключ:** `as_style_yoshitaka_amano`

**Цена:** 30 баллов

**Промпт:**
```
Preserve the original composition of the image.\n" For portraits, preserve facial identity in artistic and stylized form.\n" Apply anime illustration style inspired by Yoshitaka Amano,\n" delicate elegant linework,\n" elongated forms,\n" pastel and watercolor tones,\n" ornamental fantasy aesthetics.\n" High quality artistic anime illustration.
```

**Источник:** menu.py



## 3. Специальные промпты

### 👔 Fitting Room (Примерочная)

**Промпт:**
```
Use photo 1 as the primary subject reference. " Preserve the face, facial features, skin texture, head shape and overall identity from photo 1 exactly. " IMPORTANT: Preserve the entire body figure, body shape, body proportions, pose, and silhouette from photo 1. " The body structure, physique, and physical build must come from photo 1, not from photo 2. " Use photo 2 as clothing reference only. " Take only the clothing item from photo 2. " Do not transfer the person, face, body shape, body figure, pose, physique, silhouette, hair or background from photo 2. " Dress the person from photo 1 in the clothing from photo 2, keeping the body figure from photo 1. " Ensure the clothing fits naturally to the body proportions and figure of the person from photo 1. " Maintain realistic fabric folds, texture, proportions and lighting. " Do not change the hairstyle, face, facial expression, body shape, body figure, or pose from photo 1. " Photorealistic result, high realism, natural lighting.
```

**Источник:** menu.py (fitting room)



## 4. Кастомные промпты пользователей

Пользователи могут создавать свои собственные промпты через функцию "✍️ Свой промпт".

Эти промпты хранятся в базе данных в таблице `jobs` и не имеют предопределенных шаблонов.

Для просмотра кастомных промптов используйте скрипт `view_custom_prompts.py`.


## Статистика

- **Промпты из базы данных:** 16

- **Промпты из menu.py:** 153

- **Специальные промпты:** 1

- **Всего предопределенных промптов:** 170
