import os
import random
import string
import re
from datetime import datetime, timedelta 

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
        """إنشاء مجلدات تعتمد على التاريخ الحالي"""
        # استخدام تاريخ اليوم كمجلد رئيسي
        today_folder = datetime.now().strftime("%Y-%m-%d")
        base_root = today_folder 
        
        paths = []
        num_folders = (total_count // self.max_files_per_folder) + 1
        
        for i in range(num_folders):
            # مجلد فرعي داخل مجلد اليوم (مثال: 2026-01-08/part-1)
            sub_folder = f"part-{i+1}"
            full_path = os.path.join(base_root, sub_folder)
            os.makedirs(full_path, exist_ok=True)
            paths.append(full_path)
            
        return paths

    def run_single_cycle(self, count=500):
        folder_paths = self.get_target_path(count)
        print(f"[*] Target folders: {folder_paths}")

        generated_files = []
        half = count // 2
        modes = (['ar'] * half) + (['en'] * (count - half))
        random.shuffle(modes)

        base_time = datetime.utcnow()

        file_index = 0
        # توزيع الملفات على المجلدات المجهزة
        for folder in folder_paths:
            current_chunk = min(count - file_index, self.max_files_per_folder)
            for i in range(current_chunk):
                current_mode = modes[file_index]
                file_time = base_time - timedelta(seconds=random.randint(0, 3600))

                formatted_date_iso = file_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                formatted_date_sql = file_time.strftime("%Y-%m-%d %H:%M:%S")

                title_len = random.choice([5, 7, 9])
                raw_title = self.build_text(title_len, title_len + 2, mode=current_mode)
                display_title = f"{random.choice(self.emojis)} {raw_title} {random.choice(self.emojis)}"

                clean_name = re.sub(r'[^\w\s-]', '', raw_title.lower())
                slug = re.sub(r'[-\s]+', '-', clean_name).strip('-')[:80]
                filename = f"{slug}.html"

                generated_files.append({
                    "display_title": display_title,
                    "filename": filename,
                    "desc": self.build_text(120, 250, mode=current_mode), # تقليل الحجم قليلاً للمساحة
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

            # روابط داخلية ذكية من نفس المجلد أو اللغة
            other_files = [f for j, f in enumerate(generated_files) if i != j]
            links_sample = random.sample(other_files, min(len(other_files), random.randint(3, 5)))

            links_html = "<div class='internal-links'><ul>"
            for link in links_sample:
                # إنشاء رابط نسبي صحيح (المجلدات أصبحت متوازية الآن)
                rel_path = f"../{os.path.basename(link['folder'])}/{link['filename']}"
                links_html += f"<li><a href='{rel_path}'>{link['display_title']}</a></li>"
            links_html += "</ul></div>"

            content = content.replace("{{TITLE}}", file_data['display_title'])
            content = content.replace("{{DESCRIPTION}}", file_data['desc'])
            content = content.replace("{{KEYWORDS}}", file_data['keys'])
            content = content.replace("{{DATE}}", file_data['date_iso'])
            content = content.replace("{{DATE_SQL}}", file_data['date_sql'])
            
            if "{{INTERNAL_LINKS}}" in content:
                content = content.replace("{{INTERNAL_LINKS}}", links_html)
            else:
                content += f"\n{links_html}"

            try:
                file_path = os.path.join(file_data['folder'], file_data['filename'])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[!] Failed to write file: {e}")
        
        print(f"✅ Created {file_index} clean files in date-based folders.")

if __name__ == "__main__":
    bot = ContinuousGenerator()
    # تشغيل 300 ملف في كل دورة لتجنب مشاكل المساحة مستقبلاً
    bot.run_single_cycle(count=300)
