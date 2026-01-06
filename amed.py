import os
import random
import string
import re
import time
from datetime import datetime, timedelta

# ==============================================================================
# GENERATOR PRO - CLEAN SLUG & SMART FOLDER MANAGEMENT
# - روابط نظيفة تماماً بدون أرقام عشوائية في النهاية
# - إدارة المجلدات: الامتلاء حتى 500 ملف قبل فتح مجلد جديد
# - توليد لغوي منفصل (عربي/إنجليزي) مع تحديث التاريخ لحظياً
# ==============================================================================

class ContinuousGenerator:
    def __init__(self, template_file="test.html"):
        self.template_file = template_file
        self.keywords_ar = []
        self.keywords_en = []
        self.template_content = ""
        self.max_files_per_folder = 500
        
        self.emojis = ["🔥", "🎥", "🔞", "😱", "✅", "🌟", "📺", "🎬", "✨", "💎", "⚡"]
        
        self.load_template()
        self.load_keywords()

    def load_template(self):
        """تحميل محتوى ملف القالب test.html"""
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, "r", encoding="utf-8") as f:
                    self.template_content = f.read()
            except Exception as e:
                print(f"[!] Error reading template: {e}")
        else:
            self.template_content = "<html><head><title>{{TITLE}}</title></head><body>{{DESCRIPTION}}<br>Date: {{DATE}}<br>{{INTERNAL_LINKS}}</body></html>"

    def load_keywords(self):
        """تحميل الكلمات وتصنيفها حسب اللغة"""
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
        """بناء نص بلغة واحدة محددة"""
        target_length = random.randint(min_words, max_words)
        source = self.keywords_ar if mode == "ar" else self.keywords_en
        if not source: source = ["Keyword", "Trending", "Video"]
        words = []
        while len(words) < target_length:
            chunk = random.choice(source).split()
            words.extend(chunk)
        return " ".join(words[:target_length])

    def get_target_path(self):
        """البحث عن آخر مجلد متاح أو إنشاء مجلد جديد"""
        folder_bases = ["video", "new", "raw", "viral", "clips", "watch", "hot"]
        
        for base in folder_bases:
            if os.path.exists(base):
                subfolders = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
                if subfolders:
                    subfolders.sort(key=os.path.getctime, reverse=True)
                    latest_sub = subfolders[0]
                    file_count = len([f for f in os.listdir(latest_sub) if f.endswith('.html')])
                    if file_count < self.max_files_per_folder:
                        return latest_sub

        main_folder_name = random.choice(folder_bases)
        sub_folder_name = ''.join(random.choices(string.ascii_lowercase, k=3))
        full_path = os.path.join(main_folder_name, sub_folder_name)
        os.makedirs(full_path, exist_ok=True)
        return full_path

    def run_single_cycle(self, count=50):
        """تشغيل دورة توليد: روابط نظيفة بدون أرقام عشوائية"""
        full_path = self.get_target_path()
        current_files_in_folder = len([f for f in os.listdir(full_path) if f.endswith('.html')])
        
        print(f"[*] Target folder: {full_path} (Contains: {current_files_in_folder} files)")
        
        generated_files = []
        half = count // 2
        modes = (["ar"] * half) + (["en"] * (count - half))
        random.shuffle(modes)

        base_time = datetime.utcnow()

        for i in range(count):
            current_mode = modes[i]
            file_time = base_time - timedelta(seconds=random.randint(0, 3600), microseconds=random.randint(0, 999999))
            
            formatted_date_iso = file_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            formatted_date_sql = file_time.strftime("%Y-%m-%d %H:%M:%S")
            
            title_len = random.choice([5, 7, 9, 11])
            raw_title = self.build_text(title_len, title_len + 2, mode=current_mode)
            display_title = f"{random.choice(self.emojis)} {raw_title} {random.choice(self.emojis)}"
            
            # تحويل العنوان إلى رابط نظيف (Slug)
            clean_name = re.sub(r'[^\w\s-]', '', raw_title.lower())
            slug = re.sub(r'[-\s]+', '-', clean_name).strip('-')[:80]
            
            # اسم الملف بدون أرقام عشوائية
            filename = f"{slug}.html"
            
            generated_files.append({
                "display_title": display_title,
                "filename": filename,
                "desc": self.build_text(120, 350, mode=current_mode),
                "keys": self.build_text(3, 8, mode=current_mode),
                "mode": current_mode,
                "date_iso": formatted_date_iso,
                "date_sql": formatted_date_sql
            })

        for i, file_data in enumerate(generated_files):
            content = self.template_content
            
            # روابط داخلية
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
            
            # استبدال أي تواريخ ثابتة أو صيغ زمنية
            content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', file_data['date_iso'], content)
            content = re.sub(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', file_data['date_sql'], content)

            if "{{INTERNAL_LINKS}}" in content:
                content = content.replace("{{INTERNAL_LINKS}}", links_html)
            else:
                content += f"\n{links_html}"

            try:
                file_path = os.path.join(full_path, file_data['filename'])
                # فحص بسيط: إذا كان الملف موجوداً مسبقاً، لا نقوم بالكتابة فوقه لتجنب التكرار
                # أو يمكنك إضافة حرف عشوائي "فقط" في حالة التصادم (Conflict)
                if os.path.exists(file_path):
                    # إذا حدث تصادم نادر جداً، نضيف حرف واحد فقط للتمييز
                    file_path = file_path.replace(".html", f"-{random.choice(string.ascii_lowercase)}.html")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except:
                pass
        
        print(f"✅ Created {count} clean files in {full_path}.")

if __name__ == "__main__":
    bot = ContinuousGenerator()
    bot.run_single_cycle(count=50)