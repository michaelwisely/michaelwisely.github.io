---
myst:
  html_meta:
    description: How the skeleton on my garage door works, in plain English. Everything runs on one laptop, and no video is saved or sent anywhere.
---

# The Skeleton-inator 💀

```{rst-class} post-date
```
October 31, 2026

:::{admonition} 🔒 First things first: your privacy
:class: important privacy

- **The camera feed is processed live, on a laptop here at my house.** Each video frame is used for a split second to draw your skeleton, and then it's thrown away.
- **Nothing is saved.** No video, no pictures. Not one frame.
- **Nothing leaves the laptop.** The video isn't sent over the internet, to "the cloud," or anywhere else. The skeleton-inator doesn't even need an internet connection to run.
- **When this post says "AI," it means two small models running on that laptop.** It is *not* ChatGPT, Claude, Gemini, or any other chatbot. Nothing is sent to OpenAI, Anthropic, Google, or anyone else.
- **It doesn't know who you are.** There's no face recognition. It only works out where your elbows and knees are.

So go ahead and wave, dance, or do the Thriller. It stays in my driveway.
:::

## Behold!

*Ahem.*

Behold, the **SKELETON-INATOR!** With it, I will turn every trick-or-treater in the entire Tri-State Area into a *skeleton*! Mwahahaha!

...Temporarily. On my garage door. And then you get candy. 🍬

## What is this thing?

If you scanned the QR code out front, you probably just met your skeleton.

A camera watches the sidewalk. A laptop works out how your body is posed. A projector draws a matching skeleton on the garage door. Raise your arm, and your skeleton raises its arm. It's flipped like a mirror, so it moves the way you do. Bring friends: everybody gets their own skeleton.

## Why I built it

Every good -inator needs a tragic backstory. Mine isn't very tragic: I had a random idea and a big, blank garage door.

Mostly, it seemed like a fun excuse to play with some machine learning I'd been curious about. Specifically, *pose estimation*, which is a fancy way of saying "figuring out where someone's joints are from a picture."

I was also curious about combining different AI models. A lot of AI talk these days is about giant, do-everything chatbots. But there's another kind of AI: small models built to do *one* job really well. One model might be great at spotting people. Another might be great at finding joints. Neither one can make a skeleton by itself, but chained together, they can. I wanted to see what it's like to snap a few of those together like LEGO bricks.

It turned out to be a really fun way to learn. It was also a good reminder that the AI is only a small part of the work. Most of it is everything *around* the AI (more on that below).

## How it works

About 30 times every second, the skeleton-inator does this:

1. **Look.** A camera watches the sidewalk. It can see infrared light, and an infrared lamp lights up the sidewalk, so it works in the dark. Infrared is invisible to us (you might spot a faint red glow on the lamp, but that's it).
2. **Find the people.** The first model looks at the picture and draws a box around each person it sees.
3. **Find the joints.** The second model looks inside each box, one person at a time. It finds 17 points on the body: nose, eyes, ears, shoulders, elbows, wrists, hips, knees, and ankles.
4. **Keep track and smooth things out.** Regular, non-AI code keeps track of who's who from one moment to the next. It also smooths out the jitters so the bones don't shake.
5. **Draw.** The laptop connects the dots with glowing bones and sends the picture to a projector aimed at the garage door.

```{figure} img/how-it-works.svg
:class: diagram
:alt: Three panels. First, the camera view, with dashed boxes around a waving adult and a child. Second, a close-up of the adult with 17 dots on the nose, eyes, ears, shoulders, elbows, wrists, hips, knees and ankles. Third, a glowing skeleton on a dark garage door, waving back like a mirror image.

Find the people, find the joints, draw the skeleton. Repeat 30 times a second.
```

### Wait, what's a "model"?

A model is basically a file full of numbers. It was trained by showing it lots and lots of example pictures until it got good at one specific job. The two models in the skeleton-inator were made by Google and shared for anyone to use. I downloaded them once, ahead of time. Now they run entirely on the laptop and don't talk to anything on the internet.

### Why two models instead of one?

The joint-finding model is built to look at one person at a time. So the first model finds everybody, and the second model gets a close-up of each person. That close-up also helps with people who are far away: the joint finder gets a zoomed-in view instead of a tiny speck. Nerds call this a *top-down* approach: find the people first, then find their poses.

There was a practical reason, too. I originally designed the whole thing to run on a Coral Edge TPU, a little USB stick made for running AI models (more on how that went in the nerd section). Google publishes Coral-ready versions of exactly these two models, so that's what I built around.

## For the nerds 🤓

Want more detail? Tap any of these to open them up.

:::{dropdown} The two models

**Person finder:** [SSD MobileNet v2](https://github.com/google-coral/test_data), trained on the COCO dataset. COCO has about 80 kinds of everyday things in it; the skeleton-inator only cares about "person." The model looks at a 300×300 version of the camera frame.

**Joint finder:** [MoveNet SinglePose Lightning](https://www.tensorflow.org/hub/tutorials/movenet), released by Google in 2021. It takes a 192×192 crop around one person and returns 17 keypoints, each with a confidence score. "Lightning" is the small, fast version; "Thunder" is the bigger, more accurate one.

Both are **int8-quantized TensorFlow Lite models** from Google's Coral project. Quantized means the model's numbers are squeezed down to 8-bit integers. That makes the models smaller and faster, and it's required to run them on a Coral Edge TPU (more on that below). The download script checks each file's SHA-256 fingerprint, so I know I'm running exactly the model I think I am.

A few details that mattered:

- **No batching.** MoveNet's graph assumes one image at a time, so crops can't be batched together. Instead, crops run on a small pool of interpreters (2 interpreters × 2 threads each).
- **Careful duplicate removal.** Detectors often draw two boxes around the same person, so overlapping boxes get merged. But a kid standing in front of a grown-up also looks like "overlapping boxes"! So a box is only treated as a duplicate when it overlaps a lot (IoU ≥ 0.5) *and* is mostly inside the other box (≥ 85%). The kid survives.
- **Squash, don't letterbox.** The camera frame is wider than the detector's square input. Squashing it to fit worked better than adding black bars (letterboxing), which shrank far-away people until the detector missed them.
- **Confidence threshold of 0.3.** Lower than that and a phantom skeleton showed up. At 0.4, it started missing real people.
:::

:::{dropdown} Keeping track of who's who

The models only look at one frame at a time. They have no idea that the person in this frame is the same person from a moment ago. That's the tracker's job.

- **Matching.** Every frame, the new boxes get matched to the people already being tracked using the [Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm), a classic way to find the best one-to-one pairing. It runs in two passes. The first pass compares each new box with where each person *should* be if they kept walking at the same speed. The second pass catches leftovers by comparing against each person's recent path.
- **No stolen skeletons.** Both passes check that the heights roughly match, so a kid walking past a grown-up can't take over the grown-up's skeleton.
- **No flicker.** A new person stays hidden until they've been seen a few frames in a row, so one-off false alarms never show up. If someone is briefly hidden (say, behind a friend), their skeleton coasts for up to half a second. They can be picked up again as the same person for up to 2 seconds.
- **Things that never move don't count.** If the detector briefly mistakes a bush for a person, it won't get a skeleton, because it never walks anywhere.
:::

:::{dropdown} Smoothing out the jitters

Even when you stand perfectly still, the keypoints wiggle by a few pixels from frame to frame. Drawn as-is, the skeleton would shiver.

The fix is a [One Euro filter](https://gery.casiez.net/1euro/). It's a simple, clever filter that smooths a *lot* when things move slowly (no shivering while you stand still) and smooths *less* when things move fast (so a quick wave doesn't lag behind).

- There are two filters: one for the person's overall box, and one for the joints relative to that box.
- Speeds are measured in **body heights per second**, not pixels, so the smoothing behaves the same for someone right in front of the camera and someone far down the street.
- If the model isn't sure about a joint, that joint holds its last position relative to the body instead of flailing around.

On real footage, a person standing still came out 5–8× steadier than the raw keypoints. During tuning, I traded a little of that steadiness for snappier arms, which cut limb lag by about 12%.
:::

:::{dropdown} Drawing the skeleton (and the fake walk)

- The drawing is done with [pygame](https://www.pygame.org/), fullscreen on the projector.
- Each skeleton is stored relative to the person's own body (in body heights, measured from the feet). Then it's placed on a shared "ground line" on the door, flipped like a mirror, and scaled up. A cap keeps anybody's skull from going off the top of the door.
- The glow is drawn in layers off-screen, so overlapping bones don't pile up into bright blobs.
- Skeletons fade in after a few frames, and fade out when you leave. Single joints fade when the model isn't sure about them.
- **The fake walk:** if someone is clearly walking but the model can't make out their arms and legs (too far away, too dark), a canned side-view walking animation takes over. It only kicks in for people who are actually moving, and it only judges from frames where the person is actually visible.
:::

:::{dropdown} Benchmarks: laptop CPU vs. a Coral Edge TPU

A [Coral Edge TPU](https://developers.google.com/coral) is a little USB stick that's built to run AI models fast. I assumed it would be a big speedup. Spoiler: not on this project.

For these numbers I used OpenCV's public [`vtest.avi`](https://github.com/opencv/opencv/blob/4.x/samples/data/vtest.avi) test clip (a street with about 5 people in each frame), not footage of anyone visiting my house.

**Old laptop vs. newer laptop, CPU only:**

| | Old laptop (2011, Core i7-2675QM) | Newer laptop |
|---|---|---|
| Find people, per frame | ~21 ms | ~7.5 ms |
| Find joints, per person | ~16 ms | ~3 ms |
| Whole app, ~5 people in view | 8–9 frames/s, 110–125 ms delay | 30–41 frames/s, 23–35 ms delay |
| Temperature under load | 85–90 °C within minutes | steady ~70 °C |

**Adding the Coral (newer laptop, USB 3):**

| Setup | Time per frame |
|---|---|
| Everything on the CPU | ~22–25 ms |
| Everything on the Coral | ~65 ms (about 16 frames/s) |
| Person finder on the Coral, joints on the CPU | ~21–24 ms |

Why was the Coral slower? Each model alone was quick on it (about 7 ms for the person finder and 5.3 ms per person for the joint finder). But the two models together are about 10 MB, and the Coral only has about 8 MB of memory on the chip. So every time it switched from one model to the other, it had to reload over USB. That added about 14 ms when switching to the person finder, and 6.5 ms when switching to the joint finder. It also runs one thing at a time, while the CPU could work on a few people in parallel at ~3 ms each.

The Coral's answers did match the CPU's: 98% of people matched, and the joints were typically less than 2% of a body height apart.

On the old laptop, things went worse. On its USB 3 port, the Coral loaded fine and then froze on the very first run. That turned out to be the laptop's add-on USB 3 chip, not the Coral. On USB 2 it worked, but slowly: about 45 ms per run, plus about 200 ms every time it switched models.

**The verdict:** the newer laptop's CPU runs the show, and the Coral stays in the drawer for now. It might make more sense on a Raspberry Pi 5, where the CPU is slower.
:::

:::{dropdown} The camera, and picking a resolution

The camera is a small USB camera that can see infrared, paired with an 850 nm infrared lamp.

- **It was quietly running in low-res mode.** The camera only offers 1280×720 and 1920×1080 in a compressed format (MJPG). OpenCV picked the uncompressed format by default, and that silently dropped it to 640×480. Asking for MJPG fixed it.
- **I tested all three sizes** while standing still and walking on the sidewalk. At 640×480, the joints jittered about 2.7× more than at 1280×720, and the narrower picture showed about 25% less sidewalk. At 1920×1080, the camera only managed about 16 frames/s at night.
- **1280×720 won.** It runs at about 27–29 frames/s, and the model was confident about all 17 joints.
- **Plug in the laptop.** On battery, each frame took about 16–22 ms to process instead of about 10 ms. Still fast enough, but there's no reason to give that up.
:::

:::{dropdown} Tuning it on real (infrared) footage

To tune everything, we recorded about 2½ minutes of video of ourselves walking around the driveway at night with the infrared camera. That was recorded on purpose, by us, for testing. The skeleton-inator itself never records anything.

Results on that footage:

- People were found in 95.5% of frames. Most misses lasted only a frame or two, and the tracker covers those.
- A skeleton was on screen 97–100% of the time someone was there.
- Zero phantom skeletons. Porch lights, the parked car, and the bush were all ignored.
- Each person kept one identity the whole time, even when one of us hid the other.

Things that *didn't* help: converting to greyscale, boosting contrast, and adjusting brightness (gamma) all made the detector find *fewer* people. The camera's raw picture worked best.
:::

:::{dropdown} Privacy, the nerdy version

- The camera is read by a background thread that only ever keeps the **latest** frame. Older frames are dropped immediately.
- Frames are never written to disk. There's an automated test that fails if the code ever uses anything that saves video or images. It's strict enough that I once had to work around it just to build a camera format code, because the usual way to do that lives on OpenCV's `VideoWriter` class.
- What *does* stick around is a few numbers per person (a box and 17 points), in memory only, for tracking and smoothing. Those are forgotten a couple of seconds after someone walks away.
- The running app doesn't use the network. The only download is a one-time setup step that fetches the two model files and checks their fingerprints. To double-check, I ran the app on a test video while logging every network connection it tried to make. It made zero internet connections. (It did talk to the computer's own internal messaging system, which never leaves the machine.)
- The models don't recognize faces or identify anyone. The tracker's "identities" are just temporary numbers like "person 3," and they're gone once you leave.
:::

:::{dropdown} Tools and libraries

**The skeleton-inator:**

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) for reading the camera (and a debug view while testing)
- [LiteRT](https://developers.google.com/edge/litert) (`ai-edge-litert`), Google's runtime for TensorFlow Lite models
- [NumPy](https://numpy.org/) for the math
- [pygame](https://www.pygame.org/) for drawing and fullscreen projector output
- `libedgetpu` for the Coral experiments
- [uv](https://docs.astral.sh/uv/) for Python packages, [Nix](https://nixos.org/) for a reproducible dev environment, and [Task](https://taskfile.dev/) to run common commands
- [ruff](https://docs.astral.sh/ruff/), [pyright](https://github.com/microsoft/pyright), and [pytest](https://pytest.org/) to keep me honest

**This blog:** [Sphinx](https://www.sphinx-doc.org/) with [MyST Markdown](https://myst-parser.readthedocs.io/), the [Furo](https://github.com/pradyunsg/furo) theme, and [sphinx-design](https://sphinx-design.readthedocs.io/) for these dropdowns. It's also built in a Nix shell.
:::

## Things that went wrong

*Curse you, Perry the Platypus!*

- **The fancy AI accelerator lost to the plain old laptop.** Measure, don't guess. (Details in the benchmarks dropdown above.)
- **The old laptop got *hot*.** Like, 85–90 °C hot, and at one point it throttled itself way down. The newer laptop doesn't break a sweat.
- **The camera was secretly running in low-res mode** this whole time, until I measured it.
- **Skeletons doing the wrong walk.** The backup walking animation kept kicking in whenever someone was briefly hidden behind somebody else. Fixed.
- **The self-destruct button.** Every one of Dr. Doofenshmirtz's -inators has a self-destruct button. Mine doesn't. But for a while it crashed every single time I closed it, which is basically the same thing.

## What I learned

- **Small, specialized models are surprisingly capable,** and they run fine on an ordinary laptop. No cloud required.
- **The AI is the easy part.** Keeping track of people, smoothing, drawing, and testing in my driveway in the dark were most of the work.
- **Measure everything.** My guesses about what would be fast (and what resolution the camera was using) were wrong more than once.

## What's next?

Maybe next year: move it to a Raspberry Pi 5 with the Coral, fancier bone artwork, and... who knows. A pumpkin-inator? 🎃

## Quick questions

Is it recording me?
: No. Nothing is saved, and nothing leaves the laptop. See the box at the top.

Does it work for kids?
: Yes! I made sure a kid standing in front of a grown-up gets their own skeleton (and can't steal the grown-up's).

How many people can it handle at once?
: In testing, it kept up just fine with about five people in view.

What about big costumes?
: Most costumes are fine. Really puffy ones (inflatable dinosaurs, I'm looking at you 🦖) might confuse it. I haven't had a chance to test one yet, so if you have one, please walk by. For science.

## Credits

- **The models:** SSD MobileNet v2 and MoveNet SinglePose Lightning, both from Google.
- **The name:** Dr. Heinz Doofenshmirtz, of course. Happy Halloween!
