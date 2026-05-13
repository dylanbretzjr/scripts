#!/usr/bin/env python3
"""
Anki Media Converter: Converts .ogg to .mp3 and updates flashcard attachments.

Dependencies:
- brew install ffmpeg
- pip install pydub anki
"""

import sys
import re
from pathlib import Path
from pydub import AudioSegment
from anki.collection import Collection

def get_media_folder(profile_name='Dylan'):
    """Constructs and validates the path to the Anki media folder."""
    home_dir = Path.home()
    media_path = home_dir / f'Library/Application Support/Anki2/{profile_name}/collection.media'

    if not media_path.exists():
        print(f'Error: Could not find Anki media folder at:\n{media_path}')
        sys.exit(1)

    if not media_path.is_dir():
        print(f'Error: The path exists but is not a folder:\n{media_path}')
        sys.exit(1)

    return media_path

def get_ogg_files(media_dir):
    """Finds and returns a list of all .ogg files in the given directory."""
    ogg_files = list(media_dir.glob('*.ogg'))

    if not ogg_files:
        print('No .ogg files found in the media directory. Exiting.')
        sys.exit(0)
 
    print(f'\nFound {len(ogg_files)} .ogg files ready for conversion.')
    return ogg_files

def convert_to_mp3(ogg_files):
    """
    Converts a list of .ogg files to .mp3 format in the same directory.
    Returns a list of the .ogg file paths that were SUCCESSFULLY converted.
    """
    total_files = len(ogg_files)
    print(f'\nStarting conversion of {total_files} files...\n')

    successful_oggs = []

    for i, ogg_path in enumerate(ogg_files, 1):
        mp3_path = ogg_path.with_suffix('.mp3')

        # Skip if already converted
        if mp3_path.exists():
            print(f'[{i}/{total_files}] Skipping: {mp3_path.name} (Already exists)')
            successful_oggs.append(ogg_path)
            continue

        print(f'[{i}/{total_files}] Converting: {ogg_path.name} -> {mp3_path.name}')

        try:
            audio = AudioSegment.from_file(ogg_path, format='ogg')
            audio.export(mp3_path, format='mp3', bitrate='192k')
            successful_oggs.append(ogg_path) # Append original path on success
        except Exception as e:
            print(f'Error converting {ogg_path.name}: {e}')

    print('\nAudio conversion complete!')
    return successful_oggs

def process_card_text(text, converted_filenames_set):
    """
    Scans a block of text, updates converted .ogg references to .mp3.
    
    Returns: (new_text, text_changed, broken_links)
    """
    new_text = text
    text_changed = False
    broken_links = []

    # Find all .ogg references currently in text
    found_oggs = re.findall(r'\[sound:([^\]]+\.ogg)\]', new_text)

    for ogg_filename in found_oggs:
        # Check if this specific file was converted
        if ogg_filename in converted_filenames_set:
            mp3_filename = ogg_filename.replace('.ogg', '.mp3')
            
            old_tag = f'[sound:{ogg_filename}]'
            new_tag = f'[sound:{mp3_filename}]'
            
            new_text = new_text.replace(old_tag, new_tag)
            text_changed = True
        else:
            # If it's in the text but wasn't converted, it's broken/missing
            broken_links.append(ogg_filename)

    return new_text, text_changed, broken_links

def update_anki(media_dir, converted_ogg_paths):
    """
    Connects to the Anki database and updates flashcards.
    """
    db_path = media_dir.parent / 'collection.anki2'

    print(f'\nOpening Anki collection at: {db_path.name}...')
    try:
        col = Collection(str(db_path))
    except Exception as e:
        print(f'Error: Could not open collection. Is Anki running?\nDetails: {e}')
        sys.exit(1)

    # Convert list of paths to Set of filenames
    converted_filenames_set = {path.name for path in converted_ogg_paths}
    all_broken_links = set()
    cards_updated_count = 0

    try:
        note_ids = col.find_notes('.ogg')
        print(f"Found {len(note_ids)} notes containing '.ogg' references.")

        for nid in note_ids:
            note = col.get_note(nid)
            note_needs_saving = False

            for field_name, field_content in note.items():
                if '.ogg' not in field_content:
                    continue

                # Process text using helper function
                new_content, field_changed, broken = process_card_text(
                    field_content, 
                    converted_filenames_set
                )

                if field_changed:
                    note[field_name] = new_content
                    note_needs_saving = True

                all_broken_links.update(broken)

            if note_needs_saving:
                col.update_note(note)
                cards_updated_count += 1

        # Deprecated: saving is automatic
        # col.save()
    finally:
        col.close()

    print(f'\nSuccessfully updated {cards_updated_count} flashcards.')

    if all_broken_links:
        print('\n⚠️ WARNING: Found broken or unconverted .ogg references:')
        for broken in all_broken_links:
            print(f'  - {broken}')

def cleanup_old_files(ogg_paths):
    """
    Deletes the original .ogg files after successful conversion to save storage space.
    """
    print('\nCleaning up old .ogg files...')
    cleaned_count = 0
    for ogg_file in ogg_paths:
        try:
            if ogg_file.exists():
                ogg_file.unlink() # Delete file
                cleaned_count += 1
        except Exception as e:
            print(f'Could not delete {ogg_file.name}: {e}')

    print(f'Deleted {cleaned_count} original .ogg files to save space.')
    return cleaned_count

if __name__ == '__main__':
    print('--- Anki Media Converter ---')

    media_folder = get_media_folder()

    files_to_convert = get_ogg_files(media_folder)

    successful_oggs = convert_to_mp3(files_to_convert)
    
    if not successful_oggs:
        print('\nNo files were successfully converted. Exiting safely.')
        sys.exit(0)

    update_anki(media_folder, successful_oggs)

    cleanup_old_files(successful_oggs)

    print('\nProcess finished successfully!')
