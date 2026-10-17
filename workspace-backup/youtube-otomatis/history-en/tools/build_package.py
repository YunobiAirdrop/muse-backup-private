#!/usr/bin/env python3
"""Build the 2026-10-05 script package for history-en (Fall of Constantinople 1453)."""
import json, os, re

BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
for d in ("script", "beats", "gambar", "shorts"):
    os.makedirs(os.path.join(BASE, d), exist_ok=True)

STYLE = ("Epic digital 2D storybook illustration, 16:9 widescreen, painterly, "
         "cinematic dramatic lighting, rich historical detail, no text, no watermark:")

# (chapter or None, narration text, image scene description)
DATA = [
# ---------------- CHAPTER 1: The City of Emperors ----------------
("The City of Emperors",
 "For eleven centuries, one glittering city stood proudly as the beating heart of the ancient civilized world.",
 "Golden sunrise aerial panorama over Constantinople, domes of Hagia Sophia glowing, sea walls and harbor, seagulls in the sky"),
(None,
 "Constantinople, fortress and palace and cathedral, rising like a golden mirage between two great continents of earth.",
 "Low-angle view of Hagia Sophia domes and imperial palaces rising above the city walls, dramatic morning light, painterly detail"),
(None,
 "The great domes of Hagia Sophia caught the sunrise while the crowded harbor sheltered a thousand proud ships below.",
 "Wide harbor scene at dawn, hundreds of ships anchored in the Golden Horn, domes silhouetted against a radiant sky"),
(None,
 "Kings, crusaders, and caliphs all hungered for its mighty walls, and every single one of them failed utterly.",
 "Distant wide shot of past siege armies retreating from the walls, tattered banners in the wind, storm clouds gathering"),
(None,
 "For the city was guarded by the mightiest fortifications ever raised by the hands of mortal men.",
 "Dramatic low-angle view of the massive triple Theodosian Walls, tiny soldiers on the ramparts, epic scale"),
(None,
 "Three concentric walls of solid stone rose high above the land, all ringed by a deep and wide moat.",
 "Aerial view at dusk of the triple walls and water-filled moat stretching to the horizon, torches on the battlements"),
(None,
 "No army had ever breached those proud walls, and no conqueror had ever planted his flag inside them.",
 "Empty battlefield before the unbroken walls at twilight, abandoned siege ladders, wind blowing dust, solemn mood"),
(None,
 "But empires, like mortal men, grow old, and the year fourteen fifty-three would test everything they were.",
 "Melancholic sunset over Constantinople, old imperial statue in the foreground, long shadows, painterly"),
(None,
 "This is the true story of the greatest and most dramatic siege the medieval world would ever witness.",
 "Night establishing shot of an Ottoman siege camp, thousands of campfires, banners, mountains behind, epic cinematic"),
# ---------------- CHAPTER 2: An Empire in Twilight ----------------
("An Empire in Twilight",
 "By the middle of the fifteenth century, the once glorious Byzantine Empire was a fading shadow of itself.",
 "Vast empty imperial throne room, dusty shafts of light, a lone throne, faded mosaics, melancholy atmosphere"),
(None,
 "A once mighty realm now held little more than the great city itself and scattered distant fragments.",
 "Close-up of an ancient parchment map showing a shrinking empire, candlelight, an emperor's hand tracing borders"),
(None,
 "To the east and west, the rising Ottoman Turks had completely encircled the ancient and proud imperial capital.",
 "Aerial view of Ottoman cavalry columns marching in long lines around the city walls, dust clouds, dramatic"),
(None,
 "Constantine the Eleventh, the last of the emperors, wore a crown that had grown painfully heavy.",
 "Regal portrait of Emperor Constantine the Eleventh in purple cloak and crown, solemn expression, dramatic close-up"),
(None,
 "He was fifty years old, brave and devout, a soldier who utterly refused to abandon his people.",
 "Constantine drilling with soldiers on the walls at dawn, sword raised, determined faces, golden light"),
(None,
 "Behind the great walls waited barely eight thousand tired defenders, and many were only foreign volunteers.",
 "Small band of weary defenders standing on the massive wall ramparts, outnumbered but resolute, wide shot"),
(None,
 "Against them stood a vast Ottoman host said to number nearly eighty thousand seasoned warriors of war.",
 "Aerial panorama of a vast Ottoman tent city stretching to the horizon, banners, campfires, epic scale"),
(None,
 "Ten to one, the terrible odds were against them, yet no emperor had ever abandoned the city.",
 "Split composition: tiny defenders on the walls above, endless Ottoman army below, dramatic contrast of scale"),
(None,
 "And so Constantine solemnly prepared his people for a terrible trial written in fire and stone.",
 "Constantine addressing a crowd of citizens in a city square, banners of the double-headed eagle, tense mood"),
# ---------------- CHAPTER 3: The Young Sultan ----------------
("The Young Sultan",
 "Across the narrow strait, a twenty-one year old ruler dared to dream the impossible dream of conquest.",
 "Young Sultan Mehmed the Second on horseback overlooking the strait, cape flowing in the wind, sunset"),
(None,
 "Mehmed the Second, the young Sultan of the Ottomans, burned with one singular and fierce obsession.",
 "Mehmed in his command tent at night, studying maps by candlelight, intense gaze, dramatic chiaroscuro"),
(None,
 "He would take Constantinople and make it the shining seat of his vast and glorious new empire.",
 "Dreamlike vision of Ottoman banners flying over Constantinople, golden light, painterly and symbolic"),
(None,
 "First, he raised a mighty fortress on the strait's narrowest point in under five short months.",
 "Massive construction site of Rumeli Fortress, hundreds of workers, wooden cranes, stone blocks, busy epic scene"),
(None,
 "Rumeli Fortress choked the great city from the sea, cutting off every last supply line of grain.",
 "Rumeli Fortress towering over the narrow strait, warships blocked in the water below, dramatic aerial"),
(None,
 "Then came his masterstroke, enormous bronze cannon larger than anything the world had ever seen before.",
 "Giant bronze cannon being cast in a foundry, molten metal glowing, workers silhouetted, dramatic firelight"),
(None,
 "Forged by the master craftsman Urban, one giant gun hurled stone balls weighing half a ton.",
 "The craftsman Urban standing proudly beside an enormous bronze cannon, oxen teams hitched, epic scale"),
(None,
 "Dragons of bronze and roaring flame, these monsters could smash the proudest walls on earth.",
 "Massive cannon firing, huge burst of smoke and flame, shockwave, dramatic low angle, cinematic"),
(None,
 "By the spring of fourteen fifty-three, every road to Constantinople lay firmly beneath Ottoman banners.",
 "Ottoman banners and troops advancing along spring roads toward the distant city, green landscape, wide shot"),
(None,
 "The young sultan's vast army gathered at last, and the distant drums of war began to sound.",
 "Enormous Ottoman army marching with war drums, dust rising, banners waving, epic wide panorama"),
# ---------------- CHAPTER 4: The Siege Begins ----------------
("The Siege Begins",
 "On the sixth of April, the great cannon spoke at last, and the very ground itself trembled.",
 "Cannonball smashing into the Theodosian Walls, stone exploding, dust cloud, ground-shaking impact, dramatic"),
(None,
 "Day after day, relentless stone thunder hammered the ancient Theodosian Walls without mercy or pause.",
 "Repeated bombardment of the walls, sections cracking, smoke rising, cannons lined up in the distance"),
(None,
 "Towers cracked, battlements crumbled, and thick choking dust filled the streets of the imperial city.",
 "Dusty city street inside Constantinople, citizens hurrying past rubble, damaged tower behind, tense atmosphere"),
(None,
 "But the defenders were no strangers to war, and each night they bravely rebuilt everything.",
 "Night repair crews rebuilding the breached wall with timber beams, torchlight, determined workers, dramatic"),
(None,
 "Under cover of darkness, weary masons and soldiers raised strong barriers of timber, stone, and faith.",
 "Close-up of masons and soldiers working by torchlight on a makeshift barricade, sweat and resolve"),
(None,
 "The city's few small cannons answered back, though gunpowder was scarce and the walls were old.",
 "Small Byzantine cannon on the wall firing back at the Ottoman lines, smoke drifting, dusk light"),
(None,
 "Greek fire no longer sailed these dark seas, yet courage still burned bright in every heart.",
 "Single candle burning in a dark chapel, a soldier praying before an icon, quiet emotional moment"),
(None,
 "For many long weeks the terrible bombardment continued, and still the great walls refused to fall.",
 "Moon phases over the besieged city, siege camp fires below, passage of time, poetic wide shot"),
(None,
 "Mehmed watched his great guns with mounting fury, for the proud city would not simply kneel.",
 "Angry Mehmed in his command tent, maps and reports scattered, advisors bowing, tense candlelit drama"),
(None,
 "Then he turned his hungry eyes toward the harbor, where a bold new battle was waiting.",
 "Mehmed gazing from a hilltop toward the Golden Horn harbor, ships and chain visible, scheming expression"),
# ---------------- CHAPTER 5: Ships Across the Hills ----------------
("Ships Across the Hills",
 "The Golden Horn, the city's northern harbor, was sealed shut by a mighty iron chain barrier.",
 "Close-up of massive iron chain links stretching across dark harbor water, city walls behind, moody"),
(None,
 "Stretched across the dark water, it firmly held back every Ottoman ship that dared approach.",
 "Wide harbor view, Ottoman warships halted before the great chain, Byzantine towers watching, tense standoff"),
(None,
 "Byzantine vessels ruled those calm waters, striking the stretched enemy supply lines with deadly ease.",
 "Byzantine galley patrolling the calm Golden Horn, oars moving, city skyline behind, serene yet tense"),
(None,
 "In a daring and desperate sea battle, four Christian ships routed a fleet ten times their size.",
 "Dramatic naval battle, four ships breaking through a larger fleet, waves crashing, sails billowing, epic"),
(None,
 "Mehmed, humiliated before his watching army, fiercely vowed that the sea itself would obey him.",
 "Frustrated Mehmed on the shoreline watching his fleet retreat, clenched fist, stormy sky, dramatic"),
(None,
 "Then came one of the boldest maneuvers in all the long history of medieval warfare.",
 "Night engineering camp, wooden rollers being greased, torches, workers preparing ships, secretive atmosphere"),
(None,
 "Under cover of night, his tireless engineers greased great wooden rollers and dragged seventy ships overland.",
 "Warships being hauled uphill on giant wooden rollers at night, hundreds of men pulling ropes, moonlight"),
(None,
 "Up the dark hills they sailed, over ridge and deep valley, into the Golden Horn itself.",
 "Ships cresting a moonlit hill ridge on rollers, sails furled, impossible sight, epic painterly composition"),
(None,
 "At dawn, the stunned city woke to find Ottoman sails floating where no sails should be.",
 "Dawn over the Golden Horn, Ottoman sails floating on the water, watchtower guards alarmed, golden light"),
# ---------------- CHAPTER 6: The Final Night ----------------
("The Final Night",
 "Now the siege pressed in from every side, and the brave defenders were stretched beyond endurance.",
 "Exhausted defenders resting on the wall ramparts at dawn, weary faces, broken weapons, somber light"),
(None,
 "For fifty-three long days the walls had held, but the exhausted men behind them were fading.",
 "Tired soldiers leaning against the battlements, bandaged comrades resting, quiet moment of exhaustion, no gore"),
(None,
 "On the fateful night of the twenty-eighth of May, the sultan ordered a final assault.",
 "Ottoman camp at night before the final assault, thousands of fires, soldiers preparing, ominous red sky"),
(None,
 "His armies would strike at dawn, wave upon relentless wave, until the proud city broke.",
 "Massive Ottoman army formations at dawn, rows of banners and spears, epic wide shot, rising sun"),
(None,
 "Inside the walls, Constantine walked among his weary soldiers, quietly thanking them one by one.",
 "Constantine walking among his soldiers on the wall, clasping hands, emotional farewell, torchlight"),
(None,
 "That evening, the frightened citizens gathered inside Hagia Sophia for one final solemn service.",
 "Hagia Sophia interior packed with a candlelit congregation, golden light, solemn and moving, no faces of fear"),
(None,
 "Greeks and Latins, long bitterly divided, knelt together as one final congregation facing doom.",
 "Greeks and Latins kneeling together in prayer, candles glowing, unity in a sacred moment, painterly"),
(None,
 "The emperor prayed alone through the long night, then rode out to his post at the breach.",
 "Constantine praying alone in a small chapel, single candle glow, then riding out at night, solemn"),
(None,
 "Before sunrise, a hundred thousand voices rose as one, and the last great battle began.",
 "Hundreds of thousands of torches and banners at dawn, the final assault beginning, overwhelming epic wide shot"),
# ---------------- CHAPTER 7: The City Falls ----------------
("The City Falls",
 "The Janissaries, the sultan's elite guard, charged the smoking breach as the sun touched the horizon.",
 "Janissary elite troops charging through the breach at sunrise, tall white hats, dramatic motion, epic"),
(None,
 "They found the small outer gate called Kerkoporta left open, a truly fatal mistake of fate.",
 "Small ancient side gate standing open in the wall, morning mist, an ominous quiet moment"),
(None,
 "Through that forgotten door, the Ottoman soldiers poured into the doomed city like a flood.",
 "Ottoman soldiers pouring through the open gate into the city streets, dust rising, unstoppable tide"),
(None,
 "Constantine, seeing the end had come, tore off his imperial robes and plunged into the fight.",
 "Constantine tearing off his imperial purple robe, drawing his sword, charging into battle, heroic"),
(None,
 "He fell as an emperor should fall, his sword in hand, among his loyal soldiers.",
 "The emperor fighting heroically among his loyal soldiers, sword raised, dust and banners, tragic and noble"),
(None,
 "No one ever found his body, and legend says he turned to marble, waiting to return.",
 "Empty misty battlefield at dusk, a fallen imperial banner, a marble emperor statue half-seen, mystical"),
(None,
 "By midday, the victorious Ottoman banners waved proudly from the towers of the fallen capital.",
 "Ottoman banners raised on the towers of Constantinople, midday sun, sweeping city view, historic moment"),
(None,
 "Mehmed rode through the silent streets in triumph, the great conqueror at only twenty-one.",
 "Young Mehmed riding in triumph through the silent city streets, guards and banners, solemn victory"),
(None,
 "He entered Hagia Sophia in person and ordered it preserved as a monument of his glory.",
 "Mehmed entering Hagia Sophia, beams of light through the dome, awe and reverence, grand interior"),
(None,
 "The thousand-year Byzantine Empire was gone forever, and a bold new age had now begun.",
 "Sunset over the fallen city, new banners on the walls, a turning page of history, painterly"),
# ---------------- CHAPTER 8: Echoes of History ----------------
("Echoes of History",
 "They called him Fatih, the Conqueror, and he proudly made the great city his capital.",
 "Mehmed as Fatih the Conqueror in his royal court, receiving homage, rich Ottoman splendor, grand"),
(None,
 "Constantinople became Istanbul, the proud seat of a mighty empire that would endure for centuries more.",
 "Istanbul skyline transforming, new minarets rising beside ancient domes, golden age beginning, panoramic"),
(None,
 "The great cannons of fourteen fifty-three had shattered far more than mere stone and pride.",
 "Abandoned giant cannon beside shattered wall sections, gunpowder smoke drifting, symbolic, dramatic"),
(None,
 "They had announced the age of gunpowder, when high stone walls alone could guard no kingdom.",
 "Giant cannon as a symbol of the new age, dramatic sky, fortress walls in the distance, epic"),
(None,
 "Yet the fallen city lived on forever in memory, in sacred art, in faith, in song.",
 "Golden Byzantine mosaics and sacred art, glowing in candlelight, timeless beauty preserved, close detail"),
(None,
 "Scholars fled westward, carrying precious ancient wisdom that would help ignite the Renaissance flame.",
 "Scholars with scrolls and books sailing westward on a ship, dawn light, hope and knowledge"),
(None,
 "And the legend of the last emperor still endures today, turned to marble beneath the city.",
 "Mystical marble emperor statue beneath the city, torchlight, legend alive, atmospheric and haunting"),
(None,
 "Empires rise and empires fall, but their echoes still shape the very world we inherit.",
 "Painterly montage of rising and falling empires, ruins and new cities, timeless, epic composition"),
(None,
 "Remember Constantinople, and remember this well, no wall stands forever, but great stories do.",
 "Modern Istanbul at sunset, Hagia Sophia glowing, seagulls, timeless beauty, closing emotional shot"),
]

assert len(DATA) == 75, f"beats: {len(DATA)}"

# ---- sanity checks on narration ----
words = 0
for ch, text, _ in DATA:
    assert not re.search(r"[0-9]", text), f"digit in: {text}"
    assert '"' not in text, f"quote in: {text}"
    words += len(text.split())
print("narration word count:", words)
assert 1150 <= words <= 1250, "word count out of range"
chapters = [c for c, _, _ in DATA if c]
assert len(chapters) == 8, f"chapter markers: {len(chapters)}"

# 1. narasi (with chapter markers)
lines = []
for ch, text, _ in DATA:
    if ch:
        lines.append(f"## CHAPTER: {ch}")
    lines.append(f"Narrator: {text}")
with open(os.path.join(BASE, "script/narasi-2026-10-05.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")

# 2. tts (pure narration)
with open(os.path.join(BASE, "script/tts-2026-10-05.txt"), "w") as f:
    f.write("\n".join(f"Narrator: {t}" for _, t, _ in DATA) + "\n")

# 3. beats json
cur_chapter = None
beats = []
prompts_map = {}
for i, (ch, text, scene) in enumerate(DATA, 1):
    if ch:
        cur_chapter = ch
    prompt = STYLE + " " + scene
    beats.append({
        "beat": f"beat-{i:03d}",
        "text": text,
        "chapter": cur_chapter,
        "image_prompt": prompt,
    })
    prompts_map[f"beat-{i:03d}"] = prompt
with open(os.path.join(BASE, "beats/beats-2026-10-05.json"), "w") as f:
    json.dump(beats, f, indent=2, ensure_ascii=False)

# 4. prompts json
with open(os.path.join(BASE, "gambar/prompts-2026-10-05.json"), "w") as f:
    json.dump(prompts_map, f, indent=2, ensure_ascii=False)

# 5. shorts plan
shorts = [
    {
        "id": "s1",
        "beat_start": "beat-024",
        "beat_end": "beat-028",
        "title": "The Cannon That Broke a 1,000-Year Empire",
        "description": ("Mehmed the Second built the largest cannon the world had ever seen "
                        "and aimed it at the strongest walls on Earth.\n\n"
                        "Watch the full story on Echoes of History Channel.\n\n"
                        "#shorts #history #documentary"),
        "tags": ["constantinople 1453", "ottoman empire", "mehmed the second",
                 "giant cannon", "history shorts"],
    },
    {
        "id": "s2",
        "beat_start": "beat-043",
        "beat_end": "beat-047",
        "title": "He Dragged Warships Over a Mountain",
        "description": ("Seventy Ottoman warships sailed over land and into the Golden Horn "
                        "overnight, behind the city's defenses.\n\n"
                        "Watch the full story on Echoes of History Channel.\n\n"
                        "#shorts #history #documentary"),
        "tags": ["constantinople 1453", "golden horn", "ottoman empire",
                 "naval history", "history shorts"],
    },
    {
        "id": "s3",
        "beat_start": "beat-057",
        "beat_end": "beat-061",
        "title": "The Last Emperor Died Fighting",
        "description": ("Constantine the Eleventh tore off his imperial robes and charged "
                        "into the final battle of Constantinople.\n\n"
                        "Watch the full story on Echoes of History Channel.\n\n"
                        "#shorts #history #documentary"),
        "tags": ["constantine the eleventh", "fall of constantinople",
                 "byzantine empire", "last stand", "history shorts"],
    },
]
for s in shorts:
    assert len(s["title"]) <= 60, s["title"]
with open(os.path.join(BASE, "shorts/shorts-plan-2026-10-05.json"), "w") as f:
    json.dump(shorts, f, indent=2, ensure_ascii=False)

# 6. upload metadata
chapter_lines = "\n".join(f"- {c}" for c in chapters)
upload = {
    "long": {
        "title": "The Fall of Constantinople 1453: The 53-Day Siege That Ended an Empire",
        "description": (
            "On the twenty-ninth of May, fourteen fifty-three, a thousand-year empire fell in a single morning. "
            "This is the dramatic story of the fifty-three-day siege of Constantinople: Sultan Mehmed the Second's "
            "monstrous cannons, the impossible feat of warships dragged across hills, and Emperor Constantine the "
            "Eleventh's heroic last stand behind the mighty Theodosian Walls.\n\n"
            "CHAPTERS (timestamps will be added after editing):\n" + chapter_lines + "\n\n"
            "If you love epic stories from world history, subscribe to Echoes of History Channel for a new "
            "documentary every day.\n\n"
            "#history #documentary #constantinople #ottomanempire #byzantineempire"
        ),
        "hashtags": ["#history", "#documentary", "#constantinople",
                     "#ottomanempire", "#byzantineempire"],
        "tags": ["constantinople 1453", "fall of constantinople", "ottoman empire",
                 "mehmed the second", "byzantine empire", "constantine the eleventh",
                 "siege of constantinople", "world history documentary",
                 "echoes of history"],
        "thumbnail_text": "EMPIRE FALLS",
    },
    "shorts": shorts,
}
with open(os.path.join(BASE, "upload-2026-10-05.json"), "w") as f:
    json.dump(upload, f, indent=2, ensure_ascii=False)

# 7. riwayat-topik.json
with open(os.path.join(BASE, "riwayat-topik.json"), "w") as f:
    json.dump([{
        "tanggal": "2026-10-05",
        "topik": "The Fall of Constantinople 1453",
        "kategori": "World History",
        "status": "produksi",
    }], f, indent=2, ensure_ascii=False)

print("beats:", len(beats))
print("chapters:", chapters)
print("files written OK")
