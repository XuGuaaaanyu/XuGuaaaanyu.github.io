---
permalink: /
title: "Guanyu Xu 徐冠宇"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
projects:
  research:
    - title: "Proprioceptive Membrane for 3D Shape Reconstruction"
      url: /research/optical-sensor/
      image: /images/optical_sensor/cover.png
      alt: "Optical Sensor teaser"
      authors: ["Guanyu Xu", "Jiaqi Wang", "Dezhong Tong", "Xiaonan Huang"]
      desc: "A soft, stretchable optical waveguide sensor with embedded LEDs and photodiodes for learning-based 3D deformation reconstruction."
      date: "2026-01"
      venue: "ArXiv Preprint"
      tags:
        - label: "Paper"
          href: "https://arxiv.org/pdf/2601.13574"
          icon: "fas fa-file-pdf"
          new_tab: true
        - label: "Code"
          href: "https://github.com/GuanyuXu04/ShapeNet"
          icon: "fab fa-github"
          new_tab: true
        - label: "Video"
          href: "https://www.youtube.com/watch?v=_Gzyzb5R1V0"
          icon: "fab fa-youtube"
          new_tab: true

  course:
    - title: "INSIGHT: Smart Assistive Glass"
      url: /portfolio/01.SmartGlass/
      image: /images/glass/teaser.png
      alt: "Smart Glass teaser"
      authors: ["Guanyu Xu", "Haobo Fang", "Ruopu Dong", "Yizhe Shen", "Zhuoyang Chen", "Jinlin Li"]
      desc: "In-device navigation and scene interpretation glasses for low-vision users."
      date: "Fall 2025"
      venue: "EECS 473: Advanced Embedded Systems (UM)"
      tags:
        - label: "Poster"
          href: /files/SmartGlass/poster.pdf
          icon: "fas fa-file-pdf"
          new_tab: true
        - label: "Report"
          href: /files/SmartGlass/report.pdf
          icon: "fas fa-file-pdf"
          new_tab: true
        - label: "Code"
          href: "https://github.com/GuanyuXu04/Smart_Glass"
          icon: "fab fa-github"
          new_tab: true
        - label: "Video"
          href: "https://www.youtube.com/watch?v=iU_iTmCLjYo"
          icon: "fab fa-youtube"
          new_tab: true
    
    - title: "Lumen Grid: Multi-Robot Parking Game"
      url: /portfolio/02.LumenGrid/
      image: /images/parking/teaser.png
      alt: "Lumen Grid teaser"
      authors: ["Guanyu Xu", "Haobo Fang", "Varun Agrawal", "Xiang Jiang"]
      desc: "A competitive parking game using four Zumo robots on an LED-marked field."
      date: "Winter 2025"
      venue: "EECS 373: Introduction to Embedded System Design (UM)"
      tags:
        - label: "Poster"
          href: /files/LumenGrid/poster.pdf
          icon: "fas fa-file-pdf"
          new_tab: true
        - label: "Code"
          href: "https://github.com/XuGuaaaanyu/Lumen_Grid"
          icon: "fab fa-github"
          new_tab: true
        - label: "Video"
          href: "https://www.youtube.com/watch?v=jwMOQGUDSMY"
          icon: "fab fa-youtube"
          new_tab: true
    
    # - title: "Rover with Transformable Wheels"
    #   url: /portfolio/03.Wheel/
    #   image: /images/wheel/teaser.png
    #   alt: "Transformable Wheel teaser"
    #   authors: ["Guanyu Xu", "Jiawen Li", "Yimin Wang", "Haobo Fang"]
    #   desc: "A rover equipped with transformable wheels for cluttered terrain navigation."
    #   date: "Summer 2024"
    #   venue: "ME3500J: Design and Manufacturing (SJTU)"
    #   tags:
    #     - label: "Report"
    #       href: /files/Wheel/report.pdf
    #       icon: "fas fa-file-pdf"
    #       new_tab: true
    
---
Hi I'm Guanyu Xu, an undergraduate student pursuing dual degrees in Computer Engineering at the **University of Michigan** and Mechanical Engineering at **Shanghai Jiao Tong University**. Currently, I work as a research assistant at [Hybrid Dynamic Robotics Lab](https://soft.robotics.umich.edu/) directed by Prof. [Xiaonan Huang](https://scholar.google.com/citations?user=MNKU_WcAAAAJ&hl=en-US). 

My research interest primarily focuses on **embodied intelligence and robotics**. I am particularly interested in combining robotic foundation models with simulation-based RL to enable agile, generalizable robotic behaviors in the real world. My prior work is grounded in **full-stack robotic systems**, with expertise in mechanical design and smart manufacturing, embedded and real-time systems, and closed-loop sensorimotor control.

In addition to research, I maintain a **[portfolio]**({{ '/portfolio/' | relative_url }})of course projects that reflects hands-on experience. I also occasionaly update my learning notes in the **[blog]**({{ '/year-archive/' | relative_url }}). Feel free to check those if you are interested. 

## Research Projects
{% include project_list.html projects=page.projects.research kind="research" %}


## Selected Course Projects
{% include project_list.html projects=page.projects.course kind="course" %}