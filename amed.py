import os
import random
import string
import re
from datetime import datetime, timedelta

# ==============================================================================
# GENERATOR PRO - CLEAN SLUG & SMART FOLDER MANAGEMENT
# - روابط نظيفة تماماً بدون أرقام عشوائية في النهاية
# - إدارة المجلدات: الحد 500 ملف لكل مجلد فرعي
# - إنشاء مجلدين متداخلين لكل مجموعة ملفات
# - توليد لغوي منفصل (عربي/إنجليزي) مع تحديث التاريخ لحظياً
# ==============================================================================

class ContinuousGenerator:
    def __init__(self, template_file="test.html"):
        self.template_file = template_file
        self.keywords_ar = []
        self.keywords_en = []
        self.template_content = ""
        self.max_files_per_folder = 500  # الحد الأقصى لكل مجلد فرعي
        
        self.emojis = ["🔥", "🎥", "🔞", "😱", "✅", "🌟", "📺", "🎬", "✨", "💎", "⚡"]
        
        self.load_template()
        self.load_keywords()

    def load_template(self):
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, "r", encoding="utf-8") as f:
                    self.template_content = f.read()
            except Exception as e:
                print(f"[!] Error reading template: {e}")
        else:
            self.template_content = "<html><head><title>{{TITLE}}</title></head><body>{{DESCRIPTION}}<br>Date: {{DATE}}<br>{{INTERNAL_LINKS}}</body></html>"

    def load_keywords(self):
        ar_files = ["full_keywords_ar.txt", "triplets_ar.txt", "keywords_ar.txt"]
        en_files = ["full_keywords_en.txt", "triplets_en.txt", "keywords_en.txt"]
        
        for file in ar_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    self.keywords_ar.extend([l.strip() for l in f if l.strip()])
                    
        for file in en_files:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    self.keywords_en.extend([l.strip() for l in f if l.strip()])
        
        print(f"[*] Loaded {len(self.keywords_ar)} Arabic and {len(self.keywords_en)} English keywords.")

    def build_text(self, min_words, max_words, mode="ar"):
        target_length = random.randint(min_words, max_words)
        source = self.keywords_ar if mode == "ar" else self.keywords_en
        if not source: source = ["Keyword", "Trending", "Video"]
        words = []
        while len(words) < target_length:
            chunk = random.choice(source).split()
            words.extend(chunk)
        return " ".join(words[:target_length])

    def get_target_path(self, total_count):
        """إنشاء مجلدين متداخلين عشوائياً لكل 500 ملف تقريباً"""
        base_root = "."
        files_remaining = total_count
        paths = []

        while files_remaining > 0:
            # إنشاء مجلدين متداخلين
            first_folder = ''.join(random.choices(string.ascii_lowercase, k=3))
            second_folder = ''.join(random.choices(string.ascii_lowercase, k=3))
            full_path = os.path.join(base_root, first_folder, second_folder)
            os.makedirs(full_path, exist_ok=True)

            paths.append(full_path)
            # نحسب كم ملف يمكن وضعه هنا
            chunk = min(files_remaining, self.max_files_per_folder)
            files_remaining -= chunk

        return paths  # قائمة بكل المسارات المتاحة

    def run_single_cycle(self, count=1500):
        folder_paths = self.get_target_path(count)
        print(f"[*] Target folders: {folder_paths}")

        generated_files = []
        half = count // 2
        modes = (['ar'] * half) + (['en'] * (count - half))
        random.shuffle(modes)

        base_time = datetime.utcnow()

        # توليد الملفات
        file_index = 0
        for folder in folder_paths:
            current_chunk = min(len(modes) - file_index, self.max_files_per_folder)
            for i in range(current_chunk):
                current_mode = modes[file_index]
                file_time = base_time - timedelta(seconds=random.randint(0, 3600), microseconds=random.randint(0, 999999))

                formatted_date_iso = file_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                formatted_date_sql = file_time.strftime("%Y-%m-%d %H:%M:%S")

                title_len = random.choice([5, 7, 9, 11])
                raw_title = self.build_text(title_len, title_len + 2, mode=current_mode)
                display_title = f"{random.choice(self.emojis)} {raw_title} {random.choice(self.emojis)}"

                clean_name = re.sub(r'[^\w\s-]', '', raw_title.lower())
                slug = re.sub(r'[-\s]+', '-', clean_name).strip('-')[:80]
                filename = f"{slug}.html"

                generated_files.append({
                    "display_title": display_title,
                    "filename": filename,
                    "desc": self.build_text(120, 350, mode=current_mode),
                    "keys": self.build_text(3, 8, mode=current_mode),
                    "mode": current_mode,
                    "date_iso": formatted_date_iso,
                    "date_sql": formatted_date_sql,
                    "folder": folder
                })

                file_index += 1

        # كتابة الملفات
        for i, file_data in enumerate(generated_files):
            content = self.template_content

            other_files = [f for j, f in enumerate(generated_files) if i != j]
            same_lang_files = [f for f in other_files if f['mode'] == file_data['mode']]
            source_for_links = same_lang_files if len(same_lang_files) >= 3 else other_files
            links_sample = random.sample(source_for_links, min(len(source_for_links), random.randint(3, 6)))

            links_html = "<div class='internal-links'><ul>"
            for link in links_sample:
                links_html += f"<li><a href='{link['filename']}'>{link['display_title']}</a></li>"
            links_html += "</ul></div>"

            content = content.replace("{{TITLE}}", file_data['display_title'])
            content = content.replace("{{DESCRIPTION}}", file_data['desc'])
            content = content.replace("{{KEYWORDS}}", file_data['keys'])
            content = content.replace("{{DATE}}", file_data['date_iso'])
            content = content.replace("{{DATE_SQL}}", file_data['date_sql'])

            content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', file_data['date_iso'], content)
            content = re.sub(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', file_data['date_sql'], content)

            if "{{INTERNAL_LINKS}}" in content:
                content = content.replace("{{INTERNAL_LINKS}}", links_html)
            else:
                content += f"\n{links_html}"

            try:
                file_path = os.path.join(file_data['folder'], file_data['filename'])
                if os.path.exists(file_path):
                    file_path = file_path.replace(".html", f"-{random.choice(string.ascii_lowercase)}.html")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[!] Failed to write file: {e}")
        
        print(f"✅ Created {count} clean files across {len(folder_paths)} folder(s).")


if __name__ == "__main__":
    bot = ContinuousGenerator()
    bot.run_single_cycle(count=1000)
