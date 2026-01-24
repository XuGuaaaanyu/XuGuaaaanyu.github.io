---
permalink: /
title: "Guanyu Xu 徐冠宇"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
projects:
  research:
    - title: "Optical Waveguide Sensor for 3D Shape Reconstruction"
      url: /research/optical-sensor/
      image: /images/optical_sensor/cover.png
      alt: "Optical Sensor teaser"
      authors: ["Guanyu Xu", "Jiaqi Wang", "Dezhong Tong", "Xiaonan Huang"]
      desc: "A soft, stretchable optical waveguide sensor with embedded LEDs and photodiodes for learning-based 3D deformation reconstruction."
      tags:
        - label: "Paper"
          href: /files/OpticalSensor/paper.pdf
          icon: "fas fa-file-pdf"
          new_tab: true
        - label: "Code"
          href: "https://github.com/GuanyuXu04/ShapeNet"
          icon: "fab fa-github"
          new_tab: true
        - label: "Video"
          href: "https://www.youtube.com/watch?v=SRcHd9E9L2w"
          icon: "fab fa-youtube"
          new_tab: true

  course:
    - title: "INSIGHT: Smart Assistive Glass"
      url: /portfolio/01.SmartGlass/
      image: /images/glass/teaser.png
      alt: "Smart Glass teaser"
      authors: ["Guanyu Xu", "Haobo Fang", "Ruopu Dong", "Yizhe Shen", "Zhuoyang Chen", "Jinlin Li"]
      desc: "In-device navigation and scene interpretation glasses for low-vision users."
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
    
---
I'm an undergraduate student pursuing dual degrees in Computer Engineering at the **University of Michigan** and Mechanical Engineering at **Shanghai Jiao Tong University**. Currently, I work as a research assistant at [Hybrid Dynamic Robotics Lab](https://soft.robotics.umich.edu/) directed by Prof. [Xiaonan Huang](https://scholar.google.com/citations?user=MNKU_WcAAAAJ&hl=zh-CN). 

My research is driven by a central question: How can we enable robots to perceive and interact with the physical world naturally and safely? I am particularly interested in Embodied AI, specifically at the intersection of **cyberphysical systems, soft robotics, and human-robot interaction**. My research focuses on bridging the gap between hardware fabrication and algorithm design by embedding 'physical intelligence' into compliant robotic systems.


## Research Projects
{% include project_list.html projects=page.projects.research %}


## Selected Course Projects
{% include project_list.html projects=page.projects.course %}