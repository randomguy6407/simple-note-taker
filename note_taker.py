import os
import json
import time
import base64
from cryptography.fernet import Fernet

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def custom_encrypt(data):
    data = data.encode()
    key = Fernet.generate_key()
    cipher = Fernet(key)
    token = cipher.encrypt(data)

    key   = base64.b64encode(key).decode()
    token = base64.b64encode(token).decode()

    print(key)
    print("This is your custom key for your note, please store it somewhere safe. [If you dont have the key, you cant unlock the contents in this note!] (continuing in 10 seconds)")
    time.sleep(10)
    return key, token


def custom_decrypt(key, token):
    key   = base64.b64decode(key)
    token = base64.b64decode(token)
    return Fernet(key).decrypt(token).decode()


def note_setup(kind):
    clear()
    filename = "notes.json"
    tag = []

    with open(filename, "r") as f:
        all_notes = json.load(f)

    if kind == "auto":
        title = input("Title: ")
        note  = input("Note (include at least one #tag): ")
        encrypt_check = input("Encrypt? (y/n) ").strip().lower() == "y"

        if "#" not in note:
            print("No tags detected!  Start again and include a #tag.")
            return

        edited_note = note
        for word in note.split():
            if "#" in word:
                tag.append(word)
                edited_note = edited_note.replace(word, "")

        if encrypt_check:
            _, edited_note = custom_encrypt(edited_note)

        saved_note = {
            "title": title,
            "content": edited_note.strip(),
            "tag": " ".join(tag),
            "encrypted": encrypt_check,
        }
        all_notes.append(saved_note)
        with open(filename, "w") as f:
            json.dump(all_notes, f, indent=4)
        print("Saved.")

    elif kind == "manual":
        title = input("Title: ")
        note  = input("Note: ")
        tag   = input("Tags: ")
        encrypt_check = input("Encrypt? (y/n) ").strip().lower() == "y"
        if encrypt_check:
            _, note = custom_encrypt(note.strip())
        saved_note = {
            "title": title,
            "content": note.strip(),
            "tag": tag,
            "encrypted": encrypt_check,
        }
        all_notes.append(saved_note)
        with open(filename, "w") as f:
            json.dump(all_notes, f, indent=4)
        print("Saved.")

def note_options(kind):
    with open("notes.json", "r") as f:
        all_notes = json.load(f)
    if not all_notes:
        print("No notes yet.")
        return

    if kind == "view":
        idx = display_notes(0, 5, "title", "Select a note to view")
        if idx is None:
            return
        note = all_notes[idx]
        content = (
            custom_decrypt(input("Encrypted – key: "), note["content"])
            if note["encrypted"]
            else note["content"]
        )
        print(f"{20*'-'}")
        print(f"Content | {content}")
        print(f"Tags | [{' ' .join(note['tag'].split())}]")
        print(f"{20*'-'}")

    elif kind == "delete":
        idx = display_notes(0, 5, "title", "Select a note to delete")
        if idx is not None:
            delete_note("single", idx)

    elif kind == "batch_delete":
        delete_note("batch", None)

    elif kind == "edit":
        idx = display_notes(0, 5, "title", "Select a note to edit")
        if idx is None:
            return
        note = all_notes[idx]
        old_title = note["title"]
        old_content = (
            custom_decrypt(input("Encrypted – key: "), note["content"])
            if note["encrypted"]
            else note["content"]
        )
        old_tag = note["tag"]

        print("Current title:", old_title)
        print(f"{idx + 1} | {old_content} [{old_tag}]")

        new_title   = input("New title: ")
        new_content = input("New content: ")
        if note["encrypted"]:
            _, new_content = custom_encrypt(new_content)
        new_tag = input("New tags: ")

        all_notes[idx] = {
            "title": new_title,
            "content": new_content.strip(),
            "tag": new_tag,
            "encrypted": note["encrypted"],
        }
        with open("notes.json", "w") as f:
            json.dump(all_notes, f, indent=4)
        print("Edited.")
    
def display_notes(start, page_size, view_type, prompt):
    
    def load():
        try:
            with open("notes.json") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    notes = load()
    if not notes:
        print("Nothing to show!")
        return None

    total = len(notes)
    start = max(0, min(start, total - 1))

    def print_page(s):
        e = min(s + page_size, total)
        for i in range(s, e):
            note = notes[i]
            if note["encrypted"]:
                snippet = "<encrypted>"
            else:
                snippet = (note["content"].strip().splitlines() or [""])[0][:40]
            tags = note["tag"].strip()
            print(f"{i+1} | {snippet} [{tags}]")
        print(f"Showing {s+1}-{e} of {total}")


    while True:
        clear()
        print_page(start)
        user = input(
            f"\nSearch by tag/title, or {prompt}. "
            "(n next, b back): "
        ).strip()

        if user.isdigit():
            n = int(user)
            if 1 <= n <= total: 
                return n - 1
            input("Invalid index. Enter...")
            continue

        if user and user.lower() not in {"n", "b"}:
            needle = user.lower().lstrip("#")
            hits = [
                i
                for i, note in enumerate(notes)
                if needle in note["title"].lower()
                or needle in [t.lstrip("#").lower() for t in note["tag"].split()]
            ]
            if not hits:
                input("No match. Enter...")
                continue
            print("\nMatches:")
            for j, i in enumerate(hits, 1):
                print(f"{j}) {notes[i]['title']}")
            pick = input("Open number or Enter to cancel: ").strip()
            if pick.isdigit():
                p = int(pick)
                if 1 <= p <= len(hits):
                    return hits[p - 1]
            continue

        cmd = user.lower()
        if cmd == "n":
            start = start + page_size if start + page_size < total else start
        elif cmd == "b":
            start = start - page_size if start - page_size >= 0 else start
        else:
            input("Invalid option. Enter...")

def delete_note(kind, index):
    clear()
    with open("notes.json", "r") as f:
        all_notes = json.load(f)
    if not all_notes:
        print("Nothing to delete.")
        return
    if kind == "single":
        all_notes.pop(index)
        with open("notes.json", "w") as f:
            json.dump(all_notes, f, indent=4)
        print("Deleted index", index + 1)
    elif kind == "batch":
        if input("Are you ABSOLUTELY sure? (y/n) ").strip().lower() == "y":
            print("Deleting in 10 s… Ctrl‑C to abort.")
            time.sleep(10)
            with open("notes.json", "w") as f:
                json.dump([], f, indent=4)
            print("Cleared.")

def main():
    clear()
    for fn in ("notes.json", "config.json"):
        if not os.path.exists(fn):
            with open(fn, "w") as f:
                json.dump([], f)

    while True:
        print("Quick note‑taking CLI")
        print(f"{20*'-'}")
        print("1) Auto setup note")
        print("2) Manual setup note")
        print("3) Review a note")
        print("4) Edit a note")
        print("5) Delete a note")
        print("6) COMPLETE WIPE")
        print("0) Exit")
        print(f"{20*'-'}")
        try:
            opt = int(input("choice | "))
        except ValueError:
            clear()
            print("Invalid option!")
            continue
        clear()

        if opt == 1:
            note_setup("auto")
        elif opt == 2:
            note_setup("manual")
        elif opt == 3:
            note_options("view")
        elif opt == 4:
            note_options("edit")
        elif opt == 5:
            note_options("delete")
        elif opt == 6:
            note_options("batch_delete")
        elif opt == 0:
            print("Bye!")
            break
        else:
            print("Invalid option!")


if __name__ == "__main__":
    main()
