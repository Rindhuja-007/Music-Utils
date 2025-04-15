import os
import subprocess

def convert_audio_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    formats = {
        1: 'mp3',
        2: 'wav',
        3: 'm4a'
    }

    print("\nChoose a format to convert to:")
    for key, fmt in formats.items():
        print(f"{key}. {fmt.upper()}")

    while True:
        try:
            choice = int(input("Enter your choice: "))
            if choice not in formats:
                print("Invalid choice.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    target_format = formats[choice]
    supported_extensions = ('.mp3', '.wav', '.m4a', '.mp4')

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(supported_extensions):
                input_path = os.path.join(root, file)
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_file = os.path.join(output_folder, f"{base_name}.{target_format}")

                try:
                    print(f"Converting {file} → {target_format.upper()}")
                    subprocess.run([
                        "ffmpeg", "-y", "-i", input_path, output_file
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
                    print(f"Saved: {output_file}")
                except subprocess.CalledProcessError:
                    print(f"Failed to convert: {file}")

if __name__ == "__main__":
    input_folder = input("Enter the input folder path: ").strip().replace('"', '')
    output_folder = input("Enter the output folder path: ").strip().replace('"', '')
    convert_audio_files(input_folder, output_folder)
