#!/usr/bin/env python3
"""Beats weird-en 2026-10-12: 7 Places on Earth That Look Completely FAKE.
Grouping by theme (ALIEN LAND / FIRE & HEAT / IMPOSSIBLE WATER & SKY), NOT countdown.
72 beats, ~1050 words, hook 3-elemen, 3 reaksi narator, CTA verbal beat 36,
silence 1.3s setelah beat 35 (fakta paling gila: kristal Naica sebesar bus)."""
import json, os
W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
STYLE = "Digital 2D storybook illustration, colorful, fun, 16:9, "
B = [
# HOOK
("This place turns into a MIRROR so big, satellites use it to aim their lasers.", "a vast white salt flat flooded with a thin layer of water reflecting the sky perfectly, a tiny person walking on clouds illusion", "A MIRROR THE SIZE OF A COUNTRY"),
("And it is not even the weirdest place in this video. Not even CLOSE.", "a shocked cartoon explorer with wide eyes holding a map upside down", None),
("I found seven places on Earth that look completely FAKE in photos. Every single one is real.", "seven glowing postcard photos of bizarre landscapes floating in a row", None),
("Alien islands. A cave that can kill you in minutes. A lake the color of bubble gum.", "a split scene: alien umbrella trees, a glowing crystal cave, a bright pink lake", None),
("We are touring them by zone: alien land, fire and heat, and water that breaks physics.", "a cartoon world map with three glowing zones marked in different colors", None),
("Wait till zone two. I had to read that twice. My brain refused it the first time.", "a cartoon brain shaking its head in disbelief at a newspaper", None),
# ZONE 1 SOCOTRA
("ZONE ONE: ALIEN LAND. First stop, an island that looks like another planet. Socotra.", "an alien-looking island with umbrella-shaped trees seen from a cartoon airplane window", "ZONE 1: ALIEN LAND"),
("Socotra sits off the coast of Yemen, cut off from the mainland for millions of years.", "a small island separated from a continent by glowing ocean, dotted timeline arrows", None),
("Evolution went completely rogue there. Around a third of its plants exist NOWHERE else on Earth.", "strange cartoon plants sprouting in a row, each with a glowing unique star above it", None),
("The star is the dragon blood tree. It grows like a giant green umbrella flipped inside out.", "a giant dragon blood tree shaped like a huge green umbrella on a rocky hill", None),
("Cut its bark and it bleeds dark red sap. Literally called dragon blood. Used as dye for centuries.", "a tree trunk cut oozing dark red sap into a small wooden bowl, painter using red dye", None),
("Then there are bottle trees, fat pink trunks with tiny flowers, like cartoon props.", "fat pink bottle-shaped trees with tiny pink flowers on a sunny hillside", None),
("wait, WHAT?! A third of an island's plants invented themselves in total isolation?", "a stunned cartoon face with jaw dropped, strange plants dancing behind it", "1 IN 3 PLANTS EXIST NOWHERE ELSE"),
("Scientists call Socotra the most alien-looking place on Earth. Looking at it, zero arguments.", "a scientist in a lab coat shrugging in front of alien umbrella trees", None),
("If aliens ever land, this is the one place they will feel right at home.", "a cute cartoon alien waving happily under a dragon blood tree", None),
# SAILING STONES
("Still in alien land, we jump to Death Valley, California. The hottest valley in America.", "a cracked dry desert valley under a blazing cartoon sun", None),
("On a flat dry lakebed called the Racetrack, rocks MOVE. By themselves. Leaving long trails.", "large rocks on a flat dry lakebed with long winding trails behind them", None),
("Some of these stones weigh as much as a full-grown man. Nobody pushes them. Nobody.", "a huge boulder standing next to a cartoon man of the same height on cracked mud", None),
("For a hundred years, nobody had ever seen one move. Just the trails, every morning.", "an old-fashioned detective with a magnifying glass staring at rock trails at sunrise", None),
("People blamed aliens. Animals. Secret human pranks. Even magnetic fields.", "cartoon thought bubbles above a desert: a UFO, a coyote, a prankster, a magnet", None),
("Then in 2014, scientists finally caught them: thin sheets of ice, floating on meltwater.", "a rock sitting on a thin transparent sheet of ice on shallow water at dawn", None),
("A gentle wind pushes the ice, the ice drags the rocks, inch by inch, slower than a snail.", "a snail racing neck and neck with a slow moving rock on ice", None),
("Mystery solved, sure. But watch the footage and it STILL looks impossible.", "a cartoon camera filming a rock trail, the cameraman scratching his head", None),
("A rock that walks across a desert when nobody is watching. Alien land, indeed.", "a rock with tiny cartoon footprints walking away across the desert at night", None),
# ZONE 2 DANAKIL
("ZONE TWO: FIRE AND HEAT. Pack water. Then pack more water. The Danakil Depression, Ethiopia.", "a neon yellow and orange volcanic landscape with steam rising, a cartoon explorer sweating", "ZONE 2: FIRE AND HEAT"),
("This is one of the hottest inhabited places on Earth. Summer days regularly pass fifty degrees.", "a giant thermometer bursting at the top over a shimmering desert", None),
("The ground here is painted neon yellow, green, and orange. Like a warning sign from nature.", "bright neon yellow green and orange mineral terraces with bubbling pools", None),
("Those colors are acid springs. Hot water loaded with sulfur and iron, bubbling out of the crust.", "bubbling neon acid pools with steam and sulfur crystals around the edges", None),
("Parts of Danakil sit more than a hundred meters BELOW sea level. The land itself sank.", "a cartoon cross-section of sunken land with a measuring ruler going below a sea level line", None),
("Salt flats stretch to the horizon, and workers still mine salt blocks by hand, like centuries ago.", "workers cutting white salt blocks on a vast salt flat with camels in a line", None),
("Lava lakes glow nearby in the Erta Ale volcano, one of the few on Earth that never sleeps.", "a volcano crater glowing with a bright orange lava lake at dusk", None),
("It looks like the set of a movie about Mars. People actually LIVE here. The Afar people.", "a small village of huts beside a red Mars-like volcanic plain", None),
("Working in acid-colored heat that would hospitalize most of us in an afternoon. Respect.", "a cartoon explorer fainting dramatically while a local worker smiles and waves", None),
# NAICA
("Now we go underground. Mexico. The Cave of the Crystals, three hundred meters below a mine.", "a mine elevator descending deep underground toward a glowing cave entrance", None),
("In the year two thousand, miners drilling for silver broke into a hidden chamber.", "two cartoon miners with a drill breaking through a rock wall into bright light", None),
("And found crystals of selenite as long as a BUS. Eleven meters long. Half a million years old.", "gigantic white crystal beams crossing a cave, a tiny yellow bus beside one for scale", "CRYSTALS AS LONG AS A BUS"),
("Quick pause: if places like this blow your mind too, hit subscribe. We hunt a new one every day.", "a cheerful cartoon explorer pointing at a big red subscribe button", "Subscribe!"),
("Here is the catch. That cave is trying to kill you. The air is about fifty-eight degrees.", "a warning sign with a thermometer inside a steaming crystal cave", None),
("And the humidity is near one hundred percent. Your sweat cannot evaporate. You just cook.", "a cartoon explorer inside a steam-filled cave, sweat drops unable to evaporate", None),
("Without a special cooling suit and an ice air supply, a human survives only minutes inside.", "an explorer in a bulky orange cooling suit with an ice backpack entering the cave", None),
("Scientists explored it wearing suits that look like astronaut gear. Underground astronauts.", "astronaut-like explorers walking carefully between giant white crystals", None),
("A crystal palace, older than our species, that humans can barely visit. Fire zone wins.", "a majestic palace made of giant glowing crystals deep underground", None),
# ZONE 3 HILLIER
("ZONE THREE: IMPOSSIBLE WATER AND SKY. First, a lake that looks Photoshopped. Lake Hillier, Australia.", "an aerial view of a bright pink oval lake surrounded by green forest and blue ocean", "ZONE 3: IMPOSSIBLE WATER"),
("The water is bubblegum PINK. Not a reflection. Not a trick of the light. The water itself.", "a close-up of bubblegum pink lake water lapping a white sandy shore", None),
("Fill a bottle with it and it stays pink on your shelf. Scientists checked. Still pink.", "a clear bottle filled with pink water on a lab shelf, a scientist nodding", None),
("The color comes from tiny algae and bacteria that thrive in extremely salty water.", "cute cartoon pink algae microbes smiling inside salty pink water", None),
("And Lake Hillier is saltier than the ocean, sitting right NEXT to the deep blue Pacific.", "a pink lake and a deep blue ocean side by side separated by a thin strip of forest", None),
("From a plane, it is a pink oval punched into green forest beside blue sea. Pure cartoon.", "a cartoon airplane window view of a pink oval lake in green forest by the sea", None),
("no, because WHY does nature own a pink highlighter and nobody told us?!", "a giant pink highlighter pen drawing over a lake, a shocked cartoon face beside it", None),
("Swimming in it is considered safe, by the way. Weird, pink, and harmless. Mostly.", "a happy cartoon swimmer floating in bright pink water wearing sunglasses", None),
# SALAR
("Remember the mirror from the start? Time to land on it. Salar de Uyuni, Bolivia.", "a vast white salt flat horizon with a cartoon explorer landing like a superhero", None),
("This is the largest salt flat on Earth. Over ten thousand square kilometers of white.", "an endless white salt flat with hexagonal salt patterns stretching to the horizon", None),
("It formed when ancient lakes dried up, leaving a crust of salt up to ten meters thick.", "a cartoon cross-section showing a thick white salt crust under a dry lakebed", None),
("In the rainy season, a thin sheet of water floods the top. Centimeters deep. Perfectly still.", "rain clouds sprinkling over a salt flat forming a thin shining layer of water", None),
("And the whole flat becomes the largest natural mirror on the planet. Sky below, sky above.", "a person standing on a perfect mirror surface with sky reflected below and above", "THE WORLD'S LARGEST MIRROR"),
("People standing on it look like they are walking on clouds. The horizon completely disappears.", "tiny people walking on clouds illusion on a mirror salt flat at sunset", None),
("It is so flat and reflective, satellites use it to calibrate their instruments from orbit.", "a satellite in space aiming a beam down at a shining mirror salt flat", None),
("A mirror so big, space agencies aim at it. Let that sink in for a second.", "a cartoon explorer with mind-blown expression, mirror landscape behind him", None),
# CATATUMBO
("Last stop, we stay after dark. Lake Maracaibo, Venezuela. The Catatumbo lightning.", "a night lake with dramatic lightning bolts filling the sky", None),
("Here, lightning storms rage for around two hundred and sixty nights every single year.", "a calendar with lightning bolt icons on almost every page, night sky behind", None),
("On a good night, the sky can flash up to two hundred and eighty strikes in one hour.", "dozens of lightning bolts striking over a dark lake in one spectacular moment", "280 LIGHTNING STRIKES AN HOUR"),
("Warm trade winds slam into cold mountain air right over the river mouth. Every night. Same spot.", "warm orange winds and cold blue mountain air colliding over a river mouth", None),
("Sailors used these storms as a lighthouse for centuries. You can see the flashes far out at sea.", "an old sailing ship at night guided by lightning flashes on the horizon", None),
("The lightning is so constant, locals just call it the everlasting storm.", "villagers calmly drinking coffee under a sky full of distant lightning", None),
("Imagine trying to sleep under a sky that strobes like a broken stadium light. For centuries.", "a cartoon person in bed with a pillow over his head while lightning flashes outside", None),
("Water and sky teaming up to put on Earth's longest-running light show.", "a theatrical stage curtain opening over a lake with a lightning light show", None),
# CLOSING
("So, the verdict. Which of these seven places looks the MOST fake?", "seven landscape postcards fanned out around a big golden question mark", None),
("Socotra's alien trees are strong. The pink lake is strong. But my winner is the Salar mirror.", "a golden trophy standing on a mirror salt flat with pink lake and umbrella trees behind", None),
("A place where the ground becomes the sky is cheating. It just is.", "a person standing between sky above and sky below on a perfect mirror", None),
("Which one broke YOUR brain? Tell me in the comments, and argue about it. I read everything.", "a cartoon explorer reading a giant stack of comment cards and smiling", None),
("And if your brain likes weird, my last video proved your BODY is lying to you. Seven facts. Watch it next.", "a cartoon brain winking mischievously in a mirror, arrow pointing to a play button", None),
("New weird places, creatures, and records every day here on Weird World Daily.", "a sunrise over a collage of bizarre landscapes with a channel flag planted", None),
("Subscribe so you don't miss tomorrow's. Stay weird, everybody. See you tomorrow.", "a cheerful cartoon explorer waving goodbye in front of a mirror salt flat sunset", "STAY WEIRD!"),
]
os.makedirs(os.path.join(W, "script"), exist_ok=True)
os.makedirs(os.path.join(W, "data"), exist_ok=True)
batches = {}
for i, (tts, scene, ov) in enumerate(B, start=1):
    num = f"{i:03d}"
    open(os.path.join(W, "script", f"b12-beat-{num}.txt"), "w").write(tts)
    bnum = (i - 1) // 18
    batches.setdefault(f"batch{bnum+1}", []).append({"num": num, "tts": tts, "image_prompt": STYLE + scene, "overlay": ov})
json.dump(batches, open(os.path.join(W, "data", "batches-b12.json"), "w"), indent=1)
words = sum(len(t.split()) for t, _, _ in B)
print(f"beats={len(B)} words={words} batches={len(batches)}")
