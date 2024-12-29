import subprocess
import os
import shutil
import re
import gc

def generate_subtitle_file(subtitle_file):
    """Generate a subtitle file with predefined content."""
    try:
        print(f"Generating subtitle file {subtitle_file}...")
        with open(subtitle_file, "w") as f:
            f.write("""[Script Info]
Title: Default Google file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,-1,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:25.00,Default,,0,0,0,,{\b1\c&H16EB22&}Downloaded From {\c&HFFAB00&}Google.in{\b0}""")
        print(f"Subtitle file {subtitle_file} created successfully.")
        return True
    except Exception as e:
        print(f"Error generating subtitle file: {e}")
        return False

def delete_file(file_path):
    """Delete a file if it exists and ensure disk space is freed."""
    try:
        if os.path.exists(file_path):
            print(f"Deleting file {file_path}...")
            os.remove(file_path)
            # Run garbage collection to release resources
            gc.collect()
            # Synchronize the file system to reflect changes
            os.system("sync")
            print(f"File {file_path} deleted and disk space updated.")
        else:
            print(f"File {file_path} does not exist.")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")

def add_subtitle_as_latest_track(input_file, output_file, subtitle_file):
    """Add the generated subtitle as the latest track in the MKV file."""
    try:
        temp_file = output_file + ".temp.mkv"
        print(f"Adding subtitle {subtitle_file} as the latest track to {output_file}...")

        subprocess.run(
            [
                'mkvmerge', '-o', temp_file, input_file,
                '--language', '0:eng',
                '--track-name', '0:Google Subtitle',
                subtitle_file
            ],
            check=True
        )

        shutil.move(temp_file, output_file)
        print(f"Successfully added subtitle as the latest track in {output_file}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding subtitle track: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def set_mkv_metadata_for_folder(input_folder, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mkv"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)

            # Avoid overwriting files by ensuring unique names if needed
            if os.path.exists(output_file):
                base, ext = os.path.splitext(filename)
                count = 1
                while os.path.exists(output_file):
                    output_file = os.path.join(output_folder, f"{base}_{count}{ext}")
                    count += 1

            # Copy the input file to the output file path
            try:
                print(f"Copying {input_file} to {output_file}...")
                shutil.copyfile(input_file, output_file)
            except Exception as e:
                print(f"Error copying file {input_file}: {e}")
                continue

            # Generate and add a new subtitle track
            subtitle_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_new_subtitle.ass")
            if generate_subtitle_file(subtitle_file):
                if add_subtitle_as_latest_track(input_file, output_file, subtitle_file):
                    # Delete the subtitle file after successfully adding it to the MKV file
                    delete_file(subtitle_file)

            # Set the global title
            try:
                print(f"Setting global title to 'Visit & Support - Google.in' for {output_file}")
                subprocess.run(
                    ['mkvpropedit', output_file, '--edit', 'info', '--set', 'title=Visit & Support - Google.in'],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error setting global title for {output_file}: {e}")
                continue

            # Use mkvinfo to get track details
            try:
                result = subprocess.run(
                    ['mkvinfo', input_file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                mkv_info = result.stdout
            except subprocess.CalledProcessError as e:
                print(f"Error retrieving MKV info for {input_file}: {e}")
                continue

            # Regular expressions to match track information
            track_info_re = re.compile(
                r"\+ Track number: (\d+).*?\+ Track type: (\w+)", re.DOTALL
            )

            # Find all track details (track number and type)
            tracks = track_info_re.findall(mkv_info)

            # Go through each track and rename it based on its type
            for track_number, track_type in tracks:
                track_type = track_type.strip()

                try:
                    if track_type == "video":
                        print(f"Setting title for video track {track_number} to 'Google.in' in {output_file}")
                        subprocess.run(
                            ['mkvpropedit', output_file, '--edit', f"track:{track_number}", '--set', 'name=Google.in'],
                            check=True
                        )
                    elif track_type == "audio":
                        print(f"Setting title for audio track {track_number} to 'Google.in' in {output_file}")
                        subprocess.run(
                            ['mkvpropedit', output_file, '--edit', f"track:{track_number}", '--set', 'name=Google.in'],
                            check=True
                        )
                    elif track_type == "subtitles":
                        print(f"Setting title for subtitle track {track_number} to 'Google.in' in {output_file}")
                        subprocess.run(
                            ['mkvpropedit', output_file, '--edit', f"track:{track_number}", '--set', 'name=Google.in'],
                            check=True
                        )
                except subprocess.CalledProcessError as e:
                    print(f"Error setting {track_type} track title in {output_file}: {e}")
                    continue

            print(f"Done with {output_file}.\n")

            # Delete the original input file after successful processing
            try:
                delete_file(input_file)
                print(f"Original file {input_file} deleted after successful processing.")
            except Exception as e:
                print(f"Error deleting original file {input_file}: {e}")

# Specify the input folder and output folder
input_folder = '/content/Movies'  # Update with the path to your input folder
output_folder = '/content/Moviez'  # Update with the path for the output folder

# Run the metadata update process for all MKV files in the folder
set_mkv_metadata_for_folder(input_folder, output_folder)
