---
myst:
  html_meta:
    description: How my Halloween skeleton projector works, in plain English. It all runs on one laptop, and no video is saved or sent anywhere.
---

# The Skeleton-inator

```{rst-class} post-date
```
October 31, 2026

:::{admonition} First things first: your privacy
:class: important privacy

The skeleton-inator runs **entirely on one laptop** here at my house.

- The camera feed is processed live.
  Each frame is used for a split second to draw your skeleton, and then it's thrown away.
- **Nothing is saved.**
  No video, no pictures.
  Not one frame.
- Nothing leaves the laptop.
  The video isn't sent over the internet, to the cloud, or anywhere else.
  It doesn't even need an internet connection to run.
- When this post says "AI", it means two small models running on that laptop.
  It's **not** ChatGPT, Claude, Gemini, or any other chatbot.
  Nothing gets sent to OpenAI, Anthropic, Google, or anyone else.
- It doesn't know who you are.
  There's no face recognition.
  It only figures out where your elbows and knees are.

So wave away.
None of it leaves my driveway.
:::

## Behold!

_Ahem._

Behold, the **SKELETON-INATOR!**
With it, I will turn every trick-or-treater in the entire Tri-State Area[^tristate] into a _skeleton_!
Mwahahaha!

... Temporarily.
On my garage door.
And then you get candy.

## So, what is this thing?

The skeleton-inator is a Halloween decoration.
A camera watches the sidewalk, a laptop figures out how your body is posed, and a projector draws a matching skeleton on the garage door.
Raise your arm, and your skeleton raises its arm.

It's flipped like a mirror, so it moves the way you do.
Bring friends.
Everybody gets their own skeleton.

Well, that was the plan.

Uh...

I misplaced the power supply for my projector[^psu] 😭, so it didn't make it out this year.

That said, I think it was still a fun project, so I wanted to do the write-up anyway.

## Why I built it

Every good -inator needs a tragic backstory.
Mine isn't very tragic: I had a random idea and a big, blank garage door.

Mostly, it seemed like a fun excuse to play with some machine learning I'd been curious about.
Specifically, _pose estimation_.
That is, figuring out where someone's joints are from a picture.

I was also curious about combining different AI models.
A lot of AI talk these days is about giant chatbots that do everything.

However, there's another kind of AI: small models that do _one_ job really well.
One is great at spotting people.
Another is great at finding joints.

Neither one can make a skeleton by itself, but chained together, they can.

It turned out to be a really fun way to learn.
It was also a good reminder that the AI is a pretty small part of the work.
Most of it is everything _around_ the AI (more on that below).

## How it works

About 30 times every second, the skeleton-inator...

1. looks at the sidewalk with a camera that can see infrared light.
   An infrared lamp lights things up, so it works in the dark.
   (People can't see infrared. You might spot a faint red glow on the lamp, but that's it.)
2. finds the people.
   The first model draws a box around each person it sees.
3. finds the joints.
   The second model looks inside each box, one person at a time, and finds 17 points: nose, eyes, ears, shoulders, elbows, wrists, hips, knees, and ankles.
4. keeps track of who's who, and smooths out the jitters so the bones don't shake.
   This part is regular code, not AI.
5. draws glowing bones between the dots and sends the picture to a projector aimed at the garage door.

That's it!
Well, that's the short version.

```{figure} img/how-it-works.svg
:class: diagram
:alt: Three panels. First, the camera view, with dashed boxes around a waving adult and a child. Second, a close-up of the adult with 17 dots on the nose, eyes, ears, shoulders, elbows, wrists, hips, knees and ankles. Third, a glowing skeleton on a dark garage door, waving back like a mirror image.

Find the people, find the joints, draw the skeleton. Repeat 30 times a second.
```

### Wait, what's a "model"?

A model is basically a file full of numbers[^numbers].
It was trained on lots and lots of example pictures until it got good at one specific job.

The two models in the skeleton-inator were made by Google and shared for anyone to use.
I downloaded them once, ahead of time.
Now they run entirely on the laptop and don't talk to anything on the internet.

### Why two models instead of one?

The joint-finding model is built to look at one person at a time.
So, the first model finds everybody, and the second model gets a close-up of each person.

That close-up also helps with people who are far away.
The joint finder gets a zoomed-in view instead of a tiny speck.
Nerds call this a _top-down_ approach: find the people first, then find their poses.

There was a practical reason, too.
I originally designed the whole thing to run on a Coral Edge TPU, a little USB stick made for running AI models (more on how _that_ went below).
Google publishes Coral-ready versions of exactly these two models, so that's what I built around.

## For the nerds

Want more detail?
Tap any of these to open them up.

:::{dropdown} The two models

The person finder is [SSD MobileNet v2](https://github.com/google-coral/test_data), trained on the COCO dataset.
COCO has about 80 kinds of everyday things in it, but the skeleton-inator only cares about "person".
It looks at a 300×300 version of the camera frame.

The joint finder is [MoveNet SinglePose Lightning](https://www.tensorflow.org/hub/tutorials/movenet), released by Google in 2021.
It takes a 192×192 crop around one person and returns 17 keypoints, each with a confidence score.

"Lightning" is the small, fast version.
"Thunder" is the bigger, more accurate one.

Both are int8-quantized TensorFlow Lite models from Google's Coral project.
That is, the model's numbers are squeezed down to 8-bit integers.
That makes them smaller and faster, and it's required to run them on a Coral Edge TPU.

The download script checks each file's SHA-256 fingerprint, so I know I'm running exactly the model I think I am.

A few details that mattered:

- MoveNet's graph assumes one image at a time, so crops can't be batched together.
  Instead, they run on a small pool of interpreters (2 interpreters × 2 threads each).
- Detectors often draw two boxes around the same person, so overlapping boxes get merged.
  However, a kid standing in front of a grown-up _also_ looks like overlapping boxes.
  - So, a box only counts as a duplicate when it overlaps a lot (IoU ≥ 0.5) **and** is mostly inside the other box (≥ 85%).
    The kid survives.
- The camera frame is wider than the detector's square input.
  Squashing it to fit worked better than adding black bars (letterboxing), which shrank far-away people until the detector missed them.
- The confidence threshold is 0.3.
  Any lower and a phantom skeleton showed up.
  At 0.4, it started missing real people.

TL;DR -- One model finds people, the other finds their joints, and both come in versions that run on the Coral.
:::

:::{dropdown} Keeping track of who's who

The models only look at one frame at a time.
They have no idea that the person in this frame is the same person from a moment ago.
That's the tracker's job.

- Every frame, new boxes get matched to the people already being tracked using the [Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm), a classic way to find the best one-to-one pairing.
  It takes two passes:
  - The first pass compares each new box with where each person _should_ be if they kept walking at the same speed.
  - The second pass catches leftovers by comparing against each person's recent path.
- Both passes check that the heights roughly match, so a kid walking past a grown-up can't steal the grown-up's skeleton.
- A new person stays hidden until they've been seen a few frames in a row, so one-off false alarms never show up.
- If someone is briefly hidden (say, behind a friend), their skeleton coasts for up to half a second.
  They can be picked up again as the same person for up to 2 seconds.
- Things that never move don't get skeletons.
  If the detector briefly mistakes a bush for a person, it doesn't matter, because the bush never walks anywhere[^bush].
:::

:::{dropdown} Smoothing out the jitters

Even when you stand perfectly still, the keypoints wiggle by a few pixels from frame to frame.
Drawn as-is, the skeleton would shiver[^cold].

The fix is a [One Euro filter](https://gery.casiez.net/1euro/).
It's a pretty clever filter that smooths a _lot_ when things move slowly and smooths _less_ when things move fast.
That is, no shivering while you stand still, and no lag when you wave.

- There are two filters: one for the person's box, and one for the joints relative to that box.
- Speeds are measured in **body heights per second**, not pixels.
  That way, the smoothing behaves the same for someone right in front of the camera and someone way down the street.
- If the model isn't sure about a joint, that joint holds its last spot relative to the body instead of flailing around.

On real footage, a person standing still came out 5–8× steadier than the raw keypoints.
During tuning, I traded a little of that for snappier arms, which cut limb lag by about 12%.
:::

:::{dropdown} Drawing the skeleton (and the fake walk)

- The drawing is done with [pygame](https://www.pygame.org/), fullscreen on the projector.
- Each skeleton is stored relative to the person's own body (in body heights, measured from the feet).
  It gets placed on a shared "ground line" on the door, flipped like a mirror, and scaled up.
  - There's a cap, so that nobody's skull goes off the top of the door.
- The glow is drawn in layers off-screen, so that overlapping bones don't pile up into bright blobs.
- Skeletons fade in after a few frames and fade out when you leave.
  Single joints fade when the model isn't sure about them.

There's also a fake walk.
If someone is clearly walking but the model can't make out their arms and legs (too far away, too dark), a canned side-view walking animation takes over.

It only kicks in for people who are actually moving, and it only judges from frames where the person is actually visible.
:::

:::{dropdown} Benchmarks: laptop CPU vs. a Coral Edge TPU

A [Coral Edge TPU](https://developers.google.com/coral) is a little USB stick built to run AI models fast.
I assumed it would be a big speedup.
Spoiler: not on this project.

For these numbers, I used OpenCV's public [`vtest.avi`](https://github.com/opencv/opencv/blob/4.x/samples/data/vtest.avi) clip (a street with about 5 people in each frame), not footage of anyone visiting my house.

Here's the old laptop vs. the newer laptop, CPU only:

| | Old laptop (2011, Core i7-2675QM) | Newer laptop |
|---|---|---|
| Find people, per frame | ~21 ms | ~7.5 ms |
| Find joints, per person | ~16 ms | ~3 ms |
| Whole app, ~5 people in view | 8–9 frames/s, 110–125 ms delay | 30–41 frames/s, 23–35 ms delay |
| Temperature under load | 85–90 °C within minutes | steady ~70 °C |

And here's what happened when I added the Coral to the newer laptop (USB 3):

| Setup | Time per frame |
|---|---|
| Everything on the CPU | ~22–25 ms |
| Everything on the Coral | ~65 ms (about 16 frames/s) |
| Person finder on the Coral, joints on the CPU | ~21–24 ms |

So, why was the Coral slower?
Each model alone was quick on it: about 7 ms for the person finder, and 5.3 ms per person for the joint finder.
The catch is memory.

The two models together are about 10 MB, and the Coral only has about 8 MB on the chip.
It's like a desk that only fits one book.
Every time you switch books, you have to walk back to the shelf.

For the Coral, that walk is a reload over USB.
It cost about 14 ms when switching to the person finder, and 6.5 ms when switching to the joint finder.

It also runs one thing at a time, while the CPU can work on a few people in parallel at ~3 ms each.

FWIW, the Coral's answers matched the CPU's.
98% of people matched, and the joints were typically less than 2% of a body height apart.

On the old laptop, the Coral and the USB 3 port did _not_ get along.
The Coral loaded fine and then froze on its very first run.
That turned out to be the laptop's add-on USB 3 chip, not the Coral.

On USB 2 it worked, but slowly: about 45 ms per run, plus about 200 ms every time it switched models.

TL;DR -- The newer laptop's CPU runs the show, and the Coral stays in the drawer for now[^drawer].
It might make more sense on a Raspberry Pi 5, where the CPU is slower.
I haven't measured that yet, though.
:::

:::{dropdown} The camera, and picking a resolution

The camera is a small USB camera that can see infrared, paired with an 850 nm infrared lamp.

It was quietly running in low-res mode.
The camera only offers 1280×720 and 1920×1080 in a compressed format (MJPG), and OpenCV picked the uncompressed one by default.

So, it silently dropped to 640×480.
Asking for MJPG fixed it.

Then we tested all three sizes while standing still and walking on the sidewalk:

- At 640×480, the joints jittered about 2.7× more than at 1280×720, and the narrower picture showed about 25% less sidewalk.
- At 1920×1080, the camera only managed about 16 frames/s at night.
- At 1280×720, it runs at about 27–29 frames/s, and the model was confident about all 17 joints.
  Winner.

One more thing: plug in the laptop.
On battery, each frame took about 16–22 ms to process instead of about 10 ms.
Still fast enough, but there's no reason to give that up.

TL;DR -- 1280×720, ask for MJPG, and plug the laptop in.
:::

:::{dropdown} Tuning it on real (infrared) footage

To tune everything, we recorded about 2½ minutes of ourselves walking around the driveway at night with the infrared camera.
We recorded that on purpose, for testing.
The skeleton-inator itself never records anything.

Here's how it did on that footage:

- It found people in 95.5% of frames.
  Most misses lasted a frame or two, and the tracker covers those.
- A skeleton was on screen 97–100% of the time someone was there.
- Zero phantom skeletons.
  Porch lights, the parked car, and the bush were all ignored.
- Each of us kept one identity the whole time, even when one of us hid the other.

Some things _didn't_ help.
Converting to greyscale, boosting contrast, and adjusting brightness (gamma) all made the detector find _fewer_ people.
The camera's raw picture worked best.
:::

:::{dropdown} Privacy, the nerdy version

- The camera is read by a background thread that only keeps the **latest** frame.
  Older frames get dropped immediately.
- Frames are never written to disk.
  There's an automated test that fails if the code uses anything that saves video or images.
  - It's strict enough that I once had to work around it just to build a camera format code, because the usual way to do that lives on OpenCV's `VideoWriter` class.
- What _does_ stick around is a few numbers per person (a box and 17 points), in memory only, for tracking and smoothing.
  Those get forgotten a couple of seconds after someone walks away.
- The running app doesn't use the network.
  The only download is a one-time setup step that fetches the two model files and checks their fingerprints.
  - To double-check, I ran the app on a test video while logging every network connection it tried to make.
    It made zero internet connections.
    (It did talk to the computer's own internal messaging system, which never leaves the machine.)
- The models don't recognize faces or identify anyone.
  The tracker's "identities" are just temporary numbers like "person 3", and they're gone once you leave.
:::

:::{dropdown} Tools and libraries

For the skeleton-inator:

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) for reading the camera (and a debug view while testing)
- [LiteRT](https://developers.google.com/edge/litert) (`ai-edge-litert`), Google's runtime for TensorFlow Lite models
- [NumPy](https://numpy.org/) for the math
- [pygame](https://www.pygame.org/) for drawing and fullscreen projector output
- `libedgetpu` for the Coral experiments
- [uv](https://docs.astral.sh/uv/) for Python packages, [Nix](https://nixos.org/) for a reproducible dev environment, and [Task](https://taskfile.dev/) to run common commands
- [ruff](https://docs.astral.sh/ruff/), [pyright](https://github.com/microsoft/pyright), and [pytest](https://pytest.org/) to keep me honest

For this blog: [Sphinx](https://www.sphinx-doc.org/) with [MyST Markdown](https://myst-parser.readthedocs.io/), the [Furo](https://github.com/pradyunsg/furo) theme, and [sphinx-design](https://sphinx-design.readthedocs.io/) for these dropdowns.
It's also built in a Nix shell.
:::

## Things that went wrong

- The big one: I misplaced the projector's power supply, so the skeleton-inator sat out Halloween this year.
- The fancy AI accelerator lost to the plain old laptop.
  Measure, don't guess.
  (Details in the benchmarks section above.)
- The old laptop got _hot_.
  Like, 85–90 °C hot.
  It did not care for it, and at one point it throttled itself way down[^guy].
- The camera was secretly running in low-res mode, and I didn't notice until I measured it.
- Skeletons were doing the wrong walk.
  The backup walking animation kept kicking in whenever someone was briefly hidden behind somebody else.
  Fixed now.
- Every one of Dr. Doofenshmirtz's -inators has a self-destruct button.
  Mine doesn't.
  However, for a while it crashed every... single... time I closed it, which is basically the same thing.

## What I learned

- Small, specialized models are pretty capable, and they run fine on an ordinary laptop.
  No cloud required.
- I think the AI is the easy part.
  Tracking people, smoothing, drawing, and testing in my driveway in the dark were most of the work.
- Measure everything.
  My guesses about what would be fast (and what resolution the camera was using) were wrong more than once.

## What's next?

Maybe next year I'll try again (and look for my projector bits ahead of time...) and add more to it.

Moving it to a Raspberry Pi 5 with the Coral and making some fancier bone artwork are both on the list.

## Quick questions

Is it recording me?
: Nope.
  Nothing is saved, and nothing leaves the laptop.
  See the box at the top.

Does it work for kids?
: Yep!
  I made sure a kid standing in front of a grown-up gets their own skeleton (and can't steal the grown-up's).

How many people can it handle at once?
: In testing, it kept up just fine with about five people in view.

Does my dog get a skeleton?
: Probably not.
  The person finder only cares about people.
  Your dog will have to go as a ghost.

What about big costumes?
: Most costumes should be fine.
  Really puffy ones might confuse it (inflatable dinosaurs, I'm looking at you 🦖).
  I haven't tested one yet, so if you've got one next year, please walk by... for science.

## Credits

The models are SSD MobileNet v2 and MoveNet SinglePose Lightning, both from Google.
The name comes from Dr. Heinz Doofenshmirtz, of course.

Happy Halloween!

[^tristate]: Which three states?
    Don't worry about it.

[^psu]: It's in a box somewhere.
    I'm sure of it.
    Mostly.

[^numbers]: Yeah, yeah, it's more complicated than that.
    Don't worry about it for now.

[^drawer]: A different drawer than the projector power supply, hopefully.

[^bush]: Not yet, anyway.
    It's a spooky time of year.

[^cold]: Fair enough.
    It has no skin.

[^guy]: Come on, guy.
