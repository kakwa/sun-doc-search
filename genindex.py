import os
import json
import re
from bs4 import BeautifulSoup

# -----------------------
# CONFIG
# -----------------------
content_dir = "./"
output_file = "search-index.json"
snippet_length = 200           # max characters of page content
ignore_keyword = "component"   # skip files with this in the name
ignore_dirs = ["images", "SupportHeaders"]  # directories to skip

# -----------------------
# GLOBAL INDEX
# -----------------------
index = []

# -----------------------
# PROCESS A SINGLE FILE
# -----------------------
def process_file(filepath, count, total):
    # Skip files containing the ignore keyword
    if ignore_keyword.lower() in os.path.basename(filepath).lower():
        print(f"[{count}/{total}] Skipped (component): {filepath}")
        return

    # Skip files in ignored directories
    for d in ignore_dirs:
        if f"{os.sep}{d}{os.sep}" in filepath or filepath.lower().startswith(d.lower() + os.sep):
            print(f"[{count}/{total}] Skipped ({d} dir): {filepath}")
            return

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")

            # Extract and clean title
            title = soup.title.string.strip() if (soup.title and soup.title.string) else os.path.basename(filepath)

            # Boilerplate strings to remove from title/snippets
            boilerplate_strings = [
                "Oracle System Handbook - ISO 7.0 May 2018 Internal/Partner Edition Home",
                "Oracle System Handbook - ISO 7.0 May 2018 Internal/Partner Edition",
                "Home |",
            ]

            for bp in boilerplate_strings:
                if title:
                    title = title.replace(bp, "").strip()

            # Extract text AFTER the first <h1>, then normalize and clean
            if soup.body:
                first_h1 = soup.body.find("h1")
            else:
                first_h1 = None

            if first_h1 is not None:
                texts_after_h1 = []
                for s in first_h1.find_all_next(string=True):
                    parent_name = getattr(s.parent, "name", None)
                    if parent_name in ("script", "style"):
                        continue
                    stripped = s.strip()
                    if stripped:
                        texts_after_h1.append(stripped)
                raw_body_text = " ".join(texts_after_h1)
            else:
                raw_body_text = soup.body.get_text(" ", strip=True) if soup.body else ""
            normalized_text = " ".join(raw_body_text.split())  # collapse all whitespace

            # Remove known boilerplate occurrences
            for bp in boilerplate_strings:
                normalized_text = normalized_text.replace(bp, " ").strip()

            # Avoid repeating the title inside the content (loose match, case-insensitive, ignore punctuation/spaces)
            if title:
                title_words = re.findall(r"[A-Za-z0-9]+", title)
                if title_words:
                    # Allow any non-alphanumeric characters between title words (parentheses, punctuation, spaces, etc.)
                    sep_pattern = r"[^A-Za-z0-9]+"
                    pattern = r"\b" + sep_pattern.join(map(re.escape, title_words)) + r"\b"
                    normalized_text = re.sub(pattern, "", normalized_text, count=1, flags=re.IGNORECASE).strip(" -–|,:/")

            # Remove metadata like: "Last Modified Date 1380443.1" (case-insensitive, punctuation tolerant)
            normalized_text = re.sub(
                r"\bLast\s+Modified\s+Date\b(?:[:\s\-]*\d+(?:\.\d+)?)?",
                "",
                normalized_text,
                flags=re.IGNORECASE,
            ).strip()

            # Remove banner/footer markers and divider sequences
            normalized_text = re.sub(r"={3,}|-{3,}|_{3,}|\*{3,}", " ", normalized_text)
            normalized_text = re.sub(
                r"\b(END\s+OF\s+MAIN\s+CONTENT|PAGE\s+FOOTER|PAGE\s+HEADER|TABLE\s+BEG(?:IN(?:NING)?)?)\b",
                "",
                normalized_text,
                flags=re.IGNORECASE,
            ).strip()

            # Remove top navigation boilerplate phrase from content
            nav_boilerplate = (
                "Current Systems | Former STK Products | EOL Systems | Components | General Info | Search | Feedback"
            )
            if nav_boilerplate in normalized_text:
                normalized_text = normalized_text.replace(nav_boilerplate, " ").strip()

            # Remove unwanted keyword boilerplate phrases
            remove_token_patterns = [
                r"\bKeywords\s*:\s*",
                r"\bSolution\s+Type\b",
                r"\bProblem\s+Resolution\b",
                r"\bSure\s+Solution\b",
            ]
            for token_pat in remove_token_patterns:
                normalized_text = re.sub(token_pat, " ", normalized_text, flags=re.IGNORECASE)

            # Final collapse of whitespace and trim to snippet length
            body_text = " ".join(normalized_text.split())[:snippet_length]

            # Create relative URL
            rel_path = os.path.relpath(filepath, content_dir)
            url = rel_path.replace("index.html", "").replace("\\", "/")  # cross-platform

            index.append({
                "id": rel_path,
                "title": title,
                "content": body_text,
                "url": url
            })

            #print(f"content: {soup}")
            print(f"title: {title}")
            print(f"content: {body_text}")
            print(f"[{count}/{total}] Processed: {rel_path}")
    except Exception as e:
        print(f"⚠️  Failed to process {filepath}: {e}")

# -----------------------
# GET ALL HTML FILES
# -----------------------
def get_all_html_files(dir_path):
    files_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".html"):
                files_list.append(os.path.join(root, file))
    return files_list

# -----------------------
# MAIN SCRIPT
# -----------------------
if __name__ == "__main__":
    html_files = get_all_html_files(content_dir)
    total_files = len(html_files)

    print(f"Found {total_files} HTML files. Generating index...\n")

    for count, filepath in enumerate(html_files, start=1):
        process_file(filepath, count, total_files)

    # Write compact JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, separators=(",", ":"), ensure_ascii=False)

    print(f"\n✅ {output_file} generated with {len(index)} pages!")

