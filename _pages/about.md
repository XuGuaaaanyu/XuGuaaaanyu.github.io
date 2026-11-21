---
permalink: /
title: "Guanyu Xu 徐冠宇"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
homepage: true
projects:
  # List order = display order. Everything else (image, links, authors, period, venue, excerpt)
  # is read from the `ref` file's front matter; `title` optionally overrides its title.
  research:
    - ref: _research/01.OpticalSensor.md
      title: "Proprioceptive Membrane for 3D Shape Reconstruction"
  course:
    - ref: _portfolio/01.SmartGlass.md
      title: "INSIGHT: Smart Assistive Glass"
    - ref: _portfolio/02.LumenGrid.md
      title: "Lumen Grid: Multi-Robot Parking Game"
---
<div class="home-intro" markdown="1">
I'm a master's student in **Robotics at the University of Pennsylvania**. During my undergraduate studies, I worked with Prof. Xiaonan Huang at the University of Michigan and Prof. Hesheng Wang at Shanghai Jiao Tong University.

I work on robot sensing and control: reconstructing the shape of soft sensors from optical signals, and learning policies that let a robotic hand reorient objects using proprioception. My projects connect sensor hardware and embedded systems with learning-based perception and control.
</div>

## Education

<ul class="education-list">
  <li>
    <img class="education-logo education-logo--light" src="{{ '/images/education/penn.png' | relative_url }}" alt="University of Pennsylvania logo" width="72" height="72" loading="lazy">
    <img class="education-logo education-logo--dark" src="{{ '/images/education/penn-dark.png' | relative_url }}" alt="University of Pennsylvania logo" width="72" height="72" loading="lazy">
    <div class="education-details"><div class="education-heading"><h3>University of Pennsylvania</h3><span class="education-period">2026–2028 · Expected</span></div>
    <p>M.S.E. in Robotics</p></div>
  </li>
  <li>
    <img class="education-logo" src="{{ '/images/education/michigan.svg' | relative_url }}" alt="University of Michigan logo" width="72" height="72" loading="lazy">
    <div class="education-details"><div class="education-heading"><h3>University of Michigan</h3><span class="education-period">2024–2026</span></div>
    <p>B.S.E. in Computer Engineering</p></div>
  </li>
  <li>
    <img class="education-logo" src="{{ '/images/education/sjtu.png' | relative_url }}" alt="Shanghai Jiao Tong University logo" width="72" height="72" loading="lazy">
    <div class="education-details"><div class="education-heading"><h3>Shanghai Jiao Tong University</h3><span class="education-period">2022–2026</span></div>
    <p>B.E. in Mechanical Engineering</p></div>
  </li>
</ul>

## News
{% include news.html %}

<div class="home-section-heading">
  <h2 id="research-projects">Research Projects</h2>
  <a href="{{ '/research/' | relative_url }}" class="section-link">All research <i class="fas fa-external-link-alt" aria-hidden="true"></i></a>
</div>
{% include project_list.html projects=page.projects.research kind="research" %}

<div class="home-section-heading">
  <h2 id="course-projects">Course Projects</h2>
  <a href="{{ '/portfolio/' | relative_url }}" class="section-link">Full portfolio <i class="fas fa-external-link-alt" aria-hidden="true"></i></a>
</div>
{% include project_list.html projects=page.projects.course kind="course" %}
