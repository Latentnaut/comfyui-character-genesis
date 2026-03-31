# PORTRAIT MASTER
# Created by AI Wiz Art (Stefano Flore)
# Version: 3.5.0
# https://stefanoflore.it
# https://ai-wiz.art

import os
import re
import random
import json
# Robust import handling for ComfyUI environments
import sys
try:
    from .legacy import PortraitMaster
    from .utils import pmReadTxt, applyWeight
except (ImportError, ValueError, SystemError):
    node_path = os.path.dirname(__file__)
    if node_path not in sys.path:
        sys.path.append(node_path)
    from legacy import PortraitMaster
    from utils import pmReadTxt, applyWeight

script_dir = os.path.dirname(__file__)
presets_dir = os.path.join(script_dir, "presets")

# global vars

rand_opt = 'random 🎲'

# Load custom database (Unified items and descriptions)
custom_db_path = os.path.join(script_dir, "lists/custom_casting_db.json")

def load_custom_db():
    if os.path.exists(custom_db_path):
        try:
            with open(custom_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

custom_db = load_custom_db()

# Migration logic: Move old .txt items and custom_descriptions.json to custom_db
def migrate_to_unified_db():
    global custom_db
    changed = False
    old_desc_path = os.path.join(script_dir, "lists/custom_descriptions.json")
    
    # 1. Load old descriptions
    old_descs = {}
    if os.path.exists(old_desc_path):
        try:
            with open(old_desc_path, 'r', encoding='utf-8') as f:
                old_descs = json.load(f)
        except Exception: pass

    list_names = [
        "eyes_color", "eyes_shape", "eyes_details", "skin_tone", "skin_features", "bone_structure", "casting_archetype", "face_expression"
    ]
    
    for name in list_names:
        if name not in custom_db: custom_db[name] = {}
        
        # Load descriptions from old file
        if name in old_descs:
            for item, desc in old_descs[name].items():
                if item not in custom_db[name] or custom_db[name][item] != desc:
                    custom_db[name][item] = desc
                    changed = True
        
        # Load custom items from .txt files (anything not in builtin)
        # Note: This is tricky because we don't easily know what's builtin vs custom without checking original file content.
        # But for now, any item with a description in old_descs is definitely custom.

    if changed:
        with open(custom_db_path, 'w', encoding='utf-8') as f:
            json.dump(custom_db, f, indent=4)
    
    # Clean up old file
    if os.path.exists(old_desc_path):
        try: os.remove(old_desc_path)
        except: pass

migrate_to_unified_db()

def load_lists():
    lists = {}
    list_names = [
        "shot", "gender", "face_shape", "face_expression", "nationality", "hair_style", "light_type", "light_direction", "eyes_color", "eyes_shape", "beard_color", "hair_color", "hair_length", "body_type", "beard", "model_pose", "style", "lips_shape", "lips_color", "makeup", "clothes", "age", "makeup_color", "female_lingerie", "breast_size", "butt_size", "casting_market", "casting_brand", "casting_medium", "skin_tone", "skin_features", "eyes_details", "bone_structure", "casting_archetype"
    ]
    for name in list_names:
        list_path = os.path.join(script_dir, f"lists/{name}_list.txt")
        # Start with standard list items
        items = pmReadTxt(list_path) if os.path.exists(list_path) else []
        # Add custom items from JSON DB
        if name in custom_db:
            items.extend(custom_db[name].keys())
        # Clean and sort
        lists[name] = sorted(list(set(items)))
    return lists

lists = load_lists()


CASTING_ARCHETYPES = {
    "Classic Commercial (Female)": "symmetrical features, girl-next-door beauty, flawless glowing skin, relatable natural look, classic beauty standards, commercial fashion model",
    "Classic Commercial (Male)": "handsome male model, symmetrical balanced features, approachable, classic male grooming, commercial lifestyle model",
    "High Fashion / Edgy (Female)": "sharp bone structure, striking high cheekbones, defined angular jawline, piercing gaze, severe beauty, high fashion editorial model, edgy aesthetic",
    "High Fashion / Gaunt (Male)": "gaunt sculpted face, hyper-defined jawline, hollow cheeks, intense editorial look, high fashion male model, striking bone structure",
    "Baby Face / Doll-like (Female)": "youthful doll-like face, large expressive eyes, soft rounded cheeks, full pouty lips, innocent gaze, neotenous features, petite features",
    "Baby Face / Boyish (Male)": "boyish youthful face, soft features, large expressive eyes, clean-shaven, youthful male model, innocent charm",
    "Blank Canvas / Chameleon (Female)": "neutral balanced facial features, versatile face, smooth skin, blank expression, minimalist beauty, effortless high fashion model",
    "Blank Canvas / Chameleon (Male)": "versatile male face, balanced features, neutral expression, clean-shaven or light stubble, professional model, adaptable look",
    "Alien / Otherworldly (Female)": "unconventional striking facial features, wide-set eyes, alien-like beauty, otherworldly ethereal look, avant-garde high fashion model, unique proportions",
    "Alien / Otherworldly (Male)": "unique alien-like male features, unconventional proportions, striking bone structure, otherworldly gaze, avant-garde male model",
    "Striking / Street Cast (Female)": "interesting face, memorable distinctive facial features, imperfect unique beauty, strong confident presence, street casting model, raw aesthetic",
    "Striking / Street Cast (Male)": "memorable male face, rugged or distinctive features, strong character, authentic street casting look, unique masculine presence",
    "Androgynous (Feminine Lean)": "androgynous model with feminine lean, delicate genderless beauty, soft striking bone structure, graceful fluid aesthetic",
    "Androgynous (Masculine Lean)": "androgynous model with masculine lean, sharp angular features, gender fluid appearance, boyish high fashion look, striking bone structure",
    "Languid / Melancholic (Female)": "melancholic weary gaze, pale skin, romantic and tired expression, gaunt slender face, delicate bone structure, ethereal emotional presence, heroin-chic aesthetic",
    "Languid / Melancholic (Male)": "non-aggressive weak appearance, melancholy deep-set eyes, languid and weary facial expression, delicate features, vulnerable and sensitive male presence, soft melancholic vibe",
    "The Muse / Romantic (Female)": "graceful and sensual, ethereal beauty, soft feminine features, romantic historical-inspired aesthetic, elegant and poised",
    "The Muse / Poetic (Male)": "ethereal and soft male beauty, romantic poetic expression, delicate bone structure, sensitive and graceful presence",
    "The Rebel / Edgy (Female)": "fierce independent look, non-conformist, luxury-grunge aesthetic, piercing gaze, defiant high-fashion posture",
    "The Rebel / Gritty (Male)": "rugged non-conformist male, edgy and raw aesthetic, intense independent gaze, street-inspired luxury look",
    "The Sage / Classic (Female)": "timeless elegance, quiet luxury, intellectual discernment, sophisticated poised look, mature and refined beauty",
    "The Sage / Classic (Male)": "distinguished timeless elegance, mature intellectual presence, sophisticated quiet luxury look, commanding yet refined",
    "The Hero / Powerful (Female)": "radiating strength and mastery, empowered structural presence, athletic and determined look, high-fashion warrior aesthetic",
    "The Hero / Athletic (Male)": "strong goal-oriented male presence, athletic and powerful build, commanding physical mastery, structural high-fashion look",
    "The Innocent / Natural (Female)": "purity and authenticity, clean-girl aesthetic, effortless no-makeup look, gentle and earth-conscious vibe",
    "The Innocent / Natural (Male)": "authentic and pure male face, clean-boy aesthetic, approachable and natural look, soft and honest expression",
    "Gamine / Neotenous (Female)": "youthful gamine features, large expressive eyes, mischievous yet elegant, mischievous neotenous charm, high-fashion pixie aesthetic",
    "Gamine / Youthful (Male)": "youthful and boyish male features, lithe and graceful build, neotenous charm, playful yet sophisticated editorial look",
    "Aristocratic / Regal (Female)": "noble and high-born features, haughty regal beauty, cold elegance, sharp symmetrical bone structure, elite luxury aesthetic",
    "Aristocratic / Regal (Male)": "distinguished noble male features, haughty aristocratic presence, sharp and symmetrical beauty, elite and commanding luxury look"
}

CASTING_MARKETS = {
    "High Fashion & Luxury Editorial": "avant-garde styling, elite luxury aesthetic, high artistic value, cutting-edge trends",
    "Haute Couture": "exclusive custom-fitted clothing, high-end craftsmanship, theatrical and opulent presentation",
    "Commercial Lifestyle": "relatable everyday aesthetic, bright lighting, accessible and friendly vibe",
    "Domestic & Family Retail": "warm and comforting atmosphere, practical and durable clothing, wholesome appeal",
    "Swimwear & Lingerie": "confident body positivity, sensual yet tasteful presentation, focus on fit and form",
    "Fitness & Sportswear": "dynamic active poses, athletic and energetic look, performance-oriented aesthetic",
    "Beauty & Cosmetics Close-up": "flawless extreme close-up, highly detailed skin texture, focus on makeup and facial symmetry",
    "Streetwear & Urban Editorial": "gritty authentic urban environment, edgy youth culture, casual yet stylish",
    "Avant-Garde / Experimental Art": "pushing visual boundaries, unconventional framing, surreal and conceptual",
    "Corporate Stock & Institutional": "professional polished appearance, structured and trustworthy, standard business attire",
    "Teen & Youth Apparel": "vibrant youthful energy, trend-focused casual wear, rebellious yet fun",
    "Mature Lifestyle": "elegant aging, sophisticated and comfortable, distinguished and poised",
    "Magazine Cover Shot": "striking powerful close-up portrait, direct intense eye contact, sophisticated editorial framing",
    "Beauty Shot": "macro extreme close-up of face, flawless micro skin texture, focus on makeup artist precision"
}

CASTING_BRANDS = {
    "Gucci": "eclectic, romantic, and retro-inspired luxury with maximalist patterns",
    "Prada": "intellectual fashion, minimalist yet eccentric, modern and sophisticated",
    "Balenciaga": "subversive streetwear meets high fashion, dramatic proportions, dystopian chic",
    "Chanel": "timeless elegance, tweed fabrics, classic sophistication and refined luxury",
    "Louis Vuitton": "heritage travel luxury, iconic monogram canvas, high-end exclusive appeal",
    "Saint Laurent": "rock-chic glamor, dark and sharp tailoring, Parisian cool and edgy",
    "Zara": "fast-fashion commercial trends, accessible high-street style, clean and modern",
    "H&M": "casual everyday fashion, versatile basics, sustainable and young demographic",
    "Target": "family-friendly, bright and colorful, cheerful domestic retail",
    "Nike": "high-performance athletic wear, dynamic swoosh aesthetic, motivational and active",
    "Adidas": "iconic three-stripe sports heritage, urban athleisure, classic and clean",
    "Supreme": "hyper-exclusive streetwear, bold red box logo, skate culture and youth rebellion",
    "Off-White": "industrial-inspired streetwear, quotation marks, urban high fashion",
    "Victoria's Secret": "glamorous lingerie, bombshell beauty standard, romantic and alluring",
    "Fenty Beauty": "inclusive cosmetics, glowing skin and bold makeup, modern and diverse",
    "MAC Cosmetics": "professional bold makeup artistry, high-pigment colors, studio-ready looks",
    "Sephora": "premium beauty retail, sleek and black-and-white aesthetic, trendy and curated",
    "L'Oréal": "commercial beauty standards, classic elegance, accessible perfection",
    "Dior": "romantic and feminine high fashion, floral motifs, classic Parisian luxury",
    "Hermès": "ultra-luxury equestrian heritage, flawless leather goods, quiet and timeless wealth",
    "Versace": "bold flamboyant prints, excessive luxury, sexy and powerful Italian glamour",
    "Givenchy": "dark romanticism, aristocratic elegance, gothic-infused high fashion"
}

CASTING_MEDIUMS = {
    "Magazine Cover Shot": "striking powerful close-up portrait, direct intense eye contact, sophisticated editorial framing",
    "Beauty Shot": "macro extreme close-up of face, flawless micro skin texture, focus on makeup artist precision"
}

CASTING_AGE_DIVISIONS = {
    "Infant / Baby": {"range": (0, 2), "desc": "Newborn to toddler, soft features, large eyes, innocent neotenous look"},
    "Child / Junior": {"range": (3, 12), "desc": "Pre-adolescent youth, playful energy, growing features"},
    "Teen": {"range": (13, 17), "desc": "Adolescent look, coming-of-age aesthetic, youthful rebellion"},
    "New Face": {"range": (16, 21), "desc": "Elite high fashion board, fresh-faced, blank canvas with high symmetry"},
    "Young Adult": {"range": (18, 25), "desc": "Commercial and fashion bridge, aspirational young adult look"},
    "Main Board": {"range": (25, 35), "desc": "Professional established look, physical peak, mature features"},
    "Classic": {"range": (35, 50), "desc": "Sophisticated mature beauty, established character, refined elegance"},
    "Silver": {"range": (50, 80), "desc": "Distinguished senior look, silver-haired grace, timeless character"}
}

CASTING_SKIN_TONES = {
    "Fitzpatrick I / Porcelain": "Extremely fair skin, translucent quality, cool pink undertones, high light reactivity",
    "Fitzpatrick II / Ivory": "Fair skin, neutral balanced undertones, clear and luminous photographic quality",
    "Fitzpatrick III / Golden": "Light-medium skin, warm golden/peachy undertones, sun-kissed commercial look",
    "Fitzpatrick IV / Olive": "Medium skin with distinct greenish/yellowish olive undertones, Mediterranean / Latin aesthetic",
    "Fitzpatrick V / Caramel": "Rich brown skin, warm golden undertones, luminous and vibrant deep glow",
    "Fitzpatrick V-VI / Mahogany": "Deep dark brown skin, neutral or cool red/blue undertones, rich mahogany finish",
    "Fitzpatrick VI / Espresso": "Deepest rich espresso skin tone, high melanin density, velvet-like photographic texture"
}

CASTING_SKIN_FEATURES = {
    "Albinism (Pale / Milky)": "Extremely pale milk-white skin, translucent quality, high light sensitivity, ethereal and otherworldly presence",
    "Vitiligo (Graphic / Striking)": "Distinct de-pigmented patches, high-contrast graphic patterns, unique skin geometry, striking and memorable presence",
    "Hyper-Freckled (Raw / Character)": "Dense and high-contrast ephelis patterns across the face, sun-kissed raw texture, rustic character model look",
    "Glass Skin (Asian Beauty)": "Hyper-smooth surface, seemingly translucent, high-gloss dewy finish, ultra-hydrated and minimalist aesthetic",
    "Weathered / Sun-Damaged": "Leather-like texture, sun-induced character lines, rugged authentic appearance, aged by the elements",
    "Iridescent / Pearlized": "Subtle pearlescent sheen, multi-dimensional light reflection, radiant and futuristic skin finish",
    "Hyperpigmentation (Mottled)": "Natural uneven dark patches, graphic and interesting texture, authentic non-uniform beauty representation"
}

CASTING_BONE_STRUCTURES = {
    "Strong Mandibular Line": "High-definition jawline, sharp angles, masculine/athletic aesthetic.",
    "Pronounced Cheekbones": "High zygomatic arches, creates natural shadows, ideal for contouring.",
    "Deep-set Eyes": "Prominent brow bone, intense gaze, creates dramatic lighting shadows.",
    "Asymmetric Jaw": "Subtle natural unevenness, provides character and realism to portraits.",
    "Crooked Nose Bridge": "Non-perfect nose line, breaks symmetry for a unique 'character' model look.",
    "Sharp Orbital Bone": "Strictly defined eye sockets, creates high-fashion 'predatory' or intense look.",
    "Narrow Face Shape": "Elongated facial structure, often associated with high-fashion and runway models."
}

CASTING_EYE_COLORS = {
    "Deep Obsidian / Midnight": "Concentrated dark melanin pigment, structural depth, reflects high-density richness.",
    "Cognac / Honey Amber": "Warm golden/honey hues, rich amber vibrancy, luminous crystalline texture.",
    "Icy Blue / Steel Blue": "Desaturated cool tones, high-fashion winter aesthetic, piercing crystalline clarity.",
    "Jade / Emerald Green": "Saturated green iris, rich forest depth, striking contrast with all skin tones.",
    "Slate / Storm Grey": "Neutral cloudy grey, sophisticated muted tones, elegant soft lens contrast.",
    "Violet / Amethyst": "Extremely rare amethyst/orchid hue, otherworldly ethereal beauty, high-end creative casting.",
    "Hazel / Multi-tonal": "Complex mosaic of gold, green, and brown; dynamic light reflectivity.",
    "Complete Heterochromia": "Two naturally different colored eyes (e.g., one blue, one brown), top-tier rare model trait.",
    "Sectoral Heterochromia": "Segmented patch of different color in one iris, highly striking and memorable.",
    "Central Heterochromia (Halo)": "Dual-tone iris with a contrasting central ring around the pupil, crown-like effect."
}

CASTING_EYE_SHAPES = {
    "Almond Eyes": "Balanced horizontal/vertical axis, classic high-fashion symmetry.",
    "Upturned / Cat-Eye": "Outer corners tilted upwards, predatory and intense editorial gaze.",
    "Hooded Eyes": "Deep skin fold over the eyelid, creates a mysterious and focused intensity.",
    "Monolid": "Sleek architectural look without a lid crease, common in East Asian editorials.",
    "Deep-set Eyes": "Recessed within the orbit, creating dramatic shadows under the brow bone.",
    "Doe Eyes / Round": "Large vertical opening, neotenous neotenous innocent charm, expressive and soft.",
    "Wide-set Eyes": "Increased distance between eyes, ethereal and alien-like high-fashion vibe.",
    "Downturned / Sad": "Outer corners tilted downwards, melancholic and romantic poetic expression.",
    "Epicanthic Folds": "Distinctive skin fold of the upper eyelid covering the inner corner, vital for precise East Asian anatomy."
}

CASTING_EYE_DETAILS = {
    "Thick Limbal Ring": "Dark defined ring at iris edge, youthful high-contrast photographic appearance.",
    "Visible Iris Crypts": "Petal-shaped indentations on iris surface, providing deep organic macro texture.",
    "Collarette (Zigzag)": "Intricate line separating the pupillary and ciliar iris zones, extreme macro fidelity.",
    "Wolfflin Nodules": "Tiny pale spots on the iris periphery, common in light-colored eyes for realism.",
    "Contraction Furrows": "Concentric wavy lines in the iris following pupil dilation, adding volume.",
    "Sclera Vascularization": "Fine, almost imperceptible micro-capillaries in the white of the eye for biological realism.",
    "Lacrimal Detail": "Enriched pinkish volume in the inner corner (Caruncle) with clear moisture accumulation.",
    "Waterline Reflection": "High-gloss specular highlight along the lower eyelid edge (Wet-line).",
    "Glossy Cornea / Catchlights": "Hyper-clear corneal surface, reflects professional studio light sources.",
    "Anisocoria (Split Pupils)": "Slightly mismatched pupil sizes, adds raw intensity and biological realism.",
    "Coloboma (Keyhole)": "Rare keyhole-shaped pupil, highly unique and avant-garde character casting."
}

CASTING_EXPRESSIONS = {
    "Smoldering Gaze": "Intense focused eye contact, slightly furrowed brow, conveying confidence and allure.",
    "Mischievous Hint": "Playful smirk, direct eye contact with a hint of knowing complicity, alluring and charismatic.",
    "Stoic Mastery / Blank": "Neutral high-fashion expression, blank canvas, effortless composure, radiating professional authority.",
    "Languid / Melancholic": "Weary deep-set gaze, soft vulnerability, romantic and tired expression, poetic emotional presence.",
    "The Rebel / Defiant": "Fierce independent look, intense non-conformist energy, piercing and slightly predatory gaze.",
    "Ethereal / Dreamy": "Soft unfocused gaze, looking slightly away, creating a sense of wonder and otherworldly mystery.",
    "Subtle Smirk": "Focus on the mouth, slight asymmetrical upturn, suggesting a secret or playful thought.",
    "Vulnerable / Raw": "Wide-set expressive eyes, soft facial tension, authentic and honest beauty representation.",
    "Half-lidded (The Gaze)": "Upper eyelids partially closed, creating a sleepy but intense 'Vogue' editorial look."
}

CASTING_HAIR_STYLES = {
    "Sleek High Ponytail": "tightly pulled back, smooth finish, emphasizes bone structure",
    "Wet-look Slicked Back": "glossy editorial texture, gel-refined structure, sharp minimalist appeal",
    "Soft Beach Waves": "natural volume, effortless texture, sun-kissed commercial vibe",
    "Sharp Bob / Chin-length": "precise architectural cut, high-symmetry, sophisticated editorial look",
    "Buzz Cut": "minimalist structural exposure, emphasizing scalp texture and skull shape",
    "Messy Bedhead / Grunge": "untamed organic texture, luxury grunge aesthetic, rebellious and raw",
    "Classic Taper (Male)": "clean grooming, professional male model standard, balanced proportions",
    "Afro-textured (Natural)": "high-volume organic structure, rich coily texture, celebrating heritage beauty",
    "Braided / Cornrows": "intricate geometric patterns, cultural high-fashion expression, sharp linear detail"
}

CASTING_HAIR_COLORS = {
    "Platinum Blonde": "high-contrast icy tone, luxury bleach finish, striking editorial presence",
    "Natural Espresso": "deep rich melanin-dense brown, high-gloss natural depth",
    "Copper Red": "vibrant warm metallic hues, striking contrast with fair skin",
    "Silver Fox / Grey": "distinguished aging, elegant natural transition, sophisticated profile",
    "Pastel Pink / Creative": "avant-garde color science, soft dreamy tone, high-end creative market"
}

CASTING_BEARDS = {
    "Heavy Stubble (3-day)": "sharply defined follicles, rugged masculine texture, professional grooming",
    "Clean-shaven": "flawless jawline exposure, high-fidelity skin micro-texture visible on the chin",
    "Short Boxed Beard": "architectural grooming, refined contours, enhancing mandibular strength",
    "Designer Van Dyke": "precise goatee with disconnected mustache, eccentric luxury aesthetic"
}

CASTING_MAKEUP = {
    "No-Makeup Look": "high-fidelity natural skin texture, subtle hydration, zero visible cosmetics",
    "Smokey Eyes": "dark dramatic eyeshadow, intense orbital depth, high-fashion nighttime editorial",
    "Bold Red Lip": "saturated crimson pigment, precise application, classic high-luxury focal point",
    "Glossy Editorial Dewy": "wet-finish highlights, strategic moisture, hyper-reflective skin surface",
    "Graphic Eyeliner": "sharp architectural lines, avant-garde framing, precise symmetry"
}

def merge_trait_list(name, hardcoded_dict):
    existing = lists.get(name, [])
    combined = list(set(existing) | set(hardcoded_dict.keys()))
    combined.sort()
    lists[name] = combined

merge_trait_list('casting_archetype', CASTING_ARCHETYPES)
merge_trait_list('casting_market', CASTING_MARKETS)
merge_trait_list('casting_brand', CASTING_BRANDS)
merge_trait_list('casting_medium', CASTING_MEDIUMS)
merge_trait_list('age', CASTING_AGE_DIVISIONS)
merge_trait_list('skin_tone', CASTING_SKIN_TONES)
merge_trait_list('skin_features', CASTING_SKIN_FEATURES)
merge_trait_list('bone_structure', CASTING_BONE_STRUCTURES)
merge_trait_list('eyes_color', CASTING_EYE_COLORS)
merge_trait_list('eyes_shape', CASTING_EYE_SHAPES)
merge_trait_list('eyes_details', CASTING_EYE_DETAILS)
merge_trait_list('face_expression', CASTING_EXPRESSIONS)
merge_trait_list('hair_style', CASTING_HAIR_STYLES)
merge_trait_list('hair_color', CASTING_HAIR_COLORS)
merge_trait_list('beard', CASTING_BEARDS)
merge_trait_list('makeup', CASTING_MAKEUP)



# ─── Probabilistic multi-select parser ────────────────────────────────────
# Syntax accepted in any trait text field:
#   '-' or ''           → disabled / return None
#   '*'                 → random choice from full available list
#   'España'            → always España
#   'España, México'    → 50 / 50 random choice
#   'España 80, México' → 80% España, 20% México (remainder distributed)
#   'España 80, México 20' → explicit weights
def parse_weighted_field(text, available_list=None):
    if not text:
        return None
    text = text.strip()
    if text in ('', '-'):
        return None
    if text == '*':
        return random.choice(available_list) if available_list else None

    entries = [e.strip() for e in text.split(',') if e.strip()]
    values, weights, unweighted_idx = [], [], []
    total_explicit = 0.0

    for i, entry in enumerate(entries):
        m = re.match(r'^(.+?)\s+(\d+(?:\.\d+)?)\s*$', entry)
        if m:
            values.append(m.group(1).strip())
            w = float(m.group(2))
            weights.append(w)
            total_explicit += w
        else:
            values.append(entry)
            weights.append(None)
            unweighted_idx.append(i)

    remaining = max(0.0, 100.0 - total_explicit)
    auto_w = (remaining / len(unweighted_idx)) if unweighted_idx else 0.0
    for i in unweighted_idx:
        weights[i] = auto_w if auto_w > 0 else (100.0 / len(values))

    total = sum(weights)
    if total == 0:
        return random.choice(values)
    return random.choices(values, weights=[w / total for w in weights], k=1)[0]


# ─── API endpoint — lets the JS frontend fetch trait option lists ───────────
try:
    from server import PromptServer
    from aiohttp import web

    @PromptServer.instance.routes.get('/chargenesis/traits/{trait_name}')
    async def chargenesis_trait_list(request):
        trait_name = request.match_info['trait_name']
        if trait_name in lists:
            # Hardcoded descriptions for standard items
            hc_dicts = {
                'casting_archetype': CASTING_ARCHETYPES,
                'casting_market': CASTING_MARKETS,
                'casting_brand': CASTING_BRANDS,
                'age': {k: v['desc'] for k,v in CASTING_AGE_DIVISIONS.items()},
                'skin_tone': CASTING_SKIN_TONES,
                'skin_features': CASTING_SKIN_FEATURES,
                'bone_structure': CASTING_BONE_STRUCTURES,
                'eyes_color': CASTING_EYE_COLORS,
                'eyes_shape': CASTING_EYE_SHAPES,
                'eyes_details': CASTING_EYE_DETAILS,
                'face_expression': CASTING_EXPRESSIONS,
                'hair_style': CASTING_HAIR_STYLES,
                'hair_color': CASTING_HAIR_COLORS,
                'beard': CASTING_BEARDS,
                'makeup': CASTING_MAKEUP
            }
            
            # Start with hardcoded
            desc_map = dict(hc_dicts.get(trait_name, {}))
            
            # Merge custom overrides from database
            if trait_name in custom_db:
                desc_map.update(custom_db[trait_name])
                
            return web.json_response({'items': lists[trait_name], 'descriptions': desc_map})
        return web.json_response({'items': [], 'descriptions': {}, 'error': 'unknown trait'}, status=404)

    @PromptServer.instance.routes.post('/chargenesis/traits/{trait_name}')
    async def chargenesis_trait_edit(request):
        global lists, custom_db
        trait_name = request.match_info['trait_name']
        data = await request.json()
        action = data.get('action') # "add", "delete", "edit"
        value = data.get('value', '').strip()
        description = data.get('description', '').strip()
        old_value = data.get('old_value', '').strip()
        
        if trait_name not in lists:
             return web.json_response({'error': 'Unknown trait type'}, status=404)

        try:
            if trait_name not in custom_db:
                custom_db[trait_name] = {}
            
            if action == 'add' and value:
                custom_db[trait_name][value] = description
            elif action == 'delete' and value:
                if value in custom_db[trait_name]:
                    del custom_db[trait_name][value]
            elif action == 'edit' and value and old_value:
                desc = description or custom_db[trait_name].get(old_value, "")
                if old_value in custom_db[trait_name]:
                    del custom_db[trait_name][old_value]
                custom_db[trait_name][value] = desc
                
            # Save unified database
            with open(custom_db_path, 'w', encoding='utf-8') as f:
                json.dump(custom_db, f, indent=4)
                
            # Refreshes lists
            lists = load_lists()
            
            # Re-merge with hardcoded lists to keep everything in sync
            hardcoded_map = {
                'casting_archetype': CASTING_ARCHETYPES,
                'casting_market': CASTING_MARKETS,
                'casting_brand': CASTING_BRANDS,
                'casting_medium': CASTING_MEDIUMS,
                'age': CASTING_AGE_DIVISIONS,
                'skin_tone': CASTING_SKIN_TONES,
                'skin_features': CASTING_SKIN_FEATURES,
                'bone_structure': CASTING_BONE_STRUCTURES,
                'eyes_color': CASTING_EYE_COLORS,
                'eyes_shape': CASTING_EYE_SHAPES,
                'eyes_details': CASTING_EYE_DETAILS,
                'face_expression': CASTING_EXPRESSIONS
            }
            if trait_name in hardcoded_map:
                lists[trait_name] = sorted(list(set(lists[trait_name]) | set(hardcoded_map[trait_name].keys())))

            return web.json_response({'success': True, 'items': lists[trait_name]})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

except Exception:
    pass  # headless / test mode

# Load presets
def get_presets(preset_class):
    if not os.path.exists(presets_dir):
        return []

    class_presets_dir = os.path.join(presets_dir, preset_class)
    if not os.path.exists(class_presets_dir):
        return []

    files = [f for f in os.listdir(class_presets_dir) if f.endswith('.json')]
    return [os.path.splitext(f)[0] for f in files]

# Generic preset logic handler
def handle_presets(node_instance, **kwargs):
    params = {k: v for k, v in kwargs.items()}

    # Saving
    if params.get("save_preset") and params.get("save_preset_as"):
        preset_name = params["save_preset_as"].strip()
        if preset_name:
            preset_data = {k: v for k, v in params.items() if k not in ['text_in', 'seed', 'load_preset', 'save_preset_as', 'save_preset', '_presets_separator']}

            class_presets_dir = os.path.join(presets_dir, node_instance.preset_class)
            if not os.path.exists(class_presets_dir):
                os.makedirs(class_presets_dir)

            filepath = os.path.join(class_presets_dir, f"{preset_name}.json")
            with open(filepath, 'w') as f:
                json.dump(preset_data, f, indent=4)
            print(f"Saved preset to {filepath}")

    # Loading
    if params.get("load_preset") and params.get("load_preset") != "-- disabled --":
        preset_name = params["load_preset"]
        filepath = os.path.join(presets_dir, node_instance.preset_class, f"{preset_name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                preset_data = json.load(f)
            params.update(preset_data)
            print(f"Loaded preset from {filepath}")

    return params

# Portrait Master Base Character

class PortraitMasterBaseCharacter:
    preset_class = "BaseCharacter"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 2
        preset_files = get_presets(s.preset_class)

        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}), "seed": ("INT", {"forceInput": False})},
            "required": {
                "shot": (['-'] + [rand_opt] + lists['shot'], {"default": '-'}),
                "shot_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "gender": (['-'] + [rand_opt] + lists['gender'], {"default": '-'}),
                "androgynous": ("FLOAT", {"default": 0, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "ugly": ("FLOAT", {"default": 0, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "ordinary_face": ("FLOAT", {"default": 0, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "age": (['-'] + [rand_opt] + lists['age'], {"default": '-'}),
                "nationality_1": (['-'] + [rand_opt] + lists['nationality'], {"default": '-'}),
                "nationality_2": (['-'] + [rand_opt] + lists['nationality'], {"default": '-'}),
                "nationality_mix": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.05, "display": "slider"}),
                "body_type": (['-'] + [rand_opt] + lists['body_type'], {"default": '-'}),
                "body_type_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "breast_size": (['-'] + [rand_opt] + lists['breast_size'], {"default": '-'}),
                "breast_size_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "butt_size": (['-'] + [rand_opt] + lists['butt_size'], {"default": '-'}),
                "butt_size_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "eyes_color": (['-'] + [rand_opt] + lists['eyes_color'], {"default": '-'}),
                "eyes_shape": (['-'] + [rand_opt] + lists['eyes_shape'], {"default": '-'}),
                "lips_color": (['-'] + [rand_opt] + lists['lips_color'], {"default": '-'}),
                "lips_shape": (['-'] + [rand_opt] + lists['lips_shape'], {"default": '-'}),
                "facial_expression": (['-'] + [rand_opt] + lists['face_expression'], {"default": '-'}),
                "facial_expression_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "face_shape": (['-'] + [rand_opt] + lists['face_shape'], {"default": '-'}),
                "face_shape_weight": ("FLOAT", {"default": 1, "step": 0.05, "min": 0, "max": max_float_value, "display": "slider"}),
                "facial_asymmetry": ("FLOAT", {"default": 0, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "hair_style": (['-'] + [rand_opt] + lists['hair_style'], {"default": '-'}),
                "hair_color": (['-'] + [rand_opt] + lists['hair_color'], {"default": '-'}),
                "hair_length": (['-'] + [rand_opt] + lists['hair_length'], {"default": '-'}),
                "disheveled": ("FLOAT", {"default": 0, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "beard": (['-'] + [rand_opt] + lists['beard'], {"default": '-'}),
                "beard_color": (['-'] + [rand_opt] + lists['beard_color'], {"default": '-'}),
                "active": ("BOOLEAN", {"default": True}),
                "load_preset": (["-- disabled --"] + preset_files, ),
                "save_preset_as": ("STRING", {"default": ""}),
                "save_preset": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pmbc"
    CATEGORY = "Character Genesis"

    def pmbc(self, **kwargs):
        params = handle_presets(self, **kwargs)

        text_in=params.get('text_in','')
        shot=params.get('shot','-')
        shot_weight=params.get('shot_weight',1)
        gender=params.get('gender','-')
        androgynous=params.get('androgynous',0)
        ugly=params.get('ugly',0)
        ordinary_face=params.get('ordinary_face',0)
        age=params.get('age',30)
        nationality_1=params.get('nationality_1','-')
        nationality_2=params.get('nationality_2','-')
        nationality_mix=params.get('nationality_mix',0.5)
        body_type=params.get('body_type','-')
        body_type_weight=params.get('body_type_weight',1)
        breast_size=params.get('breast_size','-')
        breast_size_weight=params.get('breast_size_weight',1)
        butt_size=params.get('butt_size','-')
        butt_size_weight=params.get('butt_size_weight',1)
        eyes_color=params.get('eyes_color','-')
        eyes_shape=params.get('eyes_shape','-')
        lips_color=params.get('lips_color','-')
        lips_shape=params.get('lips_shape','-')
        facial_expression=params.get('facial_expression','-')
        facial_expression_weight=params.get('facial_expression_weight',1)
        face_shape=params.get('face_shape','-')
        face_shape_weight=params.get('face_shape_weight',1)
        facial_asymmetry=params.get('facial_asymmetry',0)
        hair_style=params.get('hair_style','-')
        hair_color=params.get('hair_color','-')
        hair_length=params.get('hair_length','-')
        disheveled=params.get('disheveled',0)
        beard=params.get('beard','-')
        beard_color=params.get('beard_color','-')
        active=params.get('active',True)

        prompt = []
        if text_in: prompt.append(text_in)
        if active:
            if shot_weight > 0:
                if shot == rand_opt: prompt.append(applyWeight(random.choice(lists['shot']),shot_weight))
                elif shot != '-': prompt.append(applyWeight(shot,shot_weight))
            gender_opt = ''
            if gender == rand_opt: gender_opt = random.choice(lists['gender']) + ' '
            elif gender != '-': gender_opt = gender + ' '
            age_opt = ''
            if age == rand_opt: age_opt = random.choice(lists['age']) + '-years-old '
            elif age != '-': age_opt = f'{age}-years-old '
            androgynous_opt = applyWeight('androgynous',androgynous) + ' ' if androgynous > 0 else ''
            ugly_opt = applyWeight('ugly',ugly) + ' ' if ugly > 0 else ''
            nationality = ''
            if nationality_1 != '-' or nationality_2 != '-':
                n1 = random.choice(lists['nationality']) if nationality_1 == rand_opt else nationality_1
                n2 = random.choice(lists['nationality']) if nationality_2 == rand_opt else nationality_2
                if n1 and n2 and n1 != '-' and n2 != '-': nationality = f'[{n1}:{n2}:{str(round(nationality_mix, 2))}] '
                else: nationality = (n1 if n1 != '-' else n2) + ' '
            if androgynous_opt or ugly_opt or nationality or gender_opt or age_opt:
                t = f'({androgynous_opt}{ugly_opt}{nationality}{gender_opt}{age_opt}:1.15)'.strip()
                prompt.append(t)
            if ordinary_face > 0: prompt.append(applyWeight('ordinary face',ordinary_face))
            if body_type_weight > 0:
                if body_type == rand_opt: prompt.append(applyWeight(random.choice(lists['body_type']) + ' body',body_type_weight))
                elif body_type != '-': prompt.append(applyWeight(body_type,body_type_weight) + ' body')
            if breast_size_weight > 0:
                if breast_size == rand_opt: prompt.append(applyWeight(random.choice(lists['breast_size']) + ' breasts',breast_size_weight))
                elif breast_size != '-': prompt.append(applyWeight(breast_size + ' breasts',breast_size_weight))
            if butt_size_weight > 0:
                if butt_size == rand_opt: prompt.append(applyWeight(random.choice(lists['butt_size']) + ' butt',butt_size_weight))
                elif butt_size != '-': prompt.append(applyWeight(butt_size + ' butt',butt_size_weight))
            if eyes_color == rand_opt: prompt.append(f"({random.choice(lists['eyes_color'])} eyes:1.05)")
            elif eyes_color != '-': prompt.append(f"({eyes_color} eyes:1.05)")
            if eyes_shape == rand_opt: prompt.append(f"({random.choice(lists['eyes_shape'])}:1.05)")
            elif eyes_shape != '-': prompt.append(f"({eyes_shape}:1.05)")
            if lips_color == rand_opt: prompt.append(f"({random.choice(lists['lips_color'])}:1.05)")
            elif lips_color != '-': prompt.append(f"({lips_color}:1.05)")
            if lips_shape == rand_opt: prompt.append(f"({random.choice(lists['lips_shape'])}:1.05)")
            elif lips_shape != '-': prompt.append(f"({lips_shape}:1.05)")
            if facial_expression_weight > 0:
                if facial_expression == rand_opt: prompt.append(applyWeight(f"{random.choice(lists['face_expression'])} expression",facial_expression_weight))
                elif facial_expression != '-': prompt.append(applyWeight(f"{facial_expression} expression",facial_expression_weight))
            if face_shape_weight > 0:
                if face_shape == rand_opt: prompt.append(applyWeight(f"{random.choice(lists['face_shape'])} face-shape",face_shape_weight))
                elif face_shape != '-': prompt.append(applyWeight(f"{face_shape} face-shape",face_shape_weight))
            if facial_asymmetry > 0: prompt.append(applyWeight('facial asymmetry, face asymmetry',facial_asymmetry))
            if hair_style == rand_opt: prompt.append(f"({random.choice(lists['hair_style'])} hair style:1.05)")
            elif hair_style != '-': prompt.append(f"({hair_style} hair style:1.05)")
            if hair_color == rand_opt: prompt.append(f"({random.choice(lists['hair_color'])} hair color:1.05)")
            elif hair_color != '-': prompt.append(f"({hair_color} hair color:1.05)")
            if hair_length == rand_opt: prompt.append(f"({random.choice(lists['hair_length'])} hair length:1.05)")
            elif hair_length != '-': prompt.append(f"({hair_length} hair length:1.05)")
            if disheveled > 0: prompt.append(applyWeight('disheveled',disheveled))
            if beard == rand_opt: prompt.append(f"({random.choice(lists['beard'])}:1.05)")
            elif beard != '-': prompt.append(f"({beard}:1.05)")
            if beard_color == rand_opt: prompt.append(f"({random.choice(lists['beard_color'])} beard color:1.05)")
            elif beard_color != '-': prompt.append(f"({beard_color} beard color:1.05)")
        return (', '.join(prompt).lower(),) if prompt else ('',)

# Character Portrait Base (Nanobanana Pro Optimized — Probabilistic Multi-Select)

class CharacterGenesisNode:
    preset_class = "CharacterGenesisNode"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 2
        preset_files = get_presets(s.preset_class)
        # Build hint strings for placeholder defaults
        casting_hint = ", ".join(lists['casting_archetype'][:3]) + "  |  Use: 'Baby Face / Doll-like 70, Alien / Otherworldly Beauty 30'"
        age_hint     = ", ".join(lists['age'][:4])    + "  |  Use: 'New Face 70, Young Adult 30'"
        nat_hint     = ", ".join(lists['nationality'][:4]) + "  |  Use: 'Spain 80, Mexico 20'"
        market_hint  = ", ".join(lists['casting_market'][:3]) + "  |  Use: 'High Fashion 70, Streetwear 30'"
        ec_hint      = ", ".join(lists['eyes_color'][:4])  + "  |  Multi: 'brown 60, green 40'"
        hs_hint      = ", ".join(lists['hair_style'][:3])  + "  |  Browse ↓ for full list"
        hc_hint      = ", ".join(lists['hair_color'][:3])  + "  |  Browse ↓"
        hl_hint      = ", ".join(lists['hair_length'])      + "  |  Use: 'short, medium'"
        st_hint      = ", ".join(lists['skin_tone'][:3])    + "  |  Use: 'Porcelain 80, Ivory 20'"
        sf_hint      = ", ".join(lists['skin_features'][:3])  + "  |  Use: 'Albinism 70, Glass Skin 30'"
        es_hint      = ", ".join(lists['eyes_shape'][:4])  + "  |  Use: 'Almond 70, Cat-eye 30'"
        ed_hint      = ", ".join(lists['eyes_details'][:3]) + "  |  e.g., Thick Limbal Ring, Iris Crypts"
        ex_hint      = ", ".join(lists['face_expression'][:3]) + "  |  Browse ↓"
        bd_hint      = ", ".join(lists['beard'][:3])        + "  |  Use: 'goatee 70, clean shaven 30'"
        bdc_hint     = ", ".join(lists['beard_color'][:3])  + "  |  Browse ↓"
        mk_hint      = ", ".join(lists['makeup'][:3])       + "  |  Browse ↓"
        mkc_hint     = ", ".join(lists['makeup_color'][:3]) + "  |  Browse ↓"
        bs_hint      = "Strong Mandibular Line, Pronounced Cheekbones, Deep-set Eyes  |  or Browse ↓"

        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}), "seed": ("INT", {"forceInput": False})},
            "required": {
                # ── Identity ──────────────────────────────────────────────
                "casting_archetype": ("STRING", {"multiline": False, "default": "",  "placeholder": casting_hint}),
                "age":         ("STRING", {"multiline": False, "default": "",        "placeholder": age_hint}),
                "nationality": ("STRING", {"multiline": False, "default": "",        "placeholder": nat_hint}),
                "skin_tone":   ("STRING", {"multiline": False, "default": "",        "placeholder": st_hint}),
                "skin_features": ("STRING", {"multiline": False, "default": "",      "placeholder": sf_hint}),
                "casting_market": ("STRING", {"multiline": False, "default": "",     "placeholder": market_hint}),
                "casting_brand":  ("STRING", {"multiline": False, "default": "",     "placeholder": "e.g., Gucci, Zara, Nike"}),
                # ── Bone / Asymmetry ──────────────────────────────────────
                "bone_structure":     ("STRING", {"multiline": False, "default": "", "placeholder": bs_hint}),
                # ── Skin / Eyes ───────────────────────────────────────────
                "eye_realism":  ("BOOLEAN", {"default": True}),
                "eyes_color":   ("STRING", {"multiline": False, "default": "",       "placeholder": ec_hint}),
                "eyes_shape":   ("STRING", {"multiline": False, "default": "",       "placeholder": es_hint}),
                "eyes_details": ("STRING", {"multiline": False, "default": "",       "placeholder": ed_hint}),
                # ── Hair ──────────────────────────────────────────────────
                "hair_style":  ("STRING", {"multiline": False, "default": "",        "placeholder": hs_hint}),
                "hair_color":  ("STRING", {"multiline": False, "default": "",        "placeholder": hc_hint}),
                "hair_length": ("STRING", {"multiline": False, "default": "",        "placeholder": hl_hint}),
                # ── Beard ─────────────────────────────────────────────────
                "beard_only_male": ("BOOLEAN", {"default": True}),
                "beard":       ("STRING", {"multiline": False, "default": "",        "placeholder": bd_hint}),
                "beard_color": ("STRING", {"multiline": False, "default": "",        "placeholder": bdc_hint}),
                # ── Makeup ────────────────────────────────────────────────
                "makeup_only_female": ("BOOLEAN", {"default": True}),
                "makeup":      ("STRING", {"multiline": False, "default": "",        "placeholder": mk_hint}),
                "makeup_color":("STRING", {"multiline": False, "default": "",        "placeholder": mkc_hint}),
                # ── Wardrobe ──────────────────────────────────────────────
                "strict_anatomy_wardrobe": ("BOOLEAN", {"default": True}),
                "clothing":    ("STRING", {"multiline": True,  "default": "Gucci silk scarf artfully draped around the shoulders, revealing a hint of cleavage. Dominant print featuring bold floral patterns and the iconic Gucci logo."}),
                # ── Nanobanana Pro JSON fields ────────────────────────────
                "task_description": ("STRING", {"multiline": True,  "default": "Act as a High-Fashion Casting Director for a top international agency. Generate a high-fidelity 1x1 luxury portrait based on professional casting descriptors. Pure #FFFFFF background vacuum. Frontal head-and-shoulders."}),
                "optics":           ("STRING", {"multiline": True,  "default": "Hasselblad H6D, 85mm f/5.6, ISO 800, pin-sharp focus on eyelashes."}),
                "lighting":         ("STRING", {"multiline": True,  "default": "Rembrandt pattern via Beauty Dish, soft, circular catchlights from a large softbox or window light. High-key white seamless studio backdrop with zero shadows."}),
                "post_processing":  ("STRING", {"multiline": True,  "default": "Kodak Portra 400 color science, warm highlights, creamy organic skin tones. Noritsu high-resolution negative scan rendering, 35mm organic film grain structure. Subtle light halation and slight chromatic aberration at the image edges."}),
                "expression":       ("STRING", {"multiline": False, "default": "", "placeholder": ex_hint}),
                # ── Node control ──────────────────────────────────────────
                "active":          ("BOOLEAN", {"default": True}),
                "load_preset":     (["-- disabled --"] + preset_files, ),
                "save_preset_as":  ("STRING", {"default": ""}),
                "save_preset":     ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "cpb"
    CATEGORY = "Character Genesis"

    def cpb(self, **kwargs):
        params = handle_presets(self, **kwargs)

        if not params.get('active', True):
            return ("",)

        # ── Nanobanana JSON fields ─────────────────────────────────────────
        task_description = params.get('task_description', 'Act as a High-Fashion Casting Director for a top international agency. Generate a high-fidelity 1x1 luxury portrait based on professional casting descriptors. Pure #FFFFFF background vacuum. Frontal head-and-shoulders.')
        optics           = params.get('optics',           'Hasselblad H6D, 85mm f/5.6, ISO 800, pin-sharp focus on eyelashes.')
        lighting         = params.get('lighting',         'Rembrandt pattern via Beauty Dish, soft, circular catchlights from a large softbox or window light. High-key white seamless studio backdrop with zero shadows.')
        post_processing  = params.get('post_processing',  'Kodak Portra 400 color science, warm highlights, creamy organic skin tones. Noritsu scan, 35mm organic grain.')
        expression       = params.get('expression',       'Playful, mischievous expression. Direct eye contact, conveying confidence and allure.')
        clothing_input   = params.get('clothing',         '')
        eye_realism          = params.get('eye_realism', True)
        strict_anatomy_wardrobe = params.get('strict_anatomy_wardrobe', True)

        # ── Probabilistic identity resolution ─────────────────────────────
        ca  = parse_weighted_field(params.get('casting_archetype', ''), lists['casting_archetype']) or 'Unspecified Archetype'
        st  = parse_weighted_field(params.get('skin_tone', ''), lists['skin_tone'])
        sf  = parse_weighted_field(params.get('skin_features', ''), lists['skin_features'])
        ex  = parse_weighted_field(params.get('expression', ''), lists['face_expression']) or 'Stoic Mastery / Blank'
        
        # Age resolution
        age_input = params.get('age', '')
        age_division = parse_weighted_field(age_input, lists['age'])
        
        # If the input is a raw number (or string mapping to number) like "25", we use it
        # Otherwise if it's one of our divisions, we randomize within its range
        age_res = age_division if age_division else "Adult"
        age_desc = ""
        
        if age_res in CASTING_AGE_DIVISIONS:
            div_info = CASTING_AGE_DIVISIONS[age_res]
            age_num = random.randint(div_info['range'][0], div_info['range'][1])
            a = f"{age_num} years old"
            age_desc = div_info['desc']
        else:
            # Fallback for manual numeric input
            a = age_res if "years old" in str(age_res).lower() else f"{age_res} years old"

        nat = parse_weighted_field(params.get('nationality', ''), lists['nationality']) or 'Unknown'
        cm  = parse_weighted_field(params.get('casting_market', ''), lists.get('casting_market', []))
        cb  = parse_weighted_field(params.get('casting_brand', ''), lists.get('casting_brand', []))
        bs  = parse_weighted_field(params.get('bone_structure', ''), lists['bone_structure'])

        ec  = parse_weighted_field(params.get('eyes_color', ''),  lists['eyes_color'])
        es  = parse_weighted_field(params.get('eyes_shape', ''),  lists['eyes_shape'])
        ed  = parse_weighted_field(params.get('eyes_details', ''), lists['eyes_details'])
        hs  = parse_weighted_field(params.get('hair_style', ''),  lists['hair_style'])
        hc  = parse_weighted_field(params.get('hair_color', ''),  lists['hair_color'])
        hl  = parse_weighted_field(params.get('hair_length', ''), lists['hair_length'])
        bd  = parse_weighted_field(params.get('beard', ''),       lists['beard'])
        bdc = parse_weighted_field(params.get('beard_color', ''), lists['beard_color'])
        mk  = parse_weighted_field(params.get('makeup', ''),      lists['makeup'])
        mkc = parse_weighted_field(params.get('makeup_color', ''),lists['makeup_color'])
        
        bom = params.get('beard_only_male', True)
        mof = params.get('makeup_only_female', True)

        age_str = a
        
        ca_desc = ""
        st_desc = ""
        sf_desc = ""
        ec_desc = ""
        es_desc = ""
        ed_desc = ""
        ex_desc = ""
        bs_desc = ""
        cm_desc = ""
        cb_desc = ""
        
        # Case-insensitive lookups for metadata injection (Always Included per Studio Standard)
        def get_desc(trait_name, value, hardcoded_dict):
            if not value: return ""
            v_lower = value.lower()
            # Check hardcoded first
            for k,v in hardcoded_dict.items():
                if v_lower == k.lower(): return f" ({v})"
            # Check custom database
            if trait_name in custom_db:
                for k,v in custom_db[trait_name].items():
                    if v_lower == k.lower(): return f" ({v})"
            return ""

        ca_desc = get_desc('casting_archetype', ca, CASTING_ARCHETYPES)
        st_desc = get_desc('skin_tone', st, CASTING_SKIN_TONES)
        sf_desc = get_desc('skin_features', sf, CASTING_SKIN_FEATURES)
        ec_desc = get_desc('eyes_color', ec, CASTING_EYE_COLORS)
        es_desc = get_desc('eyes_shape', es, CASTING_EYE_SHAPES)
        ed_desc = get_desc('eyes_details', ed, CASTING_EYE_DETAILS)
        ex_desc = get_desc('face_expression', ex, CASTING_EXPRESSIONS)
        bs_desc = get_desc('bone_structure', bs, CASTING_BONE_STRUCTURES)
        cm_desc = get_desc('casting_market', cm, CASTING_MARKETS)
        cb_desc = get_desc('casting_brand', cb, CASTING_BRANDS)
        
        hs_desc = get_desc('hair_style', hs, CASTING_HAIR_STYLES)
        hc_desc = get_desc('hair_color', hc, CASTING_HAIR_COLORS)
        bd_desc = get_desc('beard', bd, CASTING_BEARDS)
        mk_desc = get_desc('makeup', mk, CASTING_MAKEUP)

        # Special handling for age desc since it's a nested dict
        age_desc = ""
        if a in CASTING_AGE_DIVISIONS:
            age_desc = CASTING_AGE_DIVISIONS[a]['desc']
        elif 'age' in custom_db and a in custom_db['age']:
            age_desc = custom_db['age'][a]

        age_display = f"{age_str}"
        if age_desc: age_display += f" ({age_desc})"

        casting_heritage = (
            f"Archetype: {ca}{ca_desc}. "
            f"Skin Tone: {st if st else 'Natural'}{st_desc}. "
            f"Nationality: {nat.capitalize()}, Age: {age_display}. "
            f"Market: {cm if cm else 'Unspecified'}{cm_desc}. Brand: {cb if cb else 'Unspecified'}{cb_desc}. "
            "Radiating presence, embodying a sense of professional composure. "
            "Casting directive: luxury high-fashion editorial."
        )

        # ── Singular features (High-Fidelity Mandatory) ───────────────────
        sf_parts = []
        sf_parts.append(
            "Slightly asymmetrical lip fullness with a more pronounced Cupid's bow. "
            "Mild ptosis on one eye. Subtly uneven eyebrow height and jawline angle."
        )
        if sf:
            sf_parts.append(f"Unique skin phenotype: {sf}{sf_desc}.")
        if bs:
            sf_parts.append(f"Distinctive bone structure characterized by {bs}{bs_desc}.")
        singular_features = " ".join(sf_parts) if sf_parts else "Symmetric, standard features."

        # ── Micro detail (High-Fidelity Mandatory) ─────────────────────
        md_parts = []
        md_parts.append(
            "Visible skin pores at 1.2 magnification, particularly around the T-zone. "
            "Fine epidermal micro-texture evident across the forehead and cheeks. "
            "Noticeable facial peach fuzz around the hairline and jawline. "
            "Faint freckling and subtle micro-blemishes."
        )
        if eye_realism:
            md_parts.append(
                "Subtle micro-capillaries visible beneath the thin skin around the eyes. "
                "Realistic tear film on the eye surface with subtle corneal micro-reflections."
            )
        if ed:
            md_parts.append(f"Iris macro-detail: {ed}{ed_desc}.")
        micro_detail = " ".join(md_parts) if md_parts else "Smooth, airbrushed skin texture."

        # ── Face description ──────────────────────────────────────────────
        face_parts = []
        if ec or es:
            eye_desc_str = f"{ec if ec else ''} {es if es else ''}".strip()
            face_parts.append(f"{eye_desc_str} eyes{ec_desc}{es_desc}.".replace("  ", " ").strip().capitalize())
        
        face_parts.append(f"Expression: {ex}{ex_desc}.".capitalize())

        hair_desc_parts = filter(None, [hc, hl and hl + ' length', hs and 'styled as ' + hs])
        hair_desc = ', '.join(hair_desc_parts)
        if hair_desc: 
            desc_text = f"{hc_desc}{hs_desc}".replace(" (", "; ").replace(")", "")
            face_parts.append(f"{hair_desc.capitalize()} hair{desc_text}.")
        
        cal = ca.lower()
        is_female = any(x in cal for x in ['woman', 'girl', 'female'])
        is_male = any(x in cal for x in ['man', 'boy', 'male'])
        
        if bd:
            if not bom or is_male or not (is_female or is_male):
                face_parts.append(f"Features a {(bdc + ' ') if bdc else ''}{bd}{bd_desc}.")
        if mk:
            if not mof or is_female or not (is_female or is_male):
                face_parts.append(f"Wearing {(mkc + ' ') if mkc else ''}{mk} makeup{mk_desc}.")
                
        face_description = " ".join(face_parts)

        # ── Wardrobe ──────────────────────────────────────────────────────
        if strict_anatomy_wardrobe:
            cal = ca.lower()
            if any(x in cal for x in ['woman', 'girl', 'female']):
                clothing_desc = "Medium gray strapless top with a sweetheart neckline, leaving shoulders bare for full anatomical exposure. No jewelry, no distractions."
            elif any(x in cal for x in ['man', 'boy', 'male']):
                clothing_desc = "Medium gray ribbed tank top exposing the shoulders, neck, and trapezius muscles for highly realistic head-to-body connection. No jewelry, no distractions."
            else:
                clothing_desc = "Medium gray #808080 neutral unbranded apparel. No jewelry, no glasses."
        else:
            clothing_desc = clothing_input

        # ── Assemble JSON ─────────────────────────────────────────────────
        prompt_data = {
            "task": task_description,
            "identity_anatomy": {
                "casting_heritage": casting_heritage,
                "singular_features": singular_features,
                "micro_detail": micro_detail,
            },
            "technical_parameters": {
                "optics": optics,
                "lighting": lighting,
                "post_processing": post_processing,
            },
            "subject_details": {
                "face": face_description.strip() if face_description else "Average proportional face shape.",
                "clothing": clothing_desc,
                "expression": expression,
            },
            "verification": "Unique identity confirmed from text brief. Zero text, pure #FFFFFF vacuum.",
            "metadata": "4K RAW, Hasselblad rendering, absolute physical structure fidelity. Text-to-Image Optimized.",
        }

        text_in = params.get('text_in', '')
        if text_in:
            prompt_data["user_custom_instructions"] = text_in

        return (json.dumps(prompt_data, indent=2),)

# Portrait Master Skin Details

class PortraitMasterSkinDetails:
    preset_class = "SkinDetails"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 2
        preset_files = get_presets(s.preset_class)
        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}),"seed": ("INT", {"forceInput": False})},
            "required": {
                "natural_skin": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "bare_face": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "washed_face": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "dried_face": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "skin_details": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "skin_pores": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "dimples": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "wrinkles": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "freckles": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "moles": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "skin_imperfections": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "skin_acne": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "tanned_skin": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "eyes_details": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "iris_details": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "circular_iris": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "circular_pupil": ("FLOAT", {"default": 0,"min": 0,"max": max_float_value,"step": 0.05,"display": "slider"}),
                "active": ("BOOLEAN", {"default": True}),
                "load_preset": (["-- disabled --"] + preset_files, ),
                "save_preset_as": ("STRING", {"default": ""}),
                "save_preset": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pmsd"
    CATEGORY = "Character Genesis"

    def pmsd(self, **kwargs):
        params = handle_presets(self, **kwargs)
        text_in=params.get('text_in','')
        natural_skin=params.get('natural_skin',0)
        bare_face=params.get('bare_face',0)
        washed_face=params.get('washed_face',0)
        dried_face=params.get('dried_face',0)
        skin_details=params.get('skin_details',0)
        skin_pores=params.get('skin_pores',0)
        dimples=params.get('dimples',0)
        wrinkles=params.get('wrinkles',0)
        freckles=params.get('freckles',0)
        moles=params.get('moles',0)
        skin_imperfections=params.get('skin_imperfections',0)
        skin_acne=params.get('skin_acne',0)
        tanned_skin=params.get('tanned_skin',0)
        eyes_details=params.get('eyes_details',0)
        iris_details=params.get('iris_details',0)
        circular_iris=params.get('circular_iris',0)
        circular_pupil=params.get('circular_pupil',0)
        active=params.get('active',True)

        prompt = []
        if text_in: prompt.append(text_in)
        if active:
            if natural_skin > 0: prompt.append(applyWeight('natural skin',natural_skin))
            if bare_face > 0: prompt.append(applyWeight('bare face',bare_face))
            if washed_face > 0: prompt.append(applyWeight('washed-face',washed_face))
            if dried_face > 0: prompt.append(applyWeight('dried-face',dried_face))
            if skin_details > 0: prompt.append(applyWeight('detailed skin',skin_details))
            if skin_pores > 0: prompt.append(applyWeight('skin pores',skin_pores))
            if skin_imperfections > 0: prompt.append(applyWeight('skin imperfections',skin_imperfections))
            if skin_acne > 0: prompt.append(applyWeight('acne, skin with acne',skin_acne))
            if wrinkles > 0: prompt.append(applyWeight('wrinkles',wrinkles))
            if tanned_skin > 0: prompt.append(applyWeight('tanned skin',tanned_skin))
            if dimples > 0: prompt.append(applyWeight('dimples',dimples))
            if freckles > 0: prompt.append(applyWeight('freckles',freckles))
            if moles > 0: prompt.append(applyWeight('moles',moles))
            if eyes_details > 0: prompt.append(applyWeight('eyes details',eyes_details))
            if iris_details > 0: prompt.append(applyWeight('iris details',iris_details))
            if circular_iris > 0: prompt.append(applyWeight('circular details',circular_iris))
            if circular_pupil > 0: prompt.append(applyWeight('circular pupil',circular_pupil))
        return (', '.join(prompt).lower(),) if prompt else ('',)

# Portrait Master Style & Pose

class PortraitMasterStylePose:
    preset_class = "StylePose"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 2
        preset_files = get_presets(s.preset_class)
        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}), "seed": ("INT", {"forceInput": False})},
            "required": {
                "model_pose": (['-'] + [rand_opt] + lists['model_pose'], {"default": '-'}),
                "clothes": (['-'] + [rand_opt] + lists['clothes'], {"default": '-'}),
                "female_lingerie": (['-'] + [rand_opt] + lists['female_lingerie'], {"default": '-'}),
                "makeup": (['-'] + [rand_opt] + lists['makeup'], {"default": '-'}),
                "light_type": (['-'] + [rand_opt] + lists['light_type'], {"default": '-'}),
                "light_direction": (['-'] + [rand_opt] + lists['light_direction'], {"default": '-'}),
                "light_weight": ("FLOAT", {"default": 1, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "style_1": (['-'] + [rand_opt] + lists['style'], {"default": '-'}),
                "style_1_weight": ("FLOAT", {"default": 1, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "style_2": (['-'] + [rand_opt] + lists['style'], {"default": '-'}),
                "style_2_weight": ("FLOAT", {"default": 1, "min": 0, "max": max_float_value, "step": 0.05, "display": "slider"}),
                "photorealism_improvement": ("BOOLEAN", {"default": True}),
                "active": ("BOOLEAN", {"default": True}),
                "load_preset": (["-- disabled --"] + preset_files, ),
                "save_preset_as": ("STRING", {"default": ""}),
                "save_preset": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pmsp"
    CATEGORY = "Character Genesis"

    def pmsp(self, **kwargs):
        params = handle_presets(self, **kwargs)
        text_in=params.get('text_in','')
        model_pose=params.get('model_pose','-')
        clothes=params.get('clothes','-')
        female_lingerie=params.get('female_lingerie','-')
        makeup=params.get('makeup','-')
        light_type=params.get('light_type','-')
        light_direction=params.get('light_direction','-')
        light_weight=params.get('light_weight',1)
        style_1=params.get('style_1','-')
        style_1_weight=params.get('style_1_weight',1)
        style_2=params.get('style_2','-')
        style_2_weight=params.get('style_2_weight',1)
        photorealism_improvement=params.get('photorealism_improvement',False)
        active=params.get('active',True)

        prompt = []
        if text_in: prompt.append(text_in)
        if active:
            if makeup == rand_opt: prompt.append(f"({random.choice(lists['makeup'])}:1.05)")
            elif makeup != '-': prompt.append(f"({makeup}:1.05)")
            if model_pose == rand_opt: prompt.append(f"({random.choice(lists['model_pose'])}:1.25)")
            elif model_pose != '-': prompt.append(f"({model_pose}:1.25)")
            if clothes == rand_opt: prompt.append(f"({random.choice(lists['clothes'])}:1.25)")
            elif clothes != '-': prompt.append(f"({clothes}:1.25)")
            if female_lingerie == rand_opt: prompt.append(f"({random.choice(lists['female_lingerie'])}:1.25)")
            elif female_lingerie != '-': prompt.append(f"({female_lingerie}:1.25)")
            if light_type == rand_opt: prompt.append(applyWeight(random.choice(lists['light_type']),light_weight))
            elif light_type != '-': prompt.append(applyWeight(light_type,light_weight))
            if light_direction == rand_opt: prompt.append(applyWeight(random.choice(lists['light_direction']),light_weight))
            elif light_direction != '-': prompt.append(applyWeight(light_direction,light_weight))
            if style_1 == rand_opt: prompt.append(applyWeight(random.choice(lists['style']),style_1_weight))
            elif style_1 != '-': prompt.append(applyWeight(style_1,style_1_weight))
            if style_2 == rand_opt: prompt.append(applyWeight(random.choice(lists['style']),style_2_weight))
            elif style_2 != '-': prompt.append(applyWeight(style_2,style_2_weight))
            if photorealism_improvement: prompt.append('(professional photo, balanced photo, balanced exposure:1.2)')
        return (', '.join(prompt).lower(),) if prompt else ('',)

# Portrait Master Makeup

class PortraitMasterMakeup:
    preset_class = "Makeup"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        max_float_value = 2
        preset_files = get_presets(s.preset_class)
        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}), "seed": ("INT", {"forceInput": False})},
            "required": {
                "makeup_style": (['-'] + [rand_opt] + lists['makeup'], {"default": '-'}),
                "makeup_color": (['-'] + [rand_opt] + lists['makeup_color'], {"default": '-'}),
                "eyeshadow": ("BOOLEAN", {"default": False}),
                "eyeliner": ("BOOLEAN", {"default": False}),
                "mascara": ("BOOLEAN", {"default": False}),
                "blush": ("BOOLEAN", {"default": False}),
                "lipstick": ("BOOLEAN", {"default": False}),
                "lip_gloss": ("BOOLEAN", {"default": False}),
                "active": ("BOOLEAN", {"default": True}),
                "load_preset": (["-- disabled --"] + preset_files, ),
                "save_preset_as": ("STRING", {"default": ""}),
                "save_preset": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pmmk"
    CATEGORY = "Character Genesis"

    def pmmk(self, **kwargs):
        params = handle_presets(self, **kwargs)
        text_in=params.get('text_in','')
        makeup_style=params.get('makeup_style','-')
        makeup_color=params.get('makeup_color','-')
        eyeshadow=params.get('eyeshadow',False)
        eyeliner=params.get('eyeliner',False)
        mascara=params.get('mascara',False)
        blush=params.get('blush',False)
        lipstick=params.get('lipstick',False)
        lip_gloss=params.get('lip_gloss',False)
        active=params.get('active',True)

        prompt = []
        if text_in: prompt.append(text_in)
        if active:
            if makeup_style == rand_opt: prompt.append(f"({random.choice(lists['makeup'])}:1.05)")
            elif makeup_style != '-': prompt.append(f"({makeup_style}:1.05)")
            if makeup_color == rand_opt: prompt.append(f"({random.choice(lists['makeup_color'])} make-up color:1.05)")
            elif makeup_color != '-': prompt.append(f"({makeup_color} make-up color:1.05)")
            if eyeshadow: prompt.append("(eyeshadow make-up:1.05)")
            if eyeliner: prompt.append("(eyeliner make-up:1.05)")
            if mascara: prompt.append("(mascara make-up:1.05)")
            if blush: prompt.append("(blush make-up:1.05)")
            if lipstick: prompt.append("(lipstick make-up:1.05)")
            if lip_gloss: prompt.append("(lip gloss make-up:1.05)")
        return (', '.join(prompt).lower(),) if prompt else ('',)

# Portrait Master Face Generator

class PortraitMasterFaceGenerator:
    preset_class = "FaceGenerator"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        preset_files = get_presets(s.preset_class)
        return {
            "optional": {"text_in": ("STRING", {"forceInput": True}), "seed": ("INT", {"forceInput": False})},
            "required": {
                "gender": (['-'] + [rand_opt] + lists['gender'], {"default": '-'}),
                "age": (['-'] + [rand_opt] + lists['age'], {"default": '-'}),
                "nationality": (['-'] + [rand_opt] + lists['nationality'], {"default": '-'}),
                "body_type": (['-'] + [rand_opt] + lists['body_type'], {"default": '-'}),
                "eyes_color": (['-'] + [rand_opt] + lists['eyes_color'], {"default": '-'}),
                "hair_style": (['-'] + [rand_opt] + lists['hair_style'], {"default": '-'}),
                "hair_color": (['-'] + [rand_opt] + lists['hair_color'], {"default": '-'}),
                "hair_length": (['-'] + [rand_opt] + lists['hair_length'], {"default": '-'}),
                "beard": (['-'] + [rand_opt] + lists['beard'], {"default": '-'}),
                "beard_color": (['-'] + [rand_opt] + lists['beard_color'], {"default": '-'}),
                "active": ("BOOLEAN", {"default": True}),
                "load_preset": (["-- disabled --"] + preset_files, ),
                "save_preset_as": ("STRING", {"default": ""}),
                "save_preset": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pmfg"
    CATEGORY = "Character Genesis"

    def pmfg(self, **kwargs):
        params = handle_presets(self, **kwargs)
        
        text_in = params.get('text_in', '')
        gender = params.get('gender', '-')
        age = params.get('age', '-')
        nationality = params.get('nationality', '-')
        body_type = params.get('body_type', '-')
        eyes_color = params.get('eyes_color', '-')
        hair_style = params.get('hair_style', '-')
        hair_color = params.get('hair_color', '-')
        hair_length = params.get('hair_length', '-')
        beard = params.get('beard', '-')
        beard_color = params.get('beard_color', '-')
        active = params.get('active', True)

        prompt = []
        if text_in: 
            prompt.append(text_in)
        
        if active:
            # Base setup per volto frontale simmetrico
            prompt.append("front view portrait")
            prompt.append("symmetrical face")
            prompt.append("neutral expression")
            prompt.append("white background")
            prompt.append("soft diffused lighting")
            
            # Caratteristiche del personaggio
            character_parts = []
            
            # Genere
            if gender == rand_opt:
                character_parts.append(random.choice(lists['gender']).lower())
            elif gender != '-':
                character_parts.append(gender.lower())
            
            # Età
            if age == rand_opt:
                character_parts.append(f"{random.choice(lists['age'])}-years-old")
            elif age != '-':
                character_parts.append(f"{age}-years-old")
            
            # Nazionalità
            if nationality == rand_opt:
                character_parts.append(random.choice(lists['nationality']).lower())
            elif nationality != '-':
                character_parts.append(nationality.lower())
            
            # Tipo di corpo
            if body_type == rand_opt:
                character_parts.append(f"{random.choice(lists['body_type']).lower()} body")
            elif body_type != '-':
                character_parts.append(f"{body_type.lower()} body")
            
            if character_parts:
                prompt.append(" ".join(character_parts))
            
            # Colore occhi
            if eyes_color == rand_opt:
                prompt.append(f"{random.choice(lists['eyes_color']).lower()} eyes")
            elif eyes_color != '-':
                prompt.append(f"{eyes_color.lower()} eyes")
            
            # Stile capelli
            if hair_style == rand_opt:
                prompt.append(f"{random.choice(lists['hair_style']).lower()} hair style")
            elif hair_style != '-':
                prompt.append(f"{hair_style.lower()} hair style")
            
            # Colore capelli
            if hair_color == rand_opt:
                prompt.append(f"{random.choice(lists['hair_color']).lower()} hair")
            elif hair_color != '-':
                prompt.append(f"{hair_color.lower()} hair")
            
            # Lunghezza capelli
            if hair_length == rand_opt:
                prompt.append(f"{random.choice(lists['hair_length']).lower()} hair length")
            elif hair_length != '-':
                prompt.append(f"{hair_length.lower()} hair length")
            
            # Barba
            if beard == rand_opt:
                prompt.append(random.choice(lists['beard']).lower())
            elif beard != '-':
                prompt.append(beard.lower())
            
            # Colore barba
            if beard_color == rand_opt:
                prompt.append(f"{random.choice(lists['beard_color']).lower()} beard")
            elif beard_color != '-':
                prompt.append(f"{beard_color.lower()} beard")
        
        return (', '.join(prompt),) if prompt else ('',)


# Portrait Master Prompt Styler

class PortraitMasterPromptStyler:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_in": ("STRING", {"forceInput": True}),
                "style": (["descriptive", "cinematic", "illustrative", "artistic", "documentary", "fashion"], {"default": "descriptive"}),
                "add_extra_instructions": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_out",)
    FUNCTION = "pm_prompt_styler"
    CATEGORY = "Character Genesis"

    def pm_prompt_styler(self, text_in, style="descriptive", add_extra_instructions=True):
        tags = [t.strip() for t in text_in.split(',') if t.strip()]
        clean_tags = []
        for tag in tags:
            if '(' in tag and ')' in tag:
                content = tag.split('(')[1].split(')')[0]
                if ':' in content: content = content.split(':')[0].strip()
                clean_tags.append(content)
            else: clean_tags.append(tag)
        clean_tags = list(dict.fromkeys(clean_tags))
        style_prompts = {
            "descriptive": "A detailed photo of {subject} including the following features: {description}.",
            "cinematic": "Cinematic photo of {subject}, {description}, dramatic lighting, cinematic composition.",
            "illustrative": "Illustration of {subject}, {description}, suitable for concept art or digital illustration.",
            "artistic": "{subject} portrayed artistically with the following traits: {description}. Rich details and textures.",
            "documentary": "Documentary-style photograph of {subject} showing: {description}. Natural lighting, realistic scene.",
            "fashion": "Fashion editorial shot of {subject}, {description}, stylish pose, professional photography."
        }
        subject = "a person"
        for tag in clean_tags:
            if any(x in tag for x in ['girl', 'woman', 'female']): subject = "a woman"
            elif any(x in tag for x in ['boy', 'man', 'male']): subject = "a man"
            elif 'young' in tag: subject = f"a young {subject}"
        description = ", ".join(clean_tags)
        prompt_base = style_prompts.get(style, style_prompts['descriptive'])
        final_prompt = prompt_base.format(subject=subject, description=description)
        if add_extra_instructions: final_prompt += " Photorealistic, high resolution, dynamic lighting, intricate details."
        return (final_prompt,)

WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "CharacterGenesisNode": CharacterGenesisNode,
    "CG_PortraitMasterBaseCharacter": PortraitMasterBaseCharacter,
    "CG_PortraitMasterSkinDetails": PortraitMasterSkinDetails,
    "CG_PortraitMasterStylePose": PortraitMasterStylePose,
    "CG_PortraitMasterMakeup": PortraitMasterMakeup,
    "CG_PortraitMasterPromptStyler": PortraitMasterPromptStyler,
    "CG_PortraitMasterFaceGenerator": PortraitMasterFaceGenerator,
    "CG_PortraitMaster": PortraitMaster,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterGenesisNode": "Character Genesis (Nanobanana Pro)",
    "CG_PortraitMasterBaseCharacter": "Character Genesis: Base Character",
    "CG_PortraitMasterSkinDetails": "Character Genesis: Skin Details",
    "CG_PortraitMasterStylePose": "Character Genesis: Style & Pose",
    "CG_PortraitMasterMakeup": "Character Genesis: Make-up",
    "CG_PortraitMasterPromptStyler": "Character Genesis: Prompt Styler",
    "CG_PortraitMasterFaceGenerator": "Character Genesis: Face Generator",
    "CG_PortraitMaster": "Character Genesis (Legacy)",
}
