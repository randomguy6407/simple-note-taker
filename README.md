# Simple CLI note taker app
A simple note taker app made in python and using CLI as its gui. This app allows you to write down any note for yourself and you can access it later on, stored in a simple JSON file. Optionally, you can also encrypt your messages and decrypt them with a special key for any sensitive information you choose to store in the app.

# Features
- Tagging | You can tag your notes in this app and sort them easily while in the pagnation page!
- Editing | You can also edit your notes if you made any typos or you want to update information
- Encryption | Any content that is encrypted is done so with Fernet encryption, so that your contents inside your note will be kept safe
- Search function | You can also either search your notes via tags / titles / indexes!

# Installation guide
```
git clone https://github.com/randomguy6407/simple-note-taker
cd simple-note-taker
pip install -r requirements.txt
python3 note_taker.py
```
