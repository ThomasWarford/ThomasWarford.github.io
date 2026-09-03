---
layout: page
title: Publications
permalink: /publications/
description: "Academic publications, preprints, and research papers by Thomas Warford on machine learning, atomistic simulation, and materials science."
---


<ul class="publication-list">
  {% for pub in site.data.publications %}
    <li class="publication-item" itemscope itemtype="https://schema.org/ScholarlyArticle">
      <div class="pub-title" itemprop="headline">
        {% if pub.doi %}
          <a href="{{ pub.doi }}" itemprop="url" target="_blank" rel="noopener noreferrer">
            {{ pub.title }}
          </a>
        {% elsif pub.scholar_url %}
          <a href="{{ pub.scholar_url }}" itemprop="url" target="_blank" rel="noopener noreferrer">
            {{ pub.title }}
          </a>
        {% else %}
          {{ pub.title }}
        {% endif %}
      </div>

      <div class="pub-authors" itemprop="author">
        {{ pub.authors | replace: "T Warford", "<strong>T Warford</strong>" | replace: "Thomas Warford", "<strong>Thomas Warford</strong>" }}
      </div>

      <div class="pub-venue">
        <span itemprop="isPartOf">{{ pub.venue }}</span>{% if pub.year %}, <span itemprop="datePublished">{{ pub.year }}</span>{% endif %}
      </div>

      <div class="pub-links">
        {% if pub.doi %}
          <a class="pub-btn" href="{{ pub.doi }}" target="_blank" rel="noopener noreferrer">DOI</a>
        {% endif %}
        {% if pub.scholar_url %}
          <a class="pub-btn pub-btn-secondary" href="{{ pub.scholar_url }}" target="_blank" rel="noopener noreferrer">Google Scholar</a>
        {% endif %}
        {% if pub.arxiv %}
          <a class="pub-btn" href="{{ pub.arxiv }}" target="_blank" rel="noopener noreferrer">arXiv</a>
        {% endif %}
        {% if pub.code %}
          <a class="pub-btn pub-btn-secondary" href="{{ pub.code }}" target="_blank" rel="noopener noreferrer">Code</a>
        {% endif %}
      </div>
    </li>
  {% endfor %}
<p class="publications-outro">
  A complete and up-to-date record is available on
  <a href="{{ site.scholar }}" target="_blank" rel="noopener noreferrer">Google Scholar</a> and
  <a href="https://orcid.org/{{ site.orcid }}" target="_blank" rel="noopener noreferrer">ORCID</a>.
</p>
</ul>
