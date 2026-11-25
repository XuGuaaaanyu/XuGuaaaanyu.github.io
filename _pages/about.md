---
permalink: /
title: "Guanyu Xu 徐冠宇"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
home_layout: true   # homepage styling (body class "homepage")
# Project cards below are picked from _research/ and _portfolio/ files with `homepage: true`,
# newest `date` first. Nothing to edit here when adding a project.
---
<div class="home-intro" markdown="1">
Hi! I'm a first-year master's student in **Robotics** at the [University of Pennsylvania](https://www.grasp.upenn.edu/). I received dual bachelor's degrees from Shanghai Jiao Tong University and the [University of Michigan](https://ece.engin.umich.edu/), where I was advised by Prof. [Xiaonan Huang](https://robotics.umich.edu/people/faculty/xiaonan-sean-huang/).

I'm broadly interested in **embodied intelligence and robotics**, with a focus on robotic foundation models and sim-to-real reinforcement learning. I'm also interested in building dedicated hardware for robotic data collection. My prior work involves **full-stack robotic systems**, spanning [embedded systems](/projects/SmartGlass/), [mechanical design](/projects/Wheel/), and hardware manufacturing. 

</div>

## News

{% include news.html %}

<div class="home-section-heading">
  <h2 id="research-projects">Research Projects</h2>
  <a href="{{ '/research/' | relative_url }}" class="section-link">All research <i class="fas fa-external-link-alt" aria-hidden="true"></i></a>
</div>
{% include project_list.html collection="research" kind="research" homepage=true %}

<div class="home-section-heading">
  <h2 id="course-projects">Course Projects</h2>
  <a href="{{ '/projects/' | relative_url }}" class="section-link">All projects <i class="fas fa-external-link-alt" aria-hidden="true"></i></a>
</div>
{% include project_list.html collection="portfolio" kind="course" homepage=true %}

<div class="home-section-heading">
  <h2 id="education">Education</h2>
</div>
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

{% if site.mapmyvisitors.map_id %}
<div class="visitor-map">
  <a href="https://mapmyvisitors.com/web/{{ site.mapmyvisitors.web_id }}" title="Visit tracker" target="_blank" rel="noopener">
    <img src="https://mapmyvisitors.com/map.png?cl=ffffff&w=300&t=n&d={{ site.mapmyvisitors.map_id }}" alt="Visitor map" loading="lazy">
  </a>
</div>
{% endif %}
