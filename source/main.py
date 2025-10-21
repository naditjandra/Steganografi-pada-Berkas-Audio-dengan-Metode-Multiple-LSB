import os # For file operations
import wave # For handling WAV files
import struct # For handling binary data
from pydub import AudioSegment # For audio format conversion
import vigenere  # Import Vigenère cipher module
import steganoencrypt as stegano  # Import steganography module

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
        stegano.encode_audio(input_audio, output_audio, secret_file, encrypt_key)
            
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
        stegano.decode_audio(encoded_audio, decrypt_key)
        
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    running = True
    while running:
        main()
        quit = input("Quit Program? (y/n): ").strip()
        if quit == 'y':
            break