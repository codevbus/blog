---
title: "consumed content week ending 03-06-20"
author: ["Mike Vanbuskirk"]
publishDate: 2020-03-06
lastmod: 2020-03-05T23:30:20-05:00
slug: "consumed-content-week-ending-03-06-20"
tags: ["career", "tech", "deep learning", "ai", "machine learning", "entrepreneurship", "programming", "math", "statistics", "gaming", "operations", "devops", "ci/cd", "tech", "entrepreneurship", "startup", "health", "learning", "career", "mastery", "reading", "observability", "operations", "ux", "devops", "sre"]
categories: ["Consumed Content"]
draft: false
toc: false
lastmod: false
---

## Summary {#summary}

My quest to reduce friction in publishing weekly content continues. I've got a template created via [yasnippets](https://github.com/joaotavora/yasnippet) with some lisp to automatically populate the date. Regardless of when I create the file, the date will always be Friday of the current week. Unfortunately I'm still having to manually grep for my "finished" timestamps. Next on the to-do list is to find a way to automate searching for last week's timestamps, and populating the fields below. Once that's done, automating the tag generation for the post should be trivial.

All that being said, I want to be careful to emphasize that my goal is to reduce the friction, as much as possible, that is present in writing and publishing. It is _not_ the idea to automate the entire act, "soup-to-nuts". The act of purposeful consideration and summation of what I've read or listened to is the real benefit in doing this, and will ideally allow the creation of novel and unique ideas of my own.

Content-wise, I definitely enjoyed this week. The podcasts were awesome, and I even managed to read a(brief) research paper from Google. Some awesome blog posts as well, covering things from startup burnout and mental health to software deployment.

Hope everyone has a good weekend, and does their best to stay healthy.


### Podcasts {#podcasts}

-   [Andrew Ng: Deep Learning, Education, and Real-World AI | MIT | Artificial Intelligence Podcast](https://lexfridman.com/andrew-ng/) - One of the "OG's" of AI and deep learning. There was a ton of great discussion here, including career advice, and some powerful guidance on forming good habits and self-driven learning.7G
-   [Programming Throwdown: Episode 99: Squashing bugs using AI and Machine Learning](https://www.programmingthrowdown.com/2020/02/episode-99-squashing-bugs-using-ai-and.html) - An interview with CEO of <https://www.deepcode.ai/>. They offer a service that essentially consumes **all** of the code for a given language on GitHub, and uses that data to make suggestions as you code. They offer a [VSCode](https://marketplace.visualstudio.com/items?itemName=DeepCode.deepcode) extension right now, as well as commercial licensing. This has the potential to be a powerful tool in terms of reducing bugs _prior_ to deployment.
-   [Michael I. Jordan: Machine Learning, Recommender Systems, and the Future of AI | MIT | Artificial Intelligence Podcast](https://lexfridman.com/michael-i-jordan/) - The "Miles Davis" of AI. Another amazingly interesting conversation from this podcast. Jordan believes we're far from AGI(Artificial General Intelligence), but still sees a lot of potential in current applications. I found the discussion around niche markets created by AI especially interesting, as this isn't the first time I've heard that paradigm mentioned.
-   [The Worst Video Game Ever](https://99percentinvisible.org/episode/the-worst-video-game-ever/transcript/) - This was a fun, quick dive into the history of the "worst video game ever". I won't spoil it, but it basically sunk a billion dollar(in 1983 money!) industry single-handedly. Anyone who's ever been involved in software engineering should not be surprised to learn a sub-standard product was shipped after a single engineer was asked to deliver it in _five weeks_.


### Articles/Blogs {#articles-blogs}

-   [How to Deploy Software](https://zachholman.com/posts/deploying-software) - A technical deep-dive on operational and technical best-practices in making software deployment as pain-free as possible. As a devops engineer, this topic is near and dear to my heart.
-   [Post YC Depression](https://www.bmaho.com/articles/post-yc-depression) - A poignant article from a startup founder who lived the dream of going to Silicon Valley to run a startup, only to burnout and collapse after an unsuccessful year of 80+ hour weeks. Add this to the growing list of repudiations of "hustle porn" and the idolatry of working yourself to death.
-   [Finite and Infinite Games: Two Ways to Play the Game of Life](https://fs.blog/2020/02/finite-and-infinite-games-two-ways-to-play-the-game-of-life/) - Do you play the long game or the short game? This post is only a brief summary of the ideas in a book(which I plan to read), but the general idea is infinite players, those that want to continue the game, look to educate themselves for what _may_ come. In contrast, finite players seek immediate power, with little concern for future unknowns.


### Papers {#papers}

-   [Meaningful availability – the morning paper](https://blog.acolyer.org/2020/02/26/meaningful-availability/) - A team of engineers at Google, primarily responsible for the service health of G-Suite services like GMail, wanted a better way to quantify what it meant for their application to be "available", primarily from an end-user's perspective. They came up with "windowed user uptime". This is a great, fairly easy read, and should be of great interest to anyone in the SRE/DevOps space. The only difficult math is if you decide to follow the proof of the metric's monotonicity.
