# VaultX

A highly secure, portable, and visually striking "Hacker/Terminal" styled encrypted file vault. 

VaultX functions as an enclosed digital enclave. By dropping your raw files into VaultX, they are physically wiped from your drive and cryptographically sealed into a proprietary `.vault` payload file. Only the possessor of the 007-style Encryption Key can decrypt the payload and mount the files back into the VaultX viewer memory.

## Features
- **True Encryption**: Utilizes heavy-duty cryptography to securely encrypt and salt your file data upon lock.
- **In-Memory Viewer**: Natively unloads and streams supported file formats (Images, Text, PDF) directly to your screen from RAM—without physically extracting them back to an insecure folder.
- **Cyber-Aesthetic**: Built with a stunning `QSS` terminal stylesheet for a clean, focus-driven user experience.
- **Portable Enclave Architecture**: Your entire database lives perfectly self-contained within the `sys_data.vault` file, meaning you can drop this `.exe` and `.vault` onto a USB drive and safely move your ecosystem anywhere.

## Usage
1. Set an arbitrary Decryption Key to initialize and format your brand new Enclave.
2. Hit `IMPORT` to ingest your sensitive local files into the Vault.
3. Use the `OPEN` command to load supported files into the secure Matrix Viewer.
4. Hit `LOCK` when you are done to terminate the memory footprint and permanently seal the vault.

## Developer Installation
Ensure you have Python 3 installed. Then, use pip to install the required libraries:
```bash
pip install -r requirements.txt
python main.py
```

## License
This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software.
