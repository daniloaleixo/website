---
# Hidden page: reachable only via its URL (not in menus, lists, sitemap or search engines).
title: 'Batizado 2026 – Food & drinks'
url: /batizado-2026/essen-trinken/
type: landing
private: true # adds <meta name="robots" content="noindex">
build:
  list: never
sitemap:
  disable: true

sections:
  - block: sc_potluck
    content:
      kicker: Batizado 2026 · Buffet Sat 7 & Sun 8 Nov
      title: Food & drinks
      lead: "Our buffet is a potluck. **Check what others are already bringing**, then add yourself in the form – so we end up with a colourful mix instead of five pasta salads."
      sheet_id: 1XMLcRXgDNK8a6vF2Qsmymlv0WgUzsFCVdR68ISadg3o
      form_url: https://docs.google.com/forms/d/e/1FAIpQLSfccLk1HNv3dxROEtPH605x78L2SbzkmCmFY11i0no2mleOPA/viewform
      labels:
        jump: Add what you bring
        buffet: Who brings what
        orga: Helpers & supplies
        refresh: Refresh
        loading: Loading the list…
        empty: Nothing yet – be the first!
        error: The list couldn't be loaded. Open the sheet below instead.
        open: still open
        sheet: Open the full list (Google Sheet)
        form: Add yourself
        form_tab: Open the form in a new tab
      # key = option text exactly as in the Google Form, label = what we show here
      orga:
        - { key: 'Ich helfe beim Aufbau', label: 'Setup help (Sat 9:00)' }
        - { key: 'Ich helfe beim Abbau', label: 'Teardown help (Sun 15:00)' }
        - { key: 'Biertischgarnitur', label: 'Beer table set for the buffet' }
        - { key: 'Kaffee-Situation', label: 'Coffee (machine, coffee, etc.)' }
        - { key: 'Thermoskannen', label: 'Thermos flasks' }
        - { key: 'Ich bringe Getränke', label: 'Drinks' }
        - { key: 'Servietten', label: 'Napkins' }
        - { key: 'Becher', label: 'Cups' }
        - { key: 'Teller', label: 'Plates' }
        - { key: 'Besteck', label: 'Cutlery' }
        - { key: 'Kehrschaufel', label: 'Dustpan & broom' }
        - { key: 'Müllsäcke', label: 'Bin bags' }
        - { key: 'Lappen', label: 'Cloths for wiping' }
        - { key: 'Tischdecke', label: 'Tablecloth or similar' }
---
