"""Builds the redesigned chrisgraham.com pages into public/. Run: python3 tools/build_pages.py"""
from pathlib import Path
PUB = Path(__file__).resolve().parent.parent / "public"
DEMO_CAL = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ10SsalUOGGpzSoOXuZ3v7gF1d3zU4MYZzFTYRjQ_7vG8WL_9Gnl7pk6asMU6KB5RCKDi5oAPMR?gv=true"
COACH_CAL = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ1-VGVWWYNfrSQrDKYHftvYSVGdpfXllBoDmyraeJPamM7YJJi-oJP6w_nvDw68OPglKfl-gIrf?gv=true"
PROOF = "Trusted by Emmy, Grammy, Oscar &amp; Tony winners, legislators &amp; business leaders."

def page(name, title, desc, body):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://chrisgraham.com/img/db94ef689a40893f7c2f06e3bbd460e9.webp">
<link rel="icon" href="/img/c2e3b450f67cc23d729637b56ec75c23.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<main class="wrap">
{body}
</main>
<footer>Chris Graham · AI Coach · Fugio Consulting · Granville, Ohio<br>
<a href="/coaching">AI Coaching</a> · <a href="/pete">Pete the Pigeon</a> · <a href="/about">About</a> · <a href="https://petethepigeon.com">PeteThePigeon.com</a> · <a href="https://x.com/chrisgraham">X</a> · <a href="https://www.youtube.com/channel/UCHMlIDbKT86qGk4LGvBfD_g">YouTube</a></footer>
<script src="/assets/site-nav.js"></script>
</body>
</html>
"""
    (PUB / f"{name}.html").write_text(html, encoding="utf-8")

def book(cal, eyebrow, heading, blurb):
    return f"""  <section class="book" id="book">
    <div class="eyebrow">{eyebrow}</div>
    <h2>{heading}</h2>
    <p>{blurb}</p>
    <iframe class="cal" title="Book a time with Chris Graham" loading="lazy" src="{cal}"></iframe>
  </section>"""

IMG = "/img/"
PRESS = [
 ("Sept. 8, 2021","ddca01b54936adc2c4b8dd5e8dd29368.png","'There's no escape': Memories of priest haunt Ohio man","\"Those wounds were so deep ... I was broken,\" Graham said. \"Trauma echoes throughout your life until you begin to heal.\"","https://www.dispatch.com/in-depth/news/2021/09/08/columbus-man-raped-catholic-priest-child-haunted-memories/7504888002/","Columbus Dispatch"),
 ("Sept. 8, 2021","3b748af51a4f271f194785850b521fbc.jpg","'I'm going to change these laws': survivor seeks legal reform in Ohio","Experts have repeatedly said Ohio's laws on child sexual abuse are some of the worst in the nation.","https://www.dispatch.com/story/news/2021/09/08/chris-graham-leads-ohios-fight-against-priest-sex-abuse-statutes-limitation/8014830002/","Columbus Dispatch"),
 ("Aug. 11, 2022","4375f72570e7d01faad926ec13e20692.jpg","Ohio survivors of Boy Scout sexual abuse push for change to statute of limitations","\"I ... felt in my bones, I should be fighting for them.\"","https://www.wosu.org/politics-government/2022-08-10/ohio-survivors-of-boy-scout-sexual-abuse-push-for-change-to-statute-of-limitations","WOSU"),
 ("Dec. 1, 2022","22f2c1ecd84138631745b2d9bd0a1cd3.png","Ohio House passes \"Scout's Honor\" bill to help Boy Scout abuse survivors","Under the old statute of limitations, Ohio survivors would only get 30% to 45% of what they might be eligible to receive.","https://www.10tv.com/article/news/politics/ohio-house-passes-scouts-honor-law-bill-to-help-boy-scout-abuse-survivors/530-162dc9bc-dd01-4c5f-bb1f-f7db29d3482f","10TV"),
 ("Sept. 27, 2023","4375f72570e7d01faad926ec13e20692.jpg","Senate passes law as deadline looms for Ohio sexual abuse survivors","\"Survivors of Boy Scouts in Ohio should get the same opportunities for justice as survivors from any other state. Period.\"","https://www.wosu.org/politics-government/2023-09-27/ohio-senate-passes-scouts-honor-law-as-deadline-looms-for-survivors-to-get-cash-from-settlement","WOSU"),
 ("Sept. 28, 2023","95bd098be6548a6cbf9816bdf68fad4a.jpg","Ohio Boy Scouts survivors can recover full settlements","Senator Kunze remarked that it was the sustained advocacy of survivors, specifically Chris Graham, that put The Scout's Honor Law before the Senate.","https://www.nbc4i.com/news/politics/senate-passes-bill-to-allow-ohio-boy-scouts-survivors-to-recover-full-settlements/","NBC4"),
 ("Mar. 21, 2024","d91402e7d6d963d8f36c98c0020ede21.webp","Alabama Legislature sends 'Scout's Honor' bill to governor","Alabama follows Ohio's lead for Boy Scout survivors.","https://alabamareflector.com/2024/03/21/alabama-legislature-sends-scouts-honor-bill-to-gov-kay-ivey/","Alabama Reflector"),
 ("Apr. 24, 2024","1da92d25a856334d4c9e8c04dc5c9a1f.jpg","Bill to outlaw spousal rape set for vote at Ohio Statehouse","\"There are coming of age moments, and in Ohio, this is one of them.\"","https://www.nbc4i.com/news/local-news/columbus/bill-to-remove-spousal-rape-exception-and-more-set-for-vote-at-ohio-statehouse/","NBC4"),
 ("Apr. 11, 2025","a165ea2411bbdf32af046e9de786dee5.jpg","Survivor leads fight for grooming law in Ohio","For survivors like Graham, the hope is that this law will deter predators and protect future generations.","https://www.10tv.com/article/news/local/ohio-grooming-law-combat-child-sexual-abuse/530-c7f28c85-3aa7-46fc-9f35-00acda227ac1","10TV"),
]
GALLERY = [
 ("b0bce2fb9c55e9216c8d90b010bed4b3.jpg","Rep. Mohamed looks on as we celebrate passing the first Scout's Honor Law in Ohio. Mike Taylor and I had no idea Alabama, Indiana &amp; Iowa would copy our law."),
 ("67fa9e846399263cb91c023781c665cf.jpg","Signed, sealed &amp; delivered. Ohio's spousal rape exemption is finally dead. Reps. Hillier &amp; Miranda with Gov. DeWine, bipartisan style."),
 ("573ddcfd2b2018559167a290fe800b73.jpg","Mujaddid Muhammad, a Boy Scout survivor, walks into the Ohio Statehouse to testify for our bill."),
 ("351ef1fe9cec957860a169a903b32031.jpg","Mike Taylor &amp; David DeLapa, Boy Scout survivors, the day the Scout's Honor Law went into effect."),
 ("012d96658457667ba5d977417ec13ca7.jpg","Rep. Jessica Miranda. Very different perspectives, an amazing friendship."),
 ("fdf27e5cbfac9e6383a4ef4863a947c0.jpg","Essie Baird goes public about the childhood abuse of her track coach &amp; 6th grade teacher. Colleen Marshall interviews."),
 ("0e8ce15c19f67a2d78962de813273d78.jpg","At the Ohio Statehouse, I'm not allowed past those doors. Members only. The lobby is a great place to invite legislators into deeper waters."),
 ("6614ebd633b9fd2b8c28e8a9fb8df383.jpg","The Statehouse is full of interesting people. From left to right, I work with all of them."),
 ("99248ae27d2f2042088ed59055533c6b.jpg","David spoke out as a Boy Scout survivor for the first time, and I taught him to be a citizen lobbyist."),
 ("16c2b312eff55e4739c2ee37189ef1cd.jpg","Years ago I mastered Paisha's first record. Now we're trying to get her people's land back."),
 ("20200af0bb78032a243b8eb44f916684.jpg","Rep. Jarrells speaks at a Juneteenth press conference about The Randolph Freed People."),
 ("0fda7c10da14055c17418a20f274af62.jpg","People bring their stories to the Statehouse. It's beautiful to watch folks use their voice."),
]

# ---------------- HOME ----------------
page("index", "Chris Graham · AI Coach",
 "AI Coach Chris Graham built Pete the Pigeon, helped pass Ohio's Scout's Honor Law, and is trusted by Emmy, Grammy, Oscar & Tony winners, legislators and business leaders.",
f"""  <header class="hero">
    <div>
      <div class="eyebrow">Chris Graham · AI Coach</div>
      <h1>I help people put AI to work, and I use it to pass laws.</h1>
      <p class="lead">I built Pete the Pigeon, the Ohio Statehouse's AI wonk. I've helped write and pass bipartisan laws that other states copied. {PROOF}</p>
      <div class="cta-row">
        <a class="btn" href="#book">Book a demo &amp; AI strategy audit</a>
        <a class="btn ghost" href="https://petethepigeon.com">Try Pete free</a>
      </div>
    </div>
    <img src="{IMG}db94ef689a40893f7c2f06e3bbd460e9.webp" alt="Chris Graham" width="1080" height="922">
  </header>

  <section>
    <div class="eyebrow">At the Ohio Statehouse</div>
    <h2>Laws I've helped write and pass</h2>
    <p class="muted">No party, no law degree, not elected, not hired. Just a citizen lobbyist who gets things done with modern tools.</p>
    <div class="grid3">
      <div class="card"><h3>The Scout's Honor Law</h3><p>Passed unanimously in Ohio. Copied by Alabama, Indiana &amp; Iowa. A path to justice for 5,000+ survivors.</p></div>
      <div class="card"><h3>Spousal rape exemption, repealed</h3><p>Almost 40 years of back-room deals, ended. Signed by Gov. DeWine.</p></div>
      <div class="card"><h3>Grooming a child, now a crime</h3><p>A law meant to deter predators and protect the next generation of Ohio kids.</p></div>
    </div>
    <p class="quote">Senator Kunze remarked that it was the sustained advocacy of survivors, specifically Chris Graham, that put The Scout's Honor Law before the Senate.<span>NBC4, Sept. 28, 2023 · <a href="/about#press">More press</a></span></p>
    <figure class="photo">
      <img src="{IMG}67fa9e846399263cb91c023781c665cf.jpg" alt="Rep. Hillier, Gov. DeWine and Rep. Miranda at the spousal rape exemption repeal signing" loading="lazy">
      <figcaption>Signed, sealed &amp; delivered. Reps. Hillier &amp; Miranda with Gov. DeWine, bipartisan style.</figcaption>
    </figure>
  </section>

  <section>
    <div class="pete">
      <img src="{IMG}pete-the-pigeon.png" alt="Pete the Pigeon">
      <div>
        <div class="eyebrow">What I built</div>
        <h2>Pete the Pigeon</h2>
        <p>All of Ohio's public record in one chat, with a source on every answer. The smartest wonk in the Statehouse, in your pocket.</p>
        <ul class="ticks">
          <li>Every bill, vote, hearing and word of testimony</li>
          <li>Campaign finance and JLEC filings: follow the money on any bill</li>
          <li>All 132 legislators: what they've said, sponsored and posted</li>
          <li>Works inside ChatGPT, Claude and Outlook</li>
        </ul>
        <div class="cta-row">
          <a class="btn" href="https://petethepigeon.com">Get your free account</a>
          <a class="btn ghost" href="/pete">Why I'm building Pete</a>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="eyebrow">AI Coaching</div>
    <h2>Emmy, Grammy, Oscar &amp; Tony winners. Legislators in both parties. Business leaders.</h2>
    <p>I started as a mastering engineer, working with thousands of independent artists and labels like Sony, Warner and Disney, then co-founded the recording industry's first business podcast. When it went viral, award winners started asking for coaching. I've been building AI since 2010. Today I help them, and legislators, advocates and business leaders, figure out where AI fits in their work and put it to use.</p>
    <p style="margin-top:18px"><a class="btn ghost" href="/coaching">AI coaching for leaders</a></p>
  </section>

  <section class="prose">
    <div class="eyebrow">Why I do this</div>
    <h2>Just do the next scary thing.</h2>
    <p>During COVID, my life fell apart. Rock bottom led me to EMDR therapy, where I uncovered memories of escaping a child trafficking ring and abuse by a priest. I was shattered, but I found a path forward: just do the next scary thing.</p>
    <p>That path led me to the Statehouse. One of the most meaningful moments of my life was sitting beside my sons in the Ohio Senate before a unanimous vote to pass The Scout's Honor Law. They watched their dad's crazy idea claw back justice for 1,911 Ohio survivors.</p>
    <p><a href="/about">Read the whole story</a></p>
  </section>

{book(DEMO_CAL, "20 minutes", "Book a demo &amp; personal AI strategy audit", "I'll show you Pete and tell you where AI fits in your work. No pitch deck.")}
""")

# ---------------- COACHING ----------------
page("coaching", "AI Coaching for Leaders · Chris Graham",
 "AI coaching for leaders from Chris Graham, trusted by Emmy, Grammy, Oscar & Tony winners, legislators and business leaders.",
f"""  <header class="hero">
    <div>
      <div class="eyebrow">AI Coaching for Leaders</div>
      <h1>Work smarter with AI to accomplish your mission.</h1>
      <p class="lead">{PROOF} I've built AI since 2010, and I use it every day to pass laws and run a company.</p>
      <div class="cta-row"><a class="btn" href="#book">Pick a time</a></div>
    </div>
    <img src="{IMG}611de5c0f12e2f467bffcda6f028cac9.jpg" alt="Chris Graham coaching" loading="lazy" style="border-radius:12px">
  </header>

  <section>
    <div class="eyebrow">How it works</div>
    <h2>A personal AI strategy, built around your work</h2>
    <div class="grid3">
      <div class="card"><h3>Audit</h3><p>We look at how you spend your time and where AI can take work off your plate.</p></div>
      <div class="card"><h3>Build</h3><p>We set up the tools and workflows that fit you, not a generic playbook.</p></div>
      <div class="card"><h3>Coach</h3><p>When obstacles show up, the path forward is the same: do the next scary thing.</p></div>
    </div>
    <div class="video"><iframe src="https://www.youtube.com/embed/tSjhGT-T8XM" title="Chris Graham on AI" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
  </section>

{book(COACH_CAL, "Discovery call", "Pick a time that works for you", "Tell me what you're working on and we'll figure out where AI fits.")}
""")

# ---------------- PETE ----------------
page("pete", "Pete the Pigeon · Chris Graham",
 "Chris Graham is building Pete the Pigeon, Ohio's Statehouse AI, as a 100% employee-owned company.",
f"""  <header class="hero">
    <div>
      <div class="eyebrow">What I'm building</div>
      <h1>An advocacy AI company in Ohio, owned by the people who build it.</h1>
      <p class="lead">The product is Pete the Pigeon. The place is Ohio. The point is that a regular person should be able to walk into their own government and know as much as the lobbyist sitting across from them.</p>
      <div class="cta-row">
        <a class="btn" href="https://petethepigeon.com">Go ask Pete something</a>
        <a class="btn ghost" href="/#book">Book a demo</a>
      </div>
    </div>
    <img src="{IMG}pete-the-pigeon.png" alt="Pete the Pigeon" style="max-width:320px;margin:0 auto">
  </header>

  <section>
    <div class="eyebrow">Meet Pete</div>
    <h2>Pete the Pigeon</h2>
    <p>Pete is an AI who knows the Ohio Statehouse the way a twenty-year veteran staffer knows it, and answers anybody who asks, for free. Over a million lines of code. Sixteen years of building agentic AI, here in Ohio.</p>
    <ul class="ticks">
      <li>Every legislator, every lobbyist, every bill, every vote, every hearing, every campaign dollar</li>
      <li>A source on every answer, so you can check his work</li>
      <li>Works inside ChatGPT, Claude and Outlook</li>
    </ul>
    <p>I believe he is the most powerful advocacy technology Ohio has ever had. He is built to help every Ohioan, to make advocacy easier, and to make Ohio's government run better.</p>
  </section>

  <section id="employee-ownership">
    <div class="eyebrow">One hundred percent employee owned</div>
    <h2>I'm not building this to flip it.</h2>
    <p>I am building it so the people who do the work own the thing they made. Employee ownership is the whole design, not a perk bolted on at the end. That is also why the work is public. If the plan is to hand the company to the people who build it, the plan should be something you can read.</p>
    <div class="grid2">
      <div class="card"><h3>I podcast about it</h3><p><em>Champeons of Employee Ownership</em> is the show I make with Tim Rettig about companies owned by the people who work in them, and what it takes to build one.</p><p style="margin-top:10px"><a href="https://champeonsofemployeeownership.com">Listen</a></p></div>
      <div class="card"><h3>I teach it out loud</h3><p>I teach AI for the public good, in a room, with anybody who wants to come.</p><p style="margin-top:10px"><a href="https://www.youtube.com/channel/UCHMlIDbKT86qGk4LGvBfD_g">Watch on YouTube</a></p></div>
    </div>
  </section>

{book(DEMO_CAL, "20 minutes", "See Pete for yourself", "A 20-minute demo and a personal AI strategy audit.")}
""")

# ---------------- ABOUT ----------------
press = "\n".join(f"""      <a class="item" href="{u}" target="_blank" rel="noopener"><img src="{IMG}{img}" alt="" loading="lazy"><div><div class="date">{d} · {outlet}</div><h3>{h}</h3><p>{q}</p></div></a>""" for d,img,h,q,u,outlet in PRESS)
gal = "\n".join(f"""      <figure><img src="{IMG}{i}" alt="" loading="lazy"><figcaption>{c}</figcaption></figure>""" for i,c in GALLERY)
page("about", "About · Chris Graham",
 "Chris Graham's story: survivor, citizen lobbyist, AI coach and builder of Pete the Pigeon.",
f"""  <header class="hero">
    <div>
      <div class="eyebrow">About</div>
      <h1>Just do the next scary thing.</h1>
      <p class="lead">Singer-songwriter, mastering engineer, podcaster, AI builder, citizen lobbyist, dad. Home is a log cabin in the woods near Granville, Ohio.</p>
    </div>
    <img src="{IMG}db94ef689a40893f7c2f06e3bbd460e9.webp" alt="Chris Graham" width="1080" height="922">
  </header>

  <section class="prose">
    <div class="eyebrow">My story</div>
    <h2>From the recording studio to the Statehouse</h2>
    <p>My first business was being a singer-songwriter. Touring, selling records, playing with bands. Then I became a music producer and audio mastering engineer. About ten years in, after working with thousands of independent artists and major labels like Sony, Warner and Disney, a friend and I launched the first business podcast for the recording industry. When it went viral, people started asking for business coaching. Before I knew it, I was helping Emmy, Grammy, Oscar and Tony winners grow their businesses and themselves.</p>
    <p>In 2020, Covid shut everything down, and my life and mental health fell apart. Luckily, right before my breakdown, I had built the first agentic AI in the audio industry. Bounce Butler was a hit, and recording studios around the world still use him every day. The income my little AI brought in was just enough to keep the wheels on while I hit rock bottom, was hospitalized, diagnosed with PTSD, and started EMDR therapy.</p>
    <p>EMDR was the hardest thing I have ever done. I uncovered repressed memories of escaping a child trafficking ring. I finally met myself, and on the other side of some healing, I found the recipe for post-traumatic growth: just do the next scary thing.</p>
    <p>That path led me to the Statehouse. One of the most meaningful moments of my journey was sitting beside my sons in the Ohio Senate before a unanimous vote to pass The Scout's Honor Law. A few senators stood and spoke about a priest survivor who fought for Ohio's scout survivors and won. My sons watched as their dad's crazy idea clawed back justice for 1,911 survivors in Ohio.</p>
    <p>Then we started hearing from across the country. Alabama, Indiana and Iowa passed The Scout's Honor Law too. 5,000+ survivors now had a path to justice, and hundreds of millions of dollars in settlements.</p>
    <p>Today I'm building movements for employee owners, survivors and award-winning creatives. I've been part of building movements that changed the world, but the best thing I've ever done is show my kids that no matter how dark your path is, life is always full of possibilities.</p>
  </section>

  <section id="press">
    <div class="eyebrow">In the news</div>
    <h2>Press</h2>
    <div class="press">
{press}
    </div>
  </section>

  <section>
    <div class="eyebrow">In the wild</div>
    <h2>At the Statehouse</h2>
    <p class="muted">I'm a photography nerd, so I usually have a camera with me. Weird vintage lenses, black and white only.</p>
    <div class="gallery">
{gal}
    </div>
  </section>

  <section class="prose">
    <div class="eyebrow">Making a documentary</div>
    <h2>The Randolph Freed People</h2>
    <p>I've been producing a documentary at the Ohio Statehouse with filmmaker <a href="https://www.ianscook.com/documentary">Ian Cook</a>. The story centers on The Randolph Freed People, 382 freed slaves whose land was stolen right after they found their freedom in 1844.</p>
    <figure class="photo"><img src="{IMG}6dc58ebe6ca27c11f07c88590c29295d.jpg" alt="" loading="lazy"><figcaption><a href="https://www.wosu.org/arts-culture/2024-06-17/justice-for-the-randolph-freedpeople-telling-their-story-and-returning-their-land">WOSU: Justice for the Randolph Freedpeople</a></figcaption></figure>
  </section>

{book(COACH_CAL, "Say hello", "Grab a time on my calendar", "Coaching, speaking, or a fight worth fighting. Let's talk.")}
""")
print("built: index coaching pete about")
