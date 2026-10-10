---
permalink: /
title: "Guanyu Xu 徐冠宇"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
projects:
  # List order = display order. Everything else (image, links, authors, period, venue, excerpt)
  # is read from the `ref` file's front matter; `title` optionally overrides its title.
  course:
    - ref: _research/01.OpticalSensor.md
      title: "Proprioceptive Membrane for 3D Shape Reconstruction"
    - ref: _portfolio/01.SmartGlass.md
      title: "INSIGHT: Smart Assistive Glass"
    - ref: _portfolio/02.LumenGrid.md
      title: "Lumen Grid: Multi-Robot Parking Game"
---
Hi I'm Guanyu Xu, an undergraduate student pursuing dual degrees in Computer Engineering at the **University of Michigan** and Mechanical Engineering at **Shanghai Jiao Tong University**.

My research interest primarily focuses on **embodied intelligence and robotics**. I am particularly interested in combining robotic foundation models with simulation-based RL to enable agile, generalizable robotic behaviors in the real world. My prior work is grounded in **full-stack robotic systems**, with expertise in mechanical design and smart manufacturing, embedded and real-time systems, and closed-loop sensorimotor control.

In addition to research, I maintain a [**portfolio**](https://xuguaaaanyu.github.io/portfolio/) of course projects that reflects my hands-on experience. I also occasionaly update my learning notes in the [**blog**](https://xuguaaaanyu.github.io/nerd/).


## News
{% include news.html %}

## Selected Projects
{% include project_list.html projects=page.projects.course kind="course" %}