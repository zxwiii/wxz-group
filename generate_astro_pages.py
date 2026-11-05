import os
import json

FANKE_DIR = r"E:\OneDrive - Jiangsu University\工作\5.实验室管理\网站\wxz-cloud\fanke"

def read_fanke_file(filename):
    path = os.path.join(FANKE_DIR, filename)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

fanke_home = read_fanke_file("王小治home.txt")
fanke_research = read_fanke_file("研究方向.txt")
fanke_publications = read_fanke_file("文章.txt")
fanke_patents = read_fanke_file("专利.txt")
fanke_joinus = read_fanke_file("诚邀英才.txt")
fanke_contact = read_fanke_file("联系我们.txt")

# 1. index.astro
index_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="主页" activeNav="home">
  <div class="home-hero-container" style="background: linear-gradient(135deg, #0f2c59 0%, #1e3a8a 100%); padding: 2.5rem 1rem 3.5rem;">
    <!-- 用户原版王小治home.txt (无损嵌入) -->
    {fanke_home}
  </div>
</Layout>
"""
with open("src/pages/index.astro", "w", encoding="utf-8") as f:
    f.write(index_astro)

# 2. research.astro
research_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="研究方向" activeNav="research">
  <!-- 用户原版研究方向.txt (无损嵌入) -->
  {fanke_research}
</Layout>
"""
with open("src/pages/research.astro", "w", encoding="utf-8") as f:
    f.write(research_astro)

# 3. publications.astro
publications_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="学术文章" activeNav="outputs">
  <div class="custom-embed-wrap" style="max-width: 1240px; margin: 1.5rem auto 3rem auto; padding: 0 1.5rem;">
    <!-- 用户原版文章.txt (无损嵌入) -->
    {fanke_publications}
  </div>
</Layout>
"""
with open("src/pages/publications.astro", "w", encoding="utf-8") as f:
    f.write(publications_astro)

# 4. patents.astro
patents_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="专利成果" activeNav="outputs">
  <div class="custom-embed-wrap" style="max-width: 1240px; margin: 1.5rem auto 3rem auto; padding: 0 1.5rem;">
    <!-- 用户原版专利.txt (无损嵌入) -->
    {fanke_patents}
  </div>
</Layout>
"""
with open("src/pages/patents.astro", "w", encoding="utf-8") as f:
    f.write(patents_astro)

# 5. joinus.astro
joinus_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="诚邀英才" activeNav="joinus">
  <!-- 用户原版诚邀英才.txt (无损嵌入) -->
  {fanke_joinus}
</Layout>
"""
with open("src/pages/joinus.astro", "w", encoding="utf-8") as f:
    f.write(joinus_astro)

# 6. contact.astro
contact_astro = f"""---
import Layout from '../layouts/Layout.astro';
---

<Layout title="联系我们" activeNav="contact">
  <!-- 用户原版联系我们.txt (无损嵌入) -->
  {fanke_contact}
</Layout>
"""
with open("src/pages/contact.astro", "w", encoding="utf-8") as f:
    f.write(contact_astro)

print("Generated core Astro pages (index, research, publications, patents, joinus, contact).")
