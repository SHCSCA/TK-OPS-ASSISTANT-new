import os
import re

TARGET_FILES = [
    "desktop_app/ui/pages/content/visual_editor_page.py",
    "desktop_app/ui/pages/content/material_factory_page.py",
    "desktop_app/ui/pages/content/material_center_page.py",
    "desktop_app/ui/pages/content/video_editing_page.py",
    "desktop_app/ui/pages/content/task_hall_page.py",
    "desktop_app/ui/pages/automation/auto_reply_page.py",
    "desktop_app/ui/pages/automation/scheduled_publish_page.py",
    "desktop_app/ui/pages/automation/data_collection_page.py",
    "desktop_app/ui/pages/automation/auto_like_page.py",
    "desktop_app/ui/pages/automation/auto_comment_page.py",
    "desktop_app/ui/pages/automation/auto_direct_message_page.py",
]

def process_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, does not exist.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Reduce excessive spacing and margins
    content = content.replace("SPACING_2XL", "SPACING_XL")
    content = content.replace("SPACING_XL", "SPACING_LG")
    content = content.replace("SPACING_LG", "SPACING_MD")
    
    # Also for literal margins where setContentsMargins(20, 20, 20, 20) or setSpacing(20) is used
    content = re.sub(r'setContentsMargins\(20,\s*20,\s*20,\s*20\)', 'setContentsMargins(12, 12, 12, 12)', content)
    content = re.sub(r'setContentsMargins\(16,\s*16,\s*16,\s*16\)', 'setContentsMargins(12, 12, 12, 12)', content)
    content = re.sub(r'setSpacing\(16\)', 'setSpacing(12)', content)
    content = re.sub(r'setSpacing\(20\)', 'setSpacing(12)', content)
    content = re.sub(r'setSpacing\(18\)', 'setSpacing(12)', content)
    
    content = re.sub(r'setContentsMargins\(24,\s*24,\s*24,\s*24\)', 'setContentsMargins(16, 16, 16, 16)', content)
    content = re.sub(r'setSpacing\(24\)', 'setSpacing(16)', content)

    # 2. Improve SplitPanel ratios for a tighter sidebar and more main area
    content = re.sub(r'split_ratio=\(0\.28,\s*0\.72\)', 'split_ratio=(0.20, 0.80)', content)
    content = re.sub(r'split_ratio=\(0\.25,\s*0\.75\)', 'split_ratio=(0.20, 0.80)', content)
    content = re.sub(r'split_ratio=\(0\.30,\s*0\.70\)', 'split_ratio=(0.20, 0.80)', content)
    content = re.sub(r'split_ratio=\(0\.23,\s*0\.77\)', 'split_ratio=(0.20, 0.80)', content)
    content = re.sub(r'split_ratio=\(0\.73,\s*0\.27\)', 'split_ratio=(0.75, 0.25)', content)
    content = re.sub(r'split_ratio=\(0\.55,\s*0\.45\)', 'split_ratio=(0.60, 0.40)', content)

    # 3. Increase PageContainer max_width for better desktop usage (if limited)
    content = re.sub(r'max_width=1200', 'max_width=1600', content)
    content = re.sub(r'max_width=1400', 'max_width=1600', content)
    
    # 4. Enhance Toolbars
    # Replace some basic buttons in clear toolbars with Primary/Ghost buttons if possible, or just standard density
    # Not changing interactions, just changing layout spacing.

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Processed {filepath}")

for f in TARGET_FILES:
    process_file(f)
