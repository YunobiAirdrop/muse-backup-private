#!/usr/bin/env python3
"""Beats weird-en 2026-10-13: 7 Times History Went Completely BONKERS.
Format BARU: "THE WEIRDNESS FACE-OFF" - 7 bizarre real events, scored out of 10,
champion crowned at the end. NOT countdown, NOT zone grouping (yesterday).
Persona: Bo, si takjub ("Serius ini nyata?!"). 74 beats, ~1100 words,
3 reaksi narator, hook 3-elemen, CTA verbal beat 39 + akhir,
silence 1.3s setelah beat 37 (fakta paling gila: molasses 21 killed).
Bumper segment disisipkan setelah beat 59 (break natural sebelum final round)."""
import json, os
W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
STYLE = "Digital 2D storybook illustration, colorful, fun, 16:9, "
B = [
# HOOK (3 elemen: kalimat ucap + teks on-screen + visual frame 1)
("A twenty-five-foot wave of sticky molasses tore through a city at thirty-five miles an hour. Nobody outran it.", "a giant dark brown wave of molasses taller than houses crashing down a city street, terrified cartoon people running", "A WAVE OF MOLASSES KILLED 21 PEOPLE"),
("Real meat once rained from a clear blue sky. People picked it up. Some of them TASTED it.", "chunks of raw meat falling from a bright blue sky onto a farmyard, a shocked cartoon farmer looking up", "MEAT RAINED FROM THE SKY"),
("Welcome to Weird World Daily. I am Bo, and I hunt the weirdest true stories on Earth.", "a cheerful cartoon explorer with a safari hat holding a magnifying glass, channel-style logo space", None),
("Today: seven real events so bizarre, they sound made up. We score each one out of ten for weirdness.", "seven glowing golden scorecards numbered 1 to 7 floating in a row", None),
("At the end, one gets crowned the weirdest moment in history. Place your bets now.", "a golden championship trophy with a big question mark on it, confetti falling", None),
("Starting with the one that made me say: wait, WHAT?!", "a stunned cartoon face with jaw dropped and eyes bulging, exclamation marks", None),
# E1 DANCING PLAGUE 1518
("ROUND ONE. Strasbourg, year fifteen eighteen. A woman named Frau Troffea steps outside, and starts dancing.", "a medieval woman in old clothing dancing alone in an empty cobblestone street", "ROUND 1: THE DANCING PLAGUE, 1518"),
("Alone. No music. No party. Just dancing in the street like the floor was on fire.", "a lone medieval woman dancing frantically in a quiet old town street at dawn", None),
("Within a week, thirty-four people had joined her. Within a month, HUNDREDS.", "a growing crowd of medieval people dancing uncontrollably in a town square", None),
("They could not stop. Dancing through blistered feet, through exhaustion, through collapse.", "exhausted medieval dancers with blistered feet still dancing, some collapsing", None),
("Some of them danced until their hearts gave out. Days of nonstop dancing.", "a medieval dancer collapsing from exhaustion while others keep dancing around", "DANCED UNTIL THEY DROPPED"),
("Doctors back then said the cure was MORE dancing. So the city built a stage. Seriously.", "a medieval wooden stage built in a town square with a confused doctor pointing at it", None),
("Modern scientists think it was mass hysteria, or maybe a fungus in the rye bread. A natural hallucinogen.", "a scientist examining a loaf of rye bread with glowing green fungus under a magnifying glass", None),
("Whatever it was, the dancing plague lasted about two months. A whole city, dancing against its will.", "an aerial view of a medieval city with crowds dancing in every street", None),
("WEIRDNESS SCORE: nine out of ten. Two months of compulsory dancing? I had to read that twice.", "a giant golden scorecard showing 9 out of 10 with dancing silhouettes", "9 OUT OF 10"),
# E2 MEAT SHOWER 1876
("ROUND TWO. March third, eighteen seventy-six. Bath County, Kentucky. Clear blue sky.", "a peaceful Kentucky farm under a bright clear blue sky in the 1870s", "ROUND 2: THE MEAT SHOWER, 1876"),
("And then, out of nowhere: meat. Chunks of raw meat, falling from the sky like hail.", "chunks of raw meat falling from a clear sky onto a farm, a farmer shielding his head", "MEAT FELL FROM A CLEAR SKY"),
("Witnesses said the pieces were up to four inches across. Raining down for several minutes.", "close-up of meat chunks of various sizes scattered on farm grass", None),
("And here is the part that breaks me. Some people tasted it. TASTED. IT.", "a cartoon farmer holding a piece of sky-meat near his mouth, horrified onlookers", None),
("Two brave souls told reporters it tasted like lamb or venison. I need a minute.", "two 1870s reporters with notebooks interviewing a farmer holding meat", None),
("The best explanation scientists have? Vultures. A flock flying overhead, projectile-vomiting mid-flight.", "a flock of cartoon vultures flying in a V formation over a farm, motion lines", None),
("That is right. It was probably raining regurgitated meat. Somehow that makes it WORSE.", "a cartoon vulture with a queasy face, meat chunks falling in dotted lines below", None),
("Meat shower gets a ten out of ten for pure chaos. Nobody beats raining dinner.", "a giant golden scorecard showing 10 out of 10 with meat chunks raining", "10 OUT OF 10"),
("Which brings our scorecard to: dancing plague nine, meat shower ten.", "a scoreboard showing Dancing Plague 9 and Meat Shower 10, trophy between them", None),
# E3 BEER FLOOD 1814
("ROUND THREE. London, October eighteen fourteen. A brewery vat the size of a house bursts open.", "a massive wooden brewery vat exploding in 1814 London, beer bursting out", "ROUND 3: THE BEER FLOOD, 1814"),
("One point four MILLION liters of dark porter beer flooded the streets of St. Giles.", "a tidal wave of dark beer surging through narrow London streets, people fleeing", "A 15-FOOT WAVE OF BEER"),
("The wave was fifteen feet tall. It tore through homes, smashed walls, and lifted furniture.", "a fifteen-foot beer wave smashing through a brick house wall, furniture floating", None),
("Cellar dwellers woke up to beer pouring through their windows. Eight people died that day.", "beer pouring through a basement window onto a shocked family in 1814", None),
("Hundreds showed up with buckets, pots, even bathtubs, scooping free beer off the street.", "a crowd of 1814 Londoners with buckets and pots scooping beer from the street", None),
("One man died days later after drinking too much of the floodwater. No joke.", "a cartoon caution scene of a man drinking from a bucket with a warning sign", None),
("The brewery called it an Act of God and paid nothing. The court agreed. Beer: one, people: zero.", "a stern 1814 judge banging a gavel beside a giant beer barrel", None),
("WEIRDNESS SCORE: seven. Deadly, yes. But compared to raining meat? Beer behaves.", "a golden scorecard showing 7 out of 10 with a foamy beer mug", "7 OUT OF 10"),
("Still, a beer tsunami through London is not something I expected to say today.", "a cartoon explorer shrugging in front of a London street with beer waves", None),
# E4 MOLASSES FLOOD 1919
("ROUND FOUR. Boston, January nineteen nineteen. A steel tank holding two point three MILLION gallons of molasses.", "a giant steel molasses tank looming over Boston's North End in 1919", "ROUND 4: THE MOLASSES FLOOD, 1919"),
("At lunchtime, with a sound like machine-gun fire, the tank exploded.", "the steel tank bursting open with a deafening crack, metal plates flying", None),
("A wave of molasses twenty-five feet tall surged through the North End at thirty-five miles an hour.", "a towering dark brown molasses wave engulfing 1919 Boston streets", "25 FEET TALL, 35 MILES AN HOUR"),
("It crushed buildings, flipped a firehouse, and threw a truck into the harbor. Twenty-one people died.", "a firehouse crushed by a molasses wave, a truck flying toward the harbor", None),
("The cleanup took WEEKS. The harbor stayed brown until summer. Locals said you could smell it for decades.", "workers shoveling thick brown molasses off a Boston street, brown harbor water", None),
("Quick pause: if history this weird is your thing, hit subscribe. We do this every single day.", "a cheerful cartoon explorer pointing at a big red subscribe button", "SUBSCRIBE!"),
("Molasses is thicker than water and twice as deadly. Boston learned that the sticky way.", "a cartoon explorer stuck waist-deep in molasses, struggling comically", None),
("WEIRDNESS SCORE: ten out of ten. A killer wave of pancake syrup. There are no words.", "a giant golden scorecard showing 10 out of 10 dripping with molasses", "10 OUT OF 10"),
("Tied with the meat shower at ten. This championship is getting SPICY.", "a scoreboard showing Meat Shower 10 and Molasses 10 tied, flames around", None),
# E5 EXPLODING TROUSERS
("ROUND FIVE. New Zealand, the nineteen thirties. Farmers spray weeds with a chemical called sodium chlorate.", "a 1930s New Zealand farmer spraying weeds with a hand pump sprayer", "ROUND 5: EXPLODING TROUSERS, 1930s"),
("It dries into their clothes. Their trousers. Then someone lights a cigarette, or walks past a fire.", "a farmer's trousers with invisible chemical residue glowing faintly, a match nearby", None),
("And their PANTS burst into flames. Spontaneously. Exploding trousers.", "a cartoon 1930s farmer with his trousers on fire, jumping in shock", "HIS PANTS EXPLODED"),
("Farmers were walking around with clothes that could combust at any second.", "several farmers tiptoeing nervously in a field, trousers smoking slightly", None),
("One man reported his trousers igniting while riding his horse. The horse was fine, by the way.", "a 1930s farmer on a horse with flaming trousers, the horse looking annoyed", None),
("It took YEARS before anyone connected the dots to the weedkiller. Years of surprise flaming pants.", "a calendar flipping through years while trousers keep bursting into flames", None),
("WEIRDNESS SCORE: eight. Points for comedy, but nobody died, so it loses to the floods.", "a golden scorecard showing 8 out of 10 with flaming trousers", "8 OUT OF 10"),
("Still, my pants exploded has to be the greatest excuse in human history.", "a cartoon farmer shrugging innocently beside a pile of burnt trousers", None),
# E6 TUNGUSKA 1908
("ROUND SIX. Siberia, June nineteen oh eight. Seven in the morning.", "a quiet Siberian forest at dawn in 1908, birds flying", "ROUND 6: TUNGUSKA, 1908"),
("A fireball tears across the sky, brighter than the sun. Then the biggest explosion in recorded history.", "a blazing fireball streaking across the Siberian sky, blinding white light", None),
("Eighty MILLION trees flattened. An area bigger than some countries, just gone.", "an endless field of flattened trees radiating outward from a blast center", "80 MILLION TREES FLATTENED"),
("The shockwave circled the planet TWICE. Windows shattered hundreds of miles away.", "a shockwave ripple circling a cartoon Earth twice, windows cracking far away", None),
("For days after, nights were so bright across Europe that people read newspapers outdoors at midnight.", "Europeans reading newspapers outside at midnight under a glowing bright sky", None),
("And here is the wildest part: there is no crater. The leading theory is a meteor that exploded MID-AIR.", "a meteor exploding in mid-air above Siberia with no crater on the ground below", None),
("A cosmic bomb that never even touched the ground. Space said hello, and Siberia felt it.", "a cartoon Earth waving at a meteor, Siberia with a bump on its head", None),
("WEIRDNESS SCORE: nine. Cosmic-scale weirdness, but at least physics has an explanation.", "a golden scorecard showing 9 out of 10 with a meteor", "9 OUT OF 10"),
("Which means the meat shower still holds the crown. Barely.", "a scoreboard with Meat Shower 10 on top, Tunguska 9 below", None),
# (BUMPER SEGMENT: image + bumper-weird-en.mp3 + overlay WEIRD WORLD DAILY)
# E7 FISH RAIN HONDURAS
("FINAL ROUND. Yoro, Honduras. Every single year, after the first heavy rains of the season.", "a small Honduran town under dark storm clouds, rain pouring", "FINAL ROUND: THE FISH RAIN"),
("Fish. Hundreds of small silver fish, scattered across the fields. Raining from the sky.", "hundreds of small silver fish scattered across a green field after a storm", "FISH FALL FROM THE SKY"),
("The locals call it the Lluvia de Peces. The Rain of Fish. And it has happened for OVER a century.", "Honduran villagers collecting silver fish from a field, celebrating", None),
("Scientists say underground rivers probably flood and wash the fish up through caves.", "a cartoon cross-section of underground rivers pushing fish up through cave tunnels", None),
("But nobody has ever actually SEEN it happen. The fish just appear. After the storm.", "an empty field during a storm, then the same field covered in fish, a detective shrugging", None),
("There is even a festival for it now. A parade. Celebrating fish that fall from heaven.", "a colorful Honduran parade with fish floats and dancing villagers", None),
("WEIRDNESS SCORE: eight. Annual sky-fish is amazing, but science has a decent theory.", "a golden scorecard showing 8 out of 10 with raining fish", "8 OUT OF 10"),
("Final scoreboard: meat shower ten, molasses ten, dancing plague nine, Tunguska nine, trousers eight, fish rain eight, beer flood seven.", "a full scoreboard listing all seven events with their scores", None),
# VERDICT
("But the rules of the Weirdness Face-Off say there can only be ONE champion.", "the golden championship trophy glowing, seven event icons around it", None),
("So I break the tie with one question: which one would you LEAST want to live through?", "a cartoon explorer thinking hard, molasses wave on one side, meat rain on the other", None),
("A sticky wave you cannot outrun, or meat falling on your breakfast? My crown goes to the MOLASSES FLOOD.", "the golden trophy placed on a wave of molasses, confetti and crown", "THE CHAMPION: MOLASSES FLOOD"),
("Twenty-one lives, a city smelling sweet for decades, a wave taller than a house. Unbeatable.", "a memorial scene of 1919 Boston with a giant molasses wave statue", None),
("Disagree? GOOD. That is the point. Drop your champion in the comments and defend it.", "a cartoon explorer reading a giant stack of comment cards and grinning", None),
("And if reality being stranger than fiction is your thing, my last video toured seven places that look completely fake. Watch it next.", "a mirror salt flat and pink lake with an arrow pointing to a play button", None),
("New weirdness every single day on Weird World Daily. Subscribe, stay weird, see you tomorrow.", "a cheerful cartoon explorer waving goodbye under a sunset of bizarre landscapes", "STAY WEIRD!"),
]
os.makedirs(os.path.join(W, "script"), exist_ok=True)
os.makedirs(os.path.join(W, "data"), exist_ok=True)
batches = {}
for i, (tts, scene, ov) in enumerate(B, start=1):
    num = f"{i:03d}"
    open(os.path.join(W, "script", f"b13-beat-{num}.txt"), "w").write(tts)
    bnum = (i - 1) // 18
    batches.setdefault(f"batch{bnum+1}", []).append({"num": num, "tts": tts, "image_prompt": STYLE + scene, "overlay": ov})
json.dump(batches, open(os.path.join(W, "data", "batches-b13.json"), "w"), indent=1)
words = sum(len(t.split()) for t, _, _ in B)
print(f"beats={len(B)} words={words} batches={len(batches)}")
