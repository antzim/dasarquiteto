import os, hashlib, json, re

# Load cleaned images map
with open('project_images_map.json', encoding='utf-8') as f:
    raw_img_map = json.load(f)

# Filter logo hashes
logo_hashes = set()
out_dir = 'das_portfolio_images'
for fname in os.listdir(out_dir):
    fpath = os.path.join(out_dir, fname)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        with open(fpath, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()
        if size < 25000:
            logo_hashes.add(h)

hash_counts = {}
for fname in os.listdir(out_dir):
    fpath = os.path.join(out_dir, fname)
    if os.path.isfile(fpath):
        with open(fpath, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()
        hash_counts.setdefault(h, []).append(fname)

for h, files in hash_counts.items():
    if len(files) >= 3:
        logo_hashes.add(h)

cleaned_map = {}
for proj, files in raw_img_map.items():
    real_imgs = []
    for fpath in files:
        fname = os.path.basename(fpath)
        full_p = os.path.join(out_dir, fname)
        if not os.path.exists(full_p):
            continue
        with open(full_p, 'rb') as f:
            h = hashlib.md5(f.read()).hexdigest()
        if h not in logo_hashes and 'logo' not in fname.lower():
            real_imgs.append(fpath)
    
    seen = set()
    unique_imgs = []
    for img in real_imgs:
        if img not in seen:
            seen.add(img)
            unique_imgs.append(img)
    cleaned_map[proj] = unique_imgs[:4]

with open('index_06.html', encoding='utf-8') as f:
    content = f.read()

# Replace banner link to portfolio_02.html
content = content.replace('href="portfolio.html"', 'href="portfolio_02.html"')

# Add CSS for .pc-timer-bar and compact banner
css_to_add = """
    /* 15s TIMED PROGRESS BAR AT TOP OF CARD */
    .pc-timer-bar {
      position: absolute;
      top: 0;
      left: 0;
      width: 0%;
      height: 3px;
      background: linear-gradient(90deg, #FFFFFF, rgba(255,255,255,0.7));
      box-shadow: 0 0 8px rgba(255,255,255,0.8);
      z-index: 20;
      pointer-events: none;
      transition: width 0s linear;
    }
    .pc.timer-active .pc-timer-bar {
      width: 100%;
      transition: width 15s linear;
    }
    .pc-timer-status {
      display: inline-block;
      font-size: 0.62rem;
      opacity: 0.6;
      transition: opacity 0.3s, transform 0.3s;
    }
    .pc.timer-active .pc-timer-status {
      opacity: 1;
      animation: pulseTimer 1.5s infinite ease-in-out;
    }
    @keyframes pulseTimer {
      0%, 100% { transform: scale(1); opacity: 0.7; }
      50% { transform: scale(1.25); opacity: 1; }
    }
"""

content = content.replace('/* Image counter badge */', css_to_add + '\n    /* Image counter badge */')

# Make full-portfolio-cta-banner compact and discrete
content = content.replace('margin-top: var(--sp-32);\n      padding: var(--sp-24) var(--sp-20);', 'margin-top: var(--sp-16);\n      padding: var(--sp-8) var(--sp-16);')
content = content.replace('font-size: clamp(1.4rem, 2.4vw, 2.1rem);', 'font-size: clamp(1.05rem, 1.6vw, 1.3rem);')
content = content.replace('font-size: 0.9rem;', 'font-size: 0.8rem;')

# Helper to build cards HTML
def make_card(name, grid_class, cat_pt, cat_en, meta_html, data_c):
    imgs = cleaned_map.get(name, [])
    slides = []
    dots = []
    for idx, img_src in enumerate(imgs):
        active_cls = 'active' if idx == 0 else ''
        slides.append(f'<div class="pc-slide {active_cls}"><img src="{img_src}" alt="{name} - {idx+1}" loading="lazy"/></div>')
        dot_on = 'on' if idx == 0 else ''
        dots.append(f'<div class="pc-dot {dot_on}" data-idx="{idx}"></div>')
    
    slides_str = '\n          '.join(slides)
    dots_str = '\n          '.join(dots)
    total = len(imgs)
    counter_str = f'<div class="pc-img-counter"><span class="pc-timer-status">⏱️</span> 01 / {total:02d}</div>' if total > 1 else ''
    dots_wrap = f'<div class="pc-dots">\n          {dots_str}\n        </div>' if total > 1 else ''

    return f'''      <!-- {name.upper()} -->
      <div class="pc {grid_class}" data-c="{data_c}">
        <div class="pc-timer-bar"></div>
        <div class="pc-thumb">
          {slides_str}
        </div>
        {counter_str}
        {dots_wrap}
        <div class="pc-overlay"></div>
        <div class="pc-info">
          <span class="pc-cat"><span class="lang-pt">{cat_pt}</span><span class="lang-en">{cat_en}</span></span>
          <h3 class="pc-name">{name}</h3>
          <p class="pc-meta">{meta_html}</p>
        </div>
      </div>'''

# Build new projects grid
cards_code = [
    make_card('Arena BSB', 'pc-8', 'Esporte & Lazer', 'Sports & Leisure', '90,000m² · <span class="lang-pt">Concurso Nacional - 2º Lugar</span><span class="lang-en">National Competition - 2nd Place</span>', 'institucional'),
    make_card('Monte Alegre Residence', 'pc-4', 'Interiores & Residencial', 'Interiors & Residential', '620m² · Executive Project', 'residencial'),
    make_card('Manaca Residence', 'pc-5', 'Residencial Sustentável', 'Sustainable Residential', '1,350m² · <span class="lang-pt">Prêmio Saint Gobain</span><span class="lang-en">Saint Gobain Award</span>', 'residencial'),
    make_card('Sambaqui Sunset Residence', 'pc-7', 'Habitação', 'Housing', '26,000m² · Preliminary Design', 'residencial'),
    make_card('Vilnius Concert Hall', 'pc-6', 'Cultural Internacional', 'International Cultural', '12,000m² · Lithuania', 'cultural'),
    make_card('Ceara Building', 'pc-6', 'Edifício Residencial/Misto', 'Residential/Mixed Building', '4,449m²', 'institucional')
]

new_pg_content = '<div class="pg rv">\n\n' + '\n\n'.join(cards_code) + '\n    </div>'

# Clean pattern replacement
pattern = r'<div class="pg rv">.*?<!-- BANNER CTA ALL PROJECTS -->'
content = re.sub(pattern, new_pg_content + '\n\n    <!-- BANNER CTA ALL PROJECTS -->', content, flags=re.DOTALL)

# Compact button style in banner
content = content.replace('style="padding:14px 28px; white-space:nowrap; flex-shrink:0;"', 'style="padding:9px 20px; font-size:0.72rem; white-space:nowrap; flex-shrink:0;"')

# Replace JS slideshow block with 15s timer JS
new_js = """/* ---- 15s TIMED SLIDESHOW WITH VISUAL PROGRESS BAR INDICATOR ---- */
(function() {
  document.querySelectorAll('.pc').forEach(card => {
    const slides = card.querySelectorAll('.pc-slide');
    if (slides.length <= 1) return;

    const counter = card.querySelector('.pc-img-counter');
    const dots = card.querySelectorAll('.pc-dot');
    let current = 0;
    let timer = null;
    const total = slides.length;

    function resetProgressBar() {
      card.classList.remove('timer-active');
      void card.offsetWidth;
    }

    function triggerProgressBar() {
      resetProgressBar();
      card.classList.add('timer-active');
    }

    function goTo(idx) {
      slides[current].classList.remove('active');
      if (dots[current]) dots[current].classList.remove('on');
      
      current = (idx + total) % total;
      
      slides[current].classList.add('active');
      if (dots[current]) dots[current].classList.add('on');
      if (counter) {
        counter.innerHTML = `<span class="pc-timer-status">⏱️</span> ${String(current + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}`;
      }
      triggerProgressBar();
    }

    function start15sTimer() {
      if (timer) return;
      triggerProgressBar();
      timer = setInterval(() => {
        goTo(current + 1);
      }, 15000);
    }

    function stop15sTimer() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      resetProgressBar();
    }

    // Start 15s timer & progress bar ONLY on mouseenter or click
    card.addEventListener('mouseenter', start15sTimer);
    card.addEventListener('mouseleave', stop15sTimer);

    card.addEventListener('click', (e) => {
      start15sTimer();
    });

    dots.forEach(dot => {
      dot.addEventListener('click', (e) => {
        e.stopPropagation();
        const targetIdx = parseInt(dot.dataset.idx, 10);
        goTo(targetIdx);
        stop15sTimer();
        start15sTimer();
      });
    });
  });

  /* ---- SUBTLE 3D PARALLAX TILT ON HOVER (MINIMAL & SILKY) ---- */
  document.querySelectorAll('.pc').forEach(card => {
    const thumb = card.querySelector('.pc-thumb');
    if (!thumb) return;

    let rafId = null;

    card.addEventListener('mousemove', (e) => {
      if (card.classList.contains('expanded')) return;
      if (rafId) cancelAnimationFrame(rafId);
      
      rafId = requestAnimationFrame(() => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        const tiltX = (y / rect.height) * -2.5;
        const tiltY = (x / rect.width) * 2.5;
        
        card.style.transform = `perspective(1400px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.008, 1.008, 1.008)`;
        card.style.zIndex = '5';
      });
    });

    card.addEventListener('mouseleave', () => {
      if (card.classList.contains('expanded')) return;
      if (rafId) cancelAnimationFrame(rafId);
      card.style.transform = 'perspective(1400px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      card.style.boxShadow = '';
      card.style.zIndex = '';
    });
  });
})();"""

js_pattern = r'/\* ---- HOVER SLIDESHOW ANIMATION FOR PROJECT CARDS ---- \*/.*?</script>'
content = re.sub(js_pattern, new_js + '\n</script>', content, flags=re.DOTALL)

with open('index_07.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Regenerated index_07.html cleanly without duplicate fragments!')
