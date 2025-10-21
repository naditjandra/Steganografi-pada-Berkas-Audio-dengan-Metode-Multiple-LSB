import os

def vigenere_cipher_bytes(data: bytes, keyword: str, mode='encrypt') -> bytes:
    # Encrypt or decrypt binary data using Vigenère cipher on bytes.
    key = keyword.encode('utf-8')
    key_len = len(key)
    result = bytearray()

    for i, byte in enumerate(data):
        shift = key[i % key_len]
        if mode == 'decrypt':
            new_byte = (byte - shift) % 256
        else:  # encrypt
            new_byte = (byte + shift) % 256
        result.append(new_byte)

    return bytes(result)


def process_file(input_file: str, keyword: str, mode='encrypt'):
    # Encrypt or decrypt the given file.
    if not os.path.exists(input_file):
        print("Error: file not found.")
        return

    with open(input_file, 'rb') as f:
        data = f.read()

    processed_data = vigenere_cipher_bytes(data, keyword, mode)

    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_{'encrypted' if mode == 'encrypt' else 'decrypted'}{ext}"

    with open(output_file, 'wb') as f:
        f.write(processed_data)

    print(f"{mode.capitalize()}ed file saved as: {output_file}")


def main():
    print("=== Vigenère Cipher File Encryptor/Decryptor ===")
    print("Encrypt any file using Extended Vigenère cipher in Bytes.")
    print("=" * 60)
    print("1. Encypt file")
    print("2. Decrypt file")
    mode = input("Choose mode (1/2): ").strip()
    input_file = input("Enter source file: ").strip()
    keyword = input("Enter keyword: ").strip()

    if not keyword:
        print("Keyword cannot be empty.")
        return

    if mode == '1':
        process_file(input_file, keyword, "encrypt")
    elif mode == '2':
        process_file(input_file, keyword, "decrypt")
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

if __name__ == "__main__":
    main()