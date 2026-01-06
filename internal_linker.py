import os
import random
from bs4 import BeautifulSoup

# =========================
# SMART INTERNAL LINKER
# - يربط كل الصفحات ببعضها تلقائياً
# - يعمل على آلاف الملفات ومئات المجلدات
# - Google-Bot Friendly (سياق + Anchor طبيعي)
# =========================

ROOT_DIR = "."          # جذر الموقع
LINKS_PER_PAGE = 5       # عدد الروابط الداخلية لكل صفحة
BLOCK_CLASS = "internal-links"  # كلاس البلوك


def collect_html_files(root):
    pages = []
    for r, d, f in os.walk(root):
        for file in f:
            if file.endswith(".html"):
                full = os.path.join(r, file)
                pages.append(full)
    return pages


def relative_path(src, dst):
    return os.path.relpath(dst, os.path.dirname(src)).replace("\\", "/")


def extract_title(soup):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.text.strip() if h1 else "مقالة ذات صلة"


def build_links(current, all_pages):
    candidates = [p for p in all_pages if p != current]
    random.shuffle(candidates)
    return candidates[:LINKS_PER_PAGE]


def inject_links(file_path, all_pages):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        body = soup.body
        if not body:
            return

        # حذف بلوك قديم لو موجود (إعادة بناء نظيفة)
        old = soup.find("div", {"class": BLOCK_CLASS})
        if old:
            old.decompose()

        related = build_links(file_path, all_pages)
        if not related:
            return

        block = soup.new_tag("div")
        block["class"] = BLOCK_CLASS

        p = soup.new_tag("p")
        p.string = "مقالات قد تهمك أيضاً:"
        block.append(p)

        ul = soup.new_tag("ul")
        for target in related:
            with open(target, "r", encoding="utf-8") as tf:
                tsoup = BeautifulSoup(tf.read(), "html.parser")
            title = extract_title(tsoup)
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=relative_path(file_path, target))
            a.string = title
            li.append(a)
            ul.append(li)

        block.append(ul)
        body.append(block)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    except Exception as e:
        print(f"[!] skipped {file_path}: {e}")


def main():
    pages = collect_html_files(ROOT_DIR)
    print(f"[*] Found {len(pages)} HTML pages")

    for i, page in enumerate(pages, 1):
        inject_links(page, pages)
        if i % 100 == 0:
            print(f"  linked {i} pages")

    print("✅ Internal linking completed successfully")


if __name__ == "__main__":
    main()
