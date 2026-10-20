#!/usr/bin/env python3
"""Tulis script/beats-2026-10-20.json: 75 beat, ~1100 kata, dark psychology eduktif.
Topik: 7 Ways Social Media Secretly Hijacks Your Brain (baru, tidak di riwayat).
"""
import json, os

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
STYLE = ("dark storybook 2D illustration, 16:9 widescreen, "
         "moody psychological lighting, deep shadows")

B = []  # (narration, image_desc, insight?, chapter?)

def beat(nar, img, insight=False, chapter=None):
    B.append({"narration": nar, "image": f"{img}, {STYLE}",
              "insight": insight, "chapter": chapter})

# --- HOOK + INTRO (1-5) ---
beat("At two in the morning on a random Tuesday, I caught myself scrolling through "
     "a stranger's vacation photos, feeling miserable about my own perfectly fine life.",
     "A man in bed at 2 AM, face lit by phone glow, scrolling miserably")
beat("That is when I realized something uncomfortable. My phone was not entertaining me. "
     "It was training me.",
     "A smartphone with glowing puppet strings attached to a man's hands in darkness")
beat("Tonight: seven psychological weapons hidden inside your social media feed, "
     "designed by the smartest engineers on Earth.",
     "A smartphone screen revealing seven glowing hooked weapons inside it")
beat("Not to teach you evil. So you can see the game being played on you, and stop losing it.",
     "A lantern of light pushing back a swarm of shadowy hands")
beat("Have you ever lost a whole hour to scrolling without ever deciding to? "
     "Tell me about it in the comments.",
     "A giant hourglass made of a phone screen, time sand falling through")
# --- personal + transisi (6-7) ---
beat("I used to brag that I had self control. Then my screen time report said five hours a day. "
     "Five hours.",
     "A glowing screen time report showing five hours, a shocked man staring at it")
beat("Let us start with weapon number one. And it is the one you use every single day.",
     "A glowing countdown number one over a smartphone in darkness")
# --- CH1: Infinite Scroll (8-13) ---
beat("Weapon one: the infinite scroll.", "A long endless conveyor belt feed rolling into dark infinity", chapter="The Infinite Scroll")
beat("Old websites had pages. You reached the bottom, you got a stopping cue, and your brain said: done.",
     "A webpage with a visible bottom edge next to an endless bottomless feed")
beat("Engineers deleted the bottom. The feed never ends, so your brain never gets the signal to stop.",
     "An engineer's hand deleting the bottom of a webpage with an eraser", insight=True)
beat("A casino has no windows and no clocks. Your feed works exactly the same way.",
     "A windowless casino full of glowing slot machines, no clocks on walls")
beat("People spend up to three times longer on feeds that never end. That is not an accident.",
     "A bar chart showing time spent tripling on an endless feed")
beat("Fix it with friction. Use apps with an end, or set a hard timer before you open the feed.",
     "A smartphone locked inside a small cage with a kitchen timer on top")
# --- CH2: Variable Rewards (14-20) ---
beat("Weapon two: variable rewards.", "A slot machine with a pull down refresh lever and like icons as symbols", chapter="Variable Rewards")
beat("Every pull to refresh is a slot machine spin. Maybe a like. Maybe nothing. Maybe a viral moment.",
     "A hand pulling down to refresh a phone screen like a slot machine lever")
beat("I have caught myself pulling to refresh like a gambler at a casino. This one hit close to home.",
     "A man at a slot machine slowly morphing into a man staring at a phone")
beat("Your brain releases more dopamine on unpredictable rewards than on guaranteed ones. "
     "They know this.",
     "A human brain with dopamine sparks flying around a glowing phone")
beat("Likes, comments, new followers. Each one is a pellet in the largest conditioning experiment ever run.",
     "A laboratory experiment with reward pellets dropping as a man taps his phone")
beat("That little red badge is not information. It is a promise that maybe something good is waiting.",
     "A glowing red notification badge shining like a siren in the dark")
beat("You are not checking your phone. You are pulling the lever. And the casino always wins.",
     "A casino dealer collecting chips from a row of phone staring players", insight=True)
# --- CH3: Outrage Algorithm (21-27) ---
beat("Weapon three: the outrage algorithm.", "A giant mechanical eye sorting angry red posts to the top", chapter="The Outrage Algorithm")
beat("The algorithm does not care what you feel. It cares how long you stay. "
     "And nothing holds attention like anger.",
     "A calm blue post sinking down while a furious red post rockets upward", insight=True)
beat("A post that makes you calm gets ignored. A post that makes you furious gets shared, "
     "commented, and boosted.",
     "A furious comment thread multiplying with share arrows in every direction")
beat("Every angry comment teaches the machine one lesson: show this person more of what upsets them.",
     "A puppet hand feeding an angry face more rage filled posts")
beat("You think you are informing yourself. You are being fed the most enraging version of reality, on purpose.",
     "A man reading news through a funhouse mirror that distorts everything")
beat("Here is the counter move. When a post makes your blood boil, that is exactly when you put the phone down.",
     "A hand calmly putting down a phone while an angry post glows on screen")
beat("Calm never goes viral. Your anger is the product being sold to advertisers.",
     "A price tag hanging on a pile of anger, labeled as the product", insight=True)
# --- CH4: Comparison Trap (28-34) ---
beat("Weapon four: the comparison trap.", "A phone showing perfect vacation photos while a messy real room sits behind it", chapter="The Comparison Trap")
beat("Nobody posts their laundry pile. Everyone posts the highlight reel.",
     "A person posting glamorous photos while hiding a pile of laundry")
beat("Psychologists call it upward social comparison. Your brain compares your behind the scenes "
     "to everyone else's stage.",
     "A brain comparing a small plain self to a giant polished stranger")
beat("The result is predictable. The more you scroll, the worse you feel about a life that is actually fine.",
     "A mood meter needle dropping lower as scrolling continues")
beat("Even the influencers feel it. They compare themselves to someone with better filters.",
     "Two influencers anxiously comparing their follower counts")
beat("I once felt like a failure next to a guy my age with a yacht. Then I learned the yacht was rented for the photo.",
     "A small man feeling tiny next to a giant rented yacht photo")
beat("You are comparing your real life to an advertisement. The game is rigged from the start.",
     "A split screen: dull real life on one side, glossy advertisement on the other", insight=True)
# --- CH5: Notification Conditioning (35-41) ---
beat("Weapon five: notification conditioning.", "A ringing bell with sound waves controlling a reaching hand", chapter="Notification Conditioning")
beat("That ping is Pavlov's bell. You have been trained to salivate for approval on command.",
     "A man salivating like Pavlov's dog at the sound of a phone ping")
beat("Engineers tested thousands of notification schedules. They found the exact timing that makes you reach.",
     "An engineer with a stopwatch testing notification timing on a giant phone")
beat("Phantom vibration syndrome. People feel their phone buzz when it never did. That is how deep the training goes.",
     "A phone vibrating with ghost waves in an empty pocket")
beat("Your phone lets you batch notifications into one daily digest for a reason. One check a day breaks the spell.",
     "A stack of notifications bundled neatly into one single daily digest")
beat("Turn off everything except messages from actual humans you know. Watch how quiet your mind gets.",
     "A phone settings screen with almost all notifications toggled off")
beat("Your attention is the most valuable thing you own. Stop giving it away for free.",
     "A golden crown labeled attention being handed away for nothing", insight=True)
# --- CH6: FOMO Loop (42-48) ---
beat("Weapon six: the manufactured FOMO loop.", "A 24 hour countdown timer over a row of disappearing stories", chapter="The FOMO Loop")
beat("Stories that vanish in twenty four hours. Streaks that break if you skip a single day.",
     "A flame streak icon chaining two friends together like a contract")
beat("Your brain fears losing something twice as much as it enjoys gaining it. That is loss aversion.",
     "A balance scale with loss weighing far heavier than gain in a brain")
beat("A little flame next to a friend's name turns a friendship into an obligation.",
     "A chain of flame icons linking friends together like handcuffs")
beat("'Live now' notifications create fake urgency for events that do not matter at all.",
     "A fake live now siren blaring over a completely empty stage")
beat("When everyone watches the same drama, skipping it feels like exile from the tribe.",
     "A tribe gathered around a glowing drama screen, one outsider standing apart")
beat("You are not afraid of missing out. You are being threatened with missing out, on purpose.",
     "A hand holding a threatening letter stamped with FOMO", insight=True)
# --- CH7: Echo Chamber (49-55) ---
beat("Weapon seven: the echo chamber.", "A human head trapped inside a glass bubble hearing only its own voice", chapter="The Echo Chamber")
beat("The algorithm learns what you believe, then feeds you only proof that you are right.",
     "A thumbs up vote feeding a machine that builds a custom made world", insight=True)
beat("Every like is a vote. The machine builds a world where you are always the hero and they are always wrong.",
     "A person as a hero in a custom world built by voting machines")
beat("Two people can live in the same country and see two completely different realities.",
     "Two people side by side seeing two different realities through their phones")
beat("Outrage plus echo chamber. You end up angrier and more certain than you have ever been.",
     "A man growing angrier inside a mirrored room of his own opinions")
beat("The antidote is discomfort. Deliberately follow people you disagree with.",
     "A person uncomfortably following someone with opposing views")
beat("A mind that is never challenged is a mind that is being managed.",
     "A chained mind on one side, a mind breaking free on the other", insight=True)
# --- RECAP (56-60) ---
beat("All seven weapons, named. Write these down.", "Seven glowing weapons laid out and labeled on a dark table", chapter="All 7 Hijacks, Named")
beat("One: the infinite scroll. Two: variable rewards. Three: the outrage algorithm.",
     "Glowing numbers one two three over a dark smartphone")
beat("Four: the comparison trap. Five: notification conditioning.",
     "Glowing numbers four and five over a dark smartphone")
beat("Six: manufactured FOMO. Seven: the echo chamber.",
     "Glowing numbers six and seven over a dark smartphone")
beat("Remember this. You were never the customer of these apps. You were always the product.",
     "A price tag hanging on a human silhouette labeled product")
# --- COUNTER MOVES (61-67) ---
beat("Now the counter moves. Three defenses that actually work.",
     "A glowing shield with three defense symbols on a dark background", chapter="The Counter Moves")
beat("Defense one: turn your screen grayscale. Color is a drug for your attention.",
     "A phone screen with all colors draining away into gray")
beat("Defense two: delete the apps, use the browser. A little friction is freedom.",
     "Social apps being deleted, only a simple browser icon remaining")
beat("Defense three: the twenty minute rule. After twenty minutes, the app goes dark for the day.",
     "A twenty minute hourglass over a phone that goes dark")
beat("These sound small. That is the point. You do not defeat a trillion dollar machine with willpower alone.",
     "A tiny pebble cracking a giant war machine")
beat("The moment you notice the manipulation is the moment it stops working on you.",
     "An eye opening wide as puppet strings snap above it", insight=True)
beat("You are not weak for falling for this. It was engineered by thousands of experts. But now you know.",
     "A person standing strong against a tidal wave of notifications")
# --- OUTRO + CTA (68-75) ---
beat("So tell me honestly. Which of these seven caught you the most?",
     "A giant question mark hovering over seven glowing traps", chapter="Your Turn")
beat("Number them one through seven in the comments. I read every single one.",
     "Rows of comment bubbles filled with numbers one through seven")
beat("If this rewired how you see your own phone, subscribe to Dark Mind Files.",
     "A glowing subscribe button on a dark screen")
beat("A new dark psychology episode every single day. Built to make you sharper, not angrier.",
     "A calendar with a new episode marked on every single day")
beat("Tomorrow: the exact words manipulators use to make you doubt your own memory.",
     "Shadowy words swirling over a doubting human mind")
beat("Hit the bell, so the algorithm works for you for once.",
     "A notification bell ringing while algorithm gears turn for the viewer")
beat("Stay sharp out there. Your mind is the only feed worth curating.",
     "A sharp glowing mind shaped like a carefully curated garden")
beat("I will see you tomorrow.",
     "A dark doorway with warm light, a host silhouette waving goodbye")

assert len(B) == 75, f"beat count {len(B)} != 75"
beats = []
for i, b in enumerate(B, 1):
    beats.append({"id": f"beat-{i:03d}", **b})
total_words = sum(len(b["narration"].split()) for b in beats)
print(f"beats={len(beats)} kata={total_words} insight={[b['id'] for b in beats if b['insight']]}")
out = os.path.join(BASE, "script", "beats-2026-10-20.json")
json.dump({"beats": beats, "topic": "7 Ways Social Media Secretly Hijacks Your Brain",
           "date": "2026-10-20"}, open(out, "w"), indent=1)
print("OK", out)
