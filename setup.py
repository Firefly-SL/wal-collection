import re
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def extract_page_number(path: Path) -> float:
    match = re.search(r"\d+", path.stem)
    return float(match.group()) if match else float("inf")


# TODO: need to update the format
def build_index(base_output: Path):
    lines = ["# Global Index Menu\n"]

    for collection_dir in sorted(base_output.iterdir()):
        if not collection_dir.is_dir():
            continue

        collection_name = collection_dir.name
        lines.append(f"## {collection_name}\n")
        lines.append(f"- [{collection_name}/](<{collection_name}>)\n")

        pages = sorted(collection_dir.glob("page*.md"), key=extract_page_number)

        for page in pages:
            page_name = page.stem
            lines.append(f"  - [{page_name}](<{collection_name}/{page.name}>)")

        lines.append("\n")

    index_path = base_output / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")


def get_image_files(folder: Path):
    files = [
        f
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    ]

    return sorted(files, key=lambda x: x.name.lower())


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


# TODO: need to add number based navigation at bottom
def navigation_links(page_num, total_pages):
    lines = []

    if page_num > 1:
        lines.append(f"[← Previous](page{page_num - 1}.md) | ")

    lines.append(
        "[Index Menu](https://github.com/Firefly-SL/wal-collection/tree/testing/pages/index.md)"
    )

    if page_num < total_pages:
        lines.append(f" | [Next →](page{page_num + 1}.md)")
    lines.append("\n")

    return lines


def write_page(output_path: Path, images, page_num, total_pages):
    lines = navigation_links(page_num, total_pages)

    # For images
    for img in images:
        lines.append(
            f"![{img.name}](<https://raw.githubusercontent.com/Firefly-SL/wal-collection/refs/heads/main/{img.as_posix()}>)"
        )

    lines.append("\n")

    for links in navigation_links(page_num, total_pages):
        lines.append(links)

    output_path.write_text("\n".join(lines), encoding="utf-8")


def process_collection(collection_folder: Path, base_output: Path):
    images = get_image_files(collection_folder)

    if not images:
        return

    pages = list(chunk_list(images, 20))
    total_pages = len(pages)

    output_dir = base_output / collection_folder.name
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, page_images in enumerate(pages, start=1):
        page_file = output_dir / f"page{idx}.md"
        write_page(page_file, page_images, idx, total_pages)

    print(f"{collection_folder.name}: {total_pages} pages")


def main():
    root = Path(".")
    output_root = Path("pages")

    for folder in root.iterdir():
        if folder.is_dir() and folder.name.startswith("collection"):
            process_collection(folder, output_root)

    build_index(output_root)


if __name__ == "__main__":
    main()
