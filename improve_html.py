#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improve HTML structure by adding sections and IDs
"""

import re

# Read the generated HTML
with open('/home/user/LPT/article_full.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract the article content
content_match = re.search(r'<div class="article-content">(.*?)</div>\s*<button id="backToTop"', html, re.DOTALL)
if content_match:
    content = content_match.group(1)

    # Split into sections based on h1 and h2
    sections = []
    current_section = {'type': None, 'title': '', 'id': '', 'content': []}

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for headers
        h1_match = re.match(r'<h1>(.*?)</h1>', line)
        h2_match = re.match(r'<h2>(.*?)</h2>', line)

        if h1_match or h2_match:
            # Save previous section
            if current_section['content']:
                sections.append(current_section)

            # Start new section
            if h1_match:
                title = h1_match.group(1)
                section_id = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags
                section_id = re.sub(r'[^a-zA-Z0-9]+', '-', section_id).lower().strip('-')
                current_section = {
                    'type': 'h1',
                    'title': title,
                    'id': section_id,
                    'content': [line]
                }
            elif h2_match:
                title = h2_match.group(1)
                section_id = re.sub(r'<[^>]+>', '', title)
                section_id = re.sub(r'[^a-zA-Z0-9]+', '-', section_id).lower().strip('-')
                current_section = {
                    'type': 'h2',
                    'title': title,
                    'id': section_id,
                    'content': [line]
                }
        else:
            if line:
                current_section['content'].append(line)

        i += 1

    # Add last section
    if current_section['content']:
        sections.append(current_section)

    # Rebuild content with proper sections
    new_content = ''
    skip_first_h1 = True  # Skip the duplicate title
    for section in sections:
        if skip_first_h1 and section['type'] == 'h1' and 'LPT —' in section['title']:
            skip_first_h1 = False
            continue

        if section['type'] in ['h1', 'h2']:
            new_content += f'\n            <section id="{section["id"]}" class="section">\n'
            new_content += '                ' + '\n                '.join(section['content']) + '\n'
            new_content += '            </section>\n'

    # Replace in HTML
    new_html = re.sub(
        r'<div class="article-content">.*?</div>',
        new_content.strip(),
        html,
        flags=re.DOTALL
    )

    # Write improved HTML
    with open('/home/user/LPT/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

    print("✓ Improved HTML generated: index.html")
    print(f"✓ Created {len(sections)} sections")
else:
    print("ERROR: Could not find article content")
