#!/usr/bin/env python3
"""Naskah b16 weird-en 2026-10-18: '7 Foods So Weird They Should NOT Exist'
Ranking Weirdness Score 0-10, eskalasi 7->1. Dump ke data/batches-b16.json.
Format tiap beat: num, tts, img (prompt storybook 2D), overlay (opsional)."""
import json, os

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
ST = "storybook 2D illustration, colorful, fun, expressive, 16:9, "

B = []
def beat(tts, img, overlay=None):
    e = {"num": len(B) + 1, "tts": tts, "img": ST + img}
    if overlay:
        e["overlay"] = overlay
    B.append(e)

# ---- HOOK (3 detik pertama = momen paling mengejutkan) ----
beat("There's a cheese in Italy... that is still ALIVE when you eat it.",
     "a wheel of rustic italian cheese with cute cartoon maggots wiggling on top, dramatic lighting")
beat("And if you don't shield your eyes... the maggots jump straight at your face.",
     "cartoon maggots leaping through the air toward the viewer, person shielding eyes with hand",
     overlay="MAGGOTS JUMP AT YOUR FACE")
beat("Wait, WHAT?! Yeah — this is one hundred percent real. And it's only number SEVEN on today's list.",
     "shocked cartoon narrator with wide eyes and open mouth, question marks floating")
# ---- INTRO ----
beat("Today I'm ranking the seven WEIRDEST foods on planet Earth... from gross... to literally ILLEGAL.",
     "globe surrounded by seven mysterious covered dishes with question marks")
beat("Every dish gets a Weirdness Score out of ten. And number one? It made me question humanity itself.",
     "scoreboard showing numbers 1 to 10 with a golden trophy on top")
beat("I had to read that twice, I swear. Okay — let's do this!",
     "excited cartoon host pointing at viewer, confetti")
beat("One rule before we start: everything on this list is REAL. People actually eat this. Voluntarily.",
     "stamp saying REAL in red over a dinner plate, serious tone illustration")
beat("And to the subscriber who requested a food episode — this one's for you. You asked for it!",
     "cartoon subscriber comment bubble saying food episode please, host saluting")
# ---- #7 CENTURY EGG ----
beat("Number seven: the Century Egg. From China. It looks like it rotted for a hundred years.",
     "black preserved egg cut open showing dark jelly white and greenish yolk on a plate")
beat("It's a duck egg buried in clay, ash, and salt for weeks... until the white turns into dark jelly.",
     "duck eggs being packed in clay and ash by hands, traditional chinese setting")
beat("The yolk goes creamy and greenish. It smells like strong cheese mixed with... a chemistry lab.",
     "close-up of century egg cross-section with green swirls, wavy smell lines")
beat("The patterns on the white look like pine branches. Chefs actually call it the pine-patterned egg. Fancy!",
     "century egg white with beautiful pine-branch crystal patterns, elegant plating")
beat("First-timers swear it's rotten. It's not — it's totally safe. Just deeply, deeply suspicious looking.",
     "nervous cartoon tourist poking a black egg with a fork, sweating")
beat("Legend says it was invented by accident centuries ago, when someone found eggs in a lime pit. Best accident ever.",
     "ancient chinese farmer discovering eggs in a lime pit, surprised")
beat("Honestly? This is the TAMER one today. Weirdness Score: six out of ten. We go UP from here.",
     "scoreboard showing 6 out of 10 with a small egg icon")
# ---- #6 BALUT ----
beat("Number six: Balut. A street food superstar in the Philippines.",
     "bustling filipino night market stall with steaming pots, vendor smiling")
beat("It's a fertilized duck egg — boiled and eaten when the duckling inside is partway developed.",
     "balut egg cracked open showing developed duck embryo inside, steam rising")
beat("You crack the top, sip the warm broth, then eat the whole thing. Yes. The whole thing.",
     "hands cracking open a balut egg over a small cup, street food style")
beat("Street vendors sell them warm from baskets, shouting balut through the night markets. You can't miss them.",
     "filipino vendor carrying a basket of steaming balut eggs at night market")
beat("Locals LOVE it. They say it's rich, savory, and packed with protein. Tourists? They usually cry first.",
     "happy local eating balut next to a crying cartoon tourist, split screen")
beat("Rumor says it boosts your energy on... date nights. Let's just leave it at that.",
     "winking cartoon duck with hearts, playful romantic lighting")
beat("Would I try it? ...Maybe. With my eyes closed. Weirdness Score: seven out of ten.",
     "scoreboard showing 7 out of 10, cartoon host peeking with one eye closed")
# ---- #5 ESCAMOLES ----
beat("Number five: Escamoles. From Mexico. Also known as... insect caviar.",
     "mexican tacos filled with pale ant larvae, rustic wooden table")
beat("These are the larvae of giant black ants, scooped from the roots of agave plants.",
     "giant black ants on agave plant roots underground, larvae visible")
beat("They're sautéed in butter with onions and served in tacos. They taste nutty, like a weird popcorn.",
     "larvae sizzling in a frying pan with butter and onions, chef tossing")
beat("Harvesting them is brutal — the ants bite HARD. That's exactly why they're so expensive.",
     "person's hand being bitten by big black ants while collecting larvae, dramatic")
beat("Ancient Aztecs served them to royalty. Royalty ate BUG BABIES, people. Let that sink in.",
     "aztec emperor on throne being served a golden plate of larvae, pyramids behind")
beat("A plate can cost as much as a fancy steak. Bug larvae. Steak prices. The world is wild.",
     "restaurant bill showing high price next to a small plate of larvae")
beat("Nope. I draw the line there. Weirdness Score: seven and a half out of ten.",
     "scoreboard showing 7.5 out of 10, host making an X with arms")
# ---- #4 KOPI LUWAK ----
beat("Quick break — if your stomach is still with me, smash that subscribe button. It gets SO much worse.",
     "cartoon stomach character giving thumbs up, subscribe button glowing")
beat("Number four: Kopi Luwak. The most expensive coffee on Earth. Made from... poop.",
     "luxurious cup of coffee next to a pile of coffee beans, dollar signs floating",
     overlay="POOP COFFEE")
beat("In Indonesia, a cat-like animal called the civet eats ripe coffee cherries... and poops out the beans.",
     "cute civet cat eating red coffee cherries in indonesian jungle")
beat("Farmers collect the beans from the droppings, wash them, roast them — and sell them for hundreds of dollars per kilo.",
     "hands washing coffee beans in water, then roasting them in a pan")
beat("Fans say digestion makes it smoother and less bitter. Critics say you're just drinking... expensive poop.",
     "split screen: happy coffee drinker versus disgusted critic, same cup")
beat("The ugly truth? Most kopi luwak today comes from caged civets in rough conditions. So it's weird AND sad.",
     "sad civet in a small cage looking at camera, somber mood")
beat("Wild-sourced is rare and costs even more. Your wallet suffers either way.",
     "empty wallet with moths flying out next to a coffee cup")
beat("Weirdness Score: eight out of ten. Paying six hundred dollars for poop coffee is a CHOICE.",
     "scoreboard showing 8 out of 10, price tag reading 600 dollars")
# ---- #3 HAKARL ----
beat("Number three: Hakarl. Iceland's legendary fermented shark.",
     "icelandic landscape with northern lights, cubes of fermented shark on a plate")
beat("Greenland shark meat is actually POISONOUS when fresh. So Icelanders bury it for months to ferment it.",
     "shark meat buried in a gravel pit underground, cross-section view")
beat("The fermentation takes six to twelve WEEKS in gravel pits. That's patience... or madness.",
     "calendar pages flipping rapidly over a buried pit, snow falling")
beat("The result smells like ammonia. Like a public toilet... mixed with cleaning fluid.",
     "person pinching nose hard, green stink waves rising from shark cubes")
beat("Even Anthony Bourdain — the toughest food guy ever — called it the single worst thing he ever ate.",
     "tough chef character spitting out food dramatically, worst ever stamp")
beat("Icelanders eat it at festivals and chase it with strong liquor. You NEED the liquor. Trust me.",
     "viking-style festival with people eating shark cubes and drinking, cheering")
beat("Weirdness Score: nine out of ten. Poison shark that you must ROT before eating. Incredible.",
     "scoreboard showing 9 out of 10 with a shark icon")
# ---- #2 SURSTROMMING ----
beat("Number two: Surstromming. Fermented herring from Sweden. The smelliest food on Earth. Scientifically.",
     "swedish red cabin by a lake, bulging tin cans of fermented herring on a table")
beat("They ferment the fish in cans for months. The cans literally BULGE from the gas building up inside.",
     "metal can bulging and swelling with pressure, about to burst")
beat("One study measured it as one of the most putrid food odors ever recorded. Science said so.",
     "scientist in lab coat holding a smell meter showing maximum, fish can open")
beat("Open one indoors and the smell can clear a whole building. It's been BANNED on airplanes.",
     "airplane with a red prohibition sign over a fish can, passengers fleeing",
     overlay="BANNED ON AIRPLANES")
beat("Banned. On airplanes. Let that sink in. Your lunch is legally a biohazard at thirty thousand feet.",
     "fish can wearing a tiny biohazard suit, clouds and airplane window behind")
beat("Brave Swedes eat it outdoors with flatbread, potatoes, and onions — always in August, always upwind.",
     "swedes eating fermented herring outdoors on a picnic, wind blowing away from them")
beat("Weirdness Score: nine and a half out of ten. Half a point from perfect. Which brings us to...",
     "scoreboard showing 9.5 out of 10, drumroll illustration")
# ---- #1 CASU MARZU ----
beat("NUMBER ONE. The undisputed champion of weird food. Casu Marzu.",
     "golden trophy shaped like a cheese wheel with a crown, confetti explosion")
beat("From the island of Sardinia, Italy. The name literally means... rotten cheese.",
     "map of sardinia island with a cheese wheel marked, italian flag colors")
beat("It starts as normal sheep's milk cheese. Then they introduce cheese fly larvae. Thousands of them.",
     "sheep in green pasture next to cheese wheels, tiny flies swarming")
beat("The maggots digest the cheese from the inside, breaking down the fats until it turns soft and gooey.",
     "cross-section of cheese with cartoon maggots munching tunnels inside")
beat("When served, the maggots are still alive. Wriggling. In your food. Right now.",
     "plate of soft cheese with live wiggling maggots, extreme close-up")
beat("Some say the maggots MUST be alive when you eat it — dead maggots mean the cheese has gone bad.",
     "cartoon maggot with a heartbeat line, alive stamp versus skull for dead")
beat("Disturb them and they launch up to six inches into the air. That's why you shield your eyes.",
     "maggots launching like rockets from cheese, ruler showing six inches")
beat("The European Union officially BANNED it as a health hazard. Sardinians eat it at weddings anyway.",
     "european union flag with a ban sign over cheese, wedding couple eating it happily")
beat("At WEDDINGS, people! This is celebration food! I cannot make this up!",
     "wedding table with a cheese tower centerpiece, guests cheering")
beat("There is nothing weirder you can legally — well, ILLEGALLY — put in your mouth.",
     "cartoon mouth about to eat cheese with maggots, police tape around")
beat("Weirdness Score: a perfect TEN out of ten. Casu Marzu is the weirdest food on planet Earth.",
     "scoreboard exploding at 10 out of 10, champion cheese with crown",
     overlay="10/10 WEIRDNESS CHAMPION")
# ---- RECAP + OUTRO ----
beat("So there it is — the final ranking. Seven foods, seven levels of why does this exist.",
     "podium with seven foods ranked from 7th to 1st place")
beat("Quick recap: century egg at six... balut at seven... escamoles at seven and a half...",
     "scoreboard recap showing first three scores with food icons")
beat("Kopi luwak at eight... poison shark at nine... airplane-banned herring at nine and a half...",
     "scoreboard recap showing next three scores with food icons")
beat("And the maggot cheese champion at a perfect ten.",
     "champion cheese wheel with golden 10 on podium top")
beat("Now tell me in the comments: which one would YOU actually try? Be honest.",
     "comment section illustration with question, viewers typing")
beat("Me? I'd try the century egg. The rest can stay in their countries. Far, far away from me.",
     "cartoon host pushing away plates of weird foods, century egg kept close")
beat("If this video broke your brain a little, subscribe to Weird World Daily — I find this stuff so you don't have to eat it.",
     "subscribe button with bell, host winking, weird foods in background",
     overlay="SUBSCRIBE!")
beat("New weird facts every single day. See you tomorrow — and maybe skip lunch today.",
     "calendar with daily weird fact icons, host waving goodbye")

batches = {}
CH = 12
for i in range(0, len(B), CH):
    key = f"batch{i//CH+1}"
    batches[key] = B[i:i+CH]

json.dump(batches, open(os.path.join(W, "data", "batches-b16.json"), "w"), indent=1, ensure_ascii=False)
print(f"beats: {len(B)}, batches: {len(batches)}")
words = sum(len(e["tts"].split()) for e in B)
print(f"kata: {words}")
for e in B:
    if "overlay" in e:
        print(f"  overlay b{e['num']}: {e['overlay']}")
