#!/usr/bin/env python3
# bible_downloader.py

import os
from bible_parser import fetch_html, parse_chapter, DEFAULT_VERSION


def generate_breadcrumbs(book, chapter, max_chapters, verse=None, max_verses=None):
    """
    Generates breadcrumbs for chapter or verse navigation.
    """
    prev = next = ""
    if verse is not None:
        if verse > 1:
            prev = f"[[{book} {chapter}-{verse-1}|← {book} {chapter}:{verse-1}]]"
        if verse < max_verses:
            next = f"[[{book} {chapter}-{verse+1}|{book} {chapter}:{verse+1} →]]"
        main_link = f"[[{book} {chapter}|{book} {chapter}]]"
    else:
        if chapter > 1:
            prev = f"[[{book} {chapter-1}|← {book} {chapter-1}]]"
        if chapter < max_chapters:
            next = f"[[{book} {chapter+1}|{book} {chapter+1} →]]"
        main_link = f"[[{book}|{book}]]"

    breadcrumbs = " | ".join(filter(None, [prev, main_link, next]))
    return breadcrumbs


def write_file(file_path, content):
    """Writes content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def generate_index(books, chapters_per_book, folder):
    """Generates the master index file."""
    content = ["---\ncssclass: \"bible\"\n---\n", "# The Bible\n\n"]

    for book, max_chapters in zip(books, chapters_per_book):
        content.append(f"**[[{book}/{book}|{book}]]:** ")
        content.append(", ".join(f"[[{book}/{book} {ch}|{ch}]]" for ch in range(1, max_chapters + 1)))
        content.append("\n\n")

    write_file(os.path.join(folder, "The Bible.md"), "".join(content))


def generate_book_files(books, chapters_per_book, folder, version):
    """Generates files for each book and chapter."""
    for book, max_chapters in zip(books, chapters_per_book):
        book_folder = os.path.join(folder, book)
        os.makedirs(book_folder, exist_ok=True)

        book_content = ["---\ncssclass: \"bible\"\n---\n", f"# {book}\n\n", f"[[{book} 1|Start Reading →]]\n"]
        write_file(os.path.join(book_folder, f"{book}.md"), "".join(book_content))

        for chapter in range(1, max_chapters + 1):
            chapter_content = ["---\ncssclass: \"bible\"\n---\n", f"# {book} {chapter}\n\n"]
            chapter_content.append(generate_breadcrumbs(book, chapter, max_chapters) + "\n\n---\n\n")

            reference = f"{book} {chapter}"
            html = fetch_html(reference, version=version)
            chapter_data = parse_chapter(html)

            for element in chapter_data:
                if element["type"] == "subtitle":
                    chapter_content.append(f"## {element['text']}\n\n")
                elif element["type"] == "verse":
                    chapter_content.append(f"![[{book} {chapter}-{element['verse_number']}#{book} {chapter} {element['verse_number']}]]\n\n")

            write_file(os.path.join(book_folder, f"{book} {chapter}.md"), "".join(chapter_content))

            generate_verse_files(book, chapter, chapter_data, book_folder, max_chapters)


def generate_verse_files(book, chapter, chapter_data, folder, max_chapters):
    """Generates files for each verse in a chapter."""
    max_verses = sum(1 for element in chapter_data if element["type"] == "verse")

    for element in chapter_data:
        if element["type"] == "verse":
            verse_number = int(element["verse_number"])
            file_path = os.path.join(folder, f"{book} {chapter}-{verse_number}.md")

            long_alias = f"{book} {chapter}:{verse_number}"
            short_alias = f"{book[:3]} {chapter}:{verse_number}"

            content = ["---\n", "cssclass: \"bible\"\n", f"aliases: [\"{long_alias}\", \"{short_alias}\"]\n", "---\n\n"]
            content.append(generate_breadcrumbs(book, chapter, max_chapters, verse=verse_number, max_verses=max_verses) + "\n\n")
            content.append(f"### {book} {chapter}:{verse_number}\n\n")
            content.append(element["text"] + "\n\n")
            content.append(f"^v{verse_number}\n")

            write_file(file_path, "".join(content))


def main():
    books = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
        "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
        "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
        "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
        "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah",
        "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
        "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John",
        "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians",
        "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
        "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
    ]

    chapters_per_book = [
        50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10,
        13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1,
        4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6,
        6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22
    ]

    bible_folder = "The Bible"
    os.makedirs(bible_folder, exist_ok=True)

    generate_index(books, chapters_per_book, bible_folder)
    generate_book_files(books, chapters_per_book, bible_folder, DEFAULT_VERSION)

    print("Bible files generated successfully.")


if __name__ == "__main__":
    main()
