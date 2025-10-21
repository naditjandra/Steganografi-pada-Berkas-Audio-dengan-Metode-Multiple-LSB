import os # For file operations
import wave # For handling WAV files
import struct # For handling binary data
from pydub import AudioSegment # For audio format conversion
import vigenere  # Import Vigenère cipher module

def file_to_bin(filename, encrypt_key=None):
    # Convert any file to binary string with optional encryption.
    try:
        with open(filename, 'rb') as file:
            file_data = file.read()
        
        # Encrypt the file data if key is provided
        if encrypt_key:
            print(f"Encrypting file with Vigenère cipher...")
            file_data = vigenere.vigenere_cipher_bytes(file_data, encrypt_key, 'encrypt')
        
        # Convert file bytes to binary string
        binary_data = ''.join(format(byte, '08b') for byte in file_data)
        
        # Add file signature with markers
        file_ext = os.path.splitext(filename)[1].lower()
        file_size = len(file_data)

        # Add encryption flag to header
        encryption_flag = "ENCRYPTED" if encrypt_key else "PLAIN"
        file_info = f"STEGO_FILE_START:{file_ext}:{file_size}:{encryption_flag}:STEGO_FILE_END:"
        file_info_bin = text_to_bin(file_info)
        
        return file_info_bin + binary_data
    
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return None

def bin_to_file(binary_string, decrypt_key=None):
    # Convert binary string back to file with optional decryption.
    try:
        # Look for the start marker in binary
        start_marker = "STEGO_FILE_START:"
        end_marker = ":STEGO_FILE_END:"

        start_marker_bin = text_to_bin(start_marker)
        end_marker_bin = text_to_bin(end_marker)
        
        start_index = binary_string.find(start_marker_bin)
        if start_index == -1:
            print("No file header found in binary data")
            return None
        
        # Find the end of the header
        header_end_index = binary_string.find(end_marker_bin, start_index)
        if header_end_index == -1:
            print("Incomplete file header")
            return None
        
        # Extract the complete header
        header_end_index += len(end_marker_bin)
        header_bin = binary_string[start_index:header_end_index]
        header_text = bin_to_text(header_bin)
        
        # Parse file info, example: "STEGO_FILE_START:.png:12345:ENCRYPTED:STEGO_FILE_END:"
        if not header_text.startswith(start_marker) or not header_text.endswith(end_marker):
            print("Invalid file header format")
            return None
            
        # Extract the parts between markers
        content = header_text[len(start_marker):-len(end_marker)]
        parts = content.split(':')
        if len(parts) < 3:
            print("Invalid file info in header")
            return None
            
        file_ext = parts[0]
        file_size = int(parts[1])
        encryption_flag = parts[2]
        
        # Check if file is encrypted but no key provided
        if encryption_flag == "ENCRYPTED" and not decrypt_key:
            print("File is encrypted! Please provide a decryption key.")
            return None
        
        # Calculate where file data starts (after header)
        file_data_start = header_end_index
        file_data_end = file_data_start + (file_size * 8)
        
        if file_data_end > len(binary_string):
            print(f"Incomplete file data. Expected {file_size * 8} bits, got {len(binary_string) - file_data_start} bits")
            return None
        
        file_data_bin = binary_string[file_data_start:file_data_end]
        
        # Convert binary back to bytes
        file_bytes = bytearray()
        for i in range(0, len(file_data_bin), 8):
            byte_bin = file_data_bin[i:i+8]
            if len(byte_bin) == 8:
                file_bytes.append(int(byte_bin, 2))
        
        if len(file_bytes) != file_size:
            print(f"File size mismatch. Expected {file_size}, got {len(file_bytes)}")
            return None
        
        # Decrypt if encrypted
        if encryption_flag == "ENCRYPTED" and decrypt_key:
            print(f"Decrypting file with Vigenère cipher...")
            file_bytes = vigenere.vigenere_cipher_bytes(bytes(file_bytes), decrypt_key, 'decrypt')
        
        # Generate output filename
        base_name = "extracted_file"
        counter = 1
        output_filename = f"{base_name}{file_ext}"
        while os.path.exists(output_filename):
            output_filename = f"{base_name}_{counter}{file_ext}"
            counter += 1
        
        # Write the file
        with open(output_filename, 'wb') as f:
            f.write(file_bytes)
        
        print(f"Successfully extracted {len(file_bytes)} byte file")
        if encryption_flag == "ENCRYPTED":
            print(f"File was decrypted successfully")
        return output_filename
        
    except Exception as e:
        print(f"Error reconstructing file: {e}")
        return None

def text_to_bin(text):
    """Convert text to a binary string (used for file headers)."""
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_text(binary):
    """Convert a binary string to readable text (used for file headers)."""
    text = ''
    for i in range(0, len(binary), 8):
        byte_bin = binary[i:i+8]
        if len(byte_bin) == 8:
            text += chr(int(byte_bin, 2))
    return text

def ensure_wav(filename):
    # Check if the file exists and is a valid audio file. Convert it to WAV automatically if needed.
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return None, False

    audio_extensions = ('.wav', '.mp3', '.flac', '.ogg', '.aac', '.m4a')
    if not filename.lower().endswith(audio_extensions):
        print(f"Error: '{filename}' is not an audio file.")
        return None, False

    try:
        audio = AudioSegment.from_file(filename)
    except Exception as e:
        print(f"Error: File '{filename}' could not be opened as audio.\nReason: {e}")
        return None, False

    if not filename.lower().endswith('.wav'):
        wav_name = os.path.splitext(filename)[0] + "_converted.wav"
        print(f"Converting '{filename}' to WAV format...")
        audio.export(wav_name, format="wav")
        print(f"Converted to '{wav_name}'.")
        return wav_name, True  # Temporary file created

    return filename, False  # Original file, not temporary

def cleanup_temp_file(filename):
    # Delete temporary WAV file if it exists.
    if filename and os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Cleaned up temporary file: '{filename}'")
        except Exception as e:
            print(f"Warning: Could not delete temporary file '{filename}': {e}")

def encode_audio(input_audio, output_audio, secret_file, encrypt_key=None):
    # Encodes a file into a WAV audio file using LSB with optional encryption.
    input_audio, is_temp = ensure_wav(input_audio)
    if not input_audio:
        return

    try:
        # Handle file encoding with optional encryption
        message_bin = file_to_bin(secret_file, encrypt_key)
        if not message_bin:
            print("Error: Could not read the secret file.")
            return

        with wave.open(input_audio, 'rb') as audio:
            params = audio.getparams()
            n_frames = audio.getnframes()
            sampwidth = params.sampwidth
            nchannels = params.nchannels
            raw_data = audio.readframes(n_frames)

        # Determine correct format based on sample width
        fmt_map = {1: 'B', 2: 'h', 4: 'i'}
        if sampwidth not in fmt_map:
            raise ValueError(f"Unsupported sample width: {sampwidth} bytes")

        fmt = '<' + fmt_map[sampwidth] * n_frames * nchannels
        audio_data = list(struct.unpack(fmt, raw_data))

        if len(message_bin) > len(audio_data):
            print(f"Error: File too large for this audio file!")
            print(f"Available space: {len(audio_data)} bits ({len(audio_data)//8} bytes)")
            print(f"File requires: {len(message_bin)} bits ({len(message_bin)//8} bytes)")
            print(f"File size: {os.path.getsize(secret_file)} bytes")
            return

        print(f"Encoding {len(message_bin)} bits ({len(message_bin)//8} bytes) of data...")
        if encrypt_key:
            print(f"File is encrypted with Vigenère cipher")
        
        encoded_data = []
        for i in range(len(audio_data)):
            if i < len(message_bin):
                sample = audio_data[i]
                bit = int(message_bin[i])
                if bit == 1:
                    sample |= 1
                else:
                    sample &= ~1
                encoded_data.append(sample)
            else:
                encoded_data.append(audio_data[i])

        # Pack the encoded data using the correct format
        packed_data = struct.pack(fmt, *encoded_data)

        with wave.open(output_audio, 'wb') as encoded:
            encoded.setparams(params)
            encoded.writeframes(packed_data)

        print(f"File encoded successfully into '{output_audio}'")
        print(f"Utilization: {len(message_bin)/len(audio_data)*100:.1f}%")
        
    except Exception as e:
        print(f"Encoding error: {e}")
    finally:
        # Clean up temporary file if one was created
        if is_temp:
            cleanup_temp_file(input_audio)

def decode_audio(encoded_audio, decrypt_key=None):
    # Decodes and extracts hidden file from a WAV audio file with optional decryption.
    encoded_audio, is_temp = ensure_wav(encoded_audio)
    if not encoded_audio:
        return
    
    try:
        with wave.open(encoded_audio, 'rb') as audio:
            params = audio.getparams()
            n_frames = audio.getnframes()
            sampwidth = params.sampwidth
            nchannels = params.nchannels
            raw_data = audio.readframes(n_frames)

        fmt_map = {1: 'B', 2: 'h', 4: 'i'}
        if sampwidth not in fmt_map:
            raise ValueError(f"Unsupported sample width: {sampwidth} bytes")

        fmt = '<' + fmt_map[sampwidth] * n_frames * nchannels
        audio_data = list(struct.unpack(fmt, raw_data))

        print(f"Analyzing {len(audio_data)} samples...")
        bits = [str(sample & 1) for sample in audio_data]
        binary = ''.join(bits)

        print("Searching for hidden file...")
        # Try to detect and extract the file
        file_path = bin_to_file(binary, decrypt_key)
        if file_path:
            print(f"File extracted successfully!")
            print(f"Saved as: {file_path}")
            file_size = os.path.getsize(file_path)
            print(f"Extracted file size: {file_size} bytes")
        else:
            print("No hidden file found or data is corrupted.")
            
    except Exception as e:
        print(f"Decoding error: {e}")
    finally:
        # Clean up temporary file if one was created
        if is_temp:
            cleanup_temp_file(encoded_audio)

def main():
    # Main 
    print("=== Secure File Audio Steganography Tool ===")
    print("Hide any file inside audio files with encryption")
    print("=" * 60)
    print("1. Hide file in audio")
    print("2. Extract file from audio")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        input_audio = input("Enter source audio file: ").strip()
        output_audio = input("Enter output audio file name: ").strip()
        secret_file = input("Enter file to hide: ").strip()
        
        # Ask about encryption
        use_encryption = input("Encrypt the file? (y/n): ").strip().lower()
        encrypt_key = None
        if use_encryption == 'y':
            encrypt_key = input("Enter encryption key: ").strip()
            if not encrypt_key:
                print("Keyword cannot be empty!")
                return
        
        if not os.path.exists(input_audio):
            print(f"Error: Audio file '{input_audio}' not found!")
            return
            
        if not os.path.exists(secret_file):
            print(f"Error: Secret file '{secret_file}' not found!")
            return
            
        print(f"\nHiding '{secret_file}' in audio...")
        encode_audio(input_audio, output_audio, secret_file, encrypt_key)
            
    elif choice == '2':
        encoded_audio = input("Enter encoded audio file: ").strip()
        
        # Ask about decryption
        need_decryption = input("Is the file encrypted? (y/n): ").strip().lower()
        decrypt_key = None
        if need_decryption == 'y':
            decrypt_key = input("Enter decryption key: ").strip()
            if not decrypt_key:
                print("Decryption key cannot be empty!")
                return
        
        if not os.path.exists(encoded_audio):
            print(f"Error: Audio file '{encoded_audio}' not found!")
            return
            
        print(f"\nExtracting hidden file from '{encoded_audio}'...")
        decode_audio(encoded_audio, decrypt_key)
        
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()