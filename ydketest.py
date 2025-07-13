import base64
import struct
from tkinter import Tk, Text, Button, END, messagebox
from typing import NamedTuple, List

class TypedDeck(NamedTuple):
    main: List[int]
    extra: List[int]
    side: List[int]

def base64_to_passcodes(base64_str: str) -> bytes:
    decoded_bytes = base64.b64decode(base64_str)
    return struct.unpack(f"<{len(decoded_bytes) // 4}L", decoded_bytes)

def passcodes_to_base64(passcodes: List[int]) -> str:
    encoded_bytes = struct.pack(f"<{len(passcodes)}L", *passcodes)
    return base64.b64encode(encoded_bytes).decode('utf-8')

def parse_url(ydke: str) -> TypedDeck:
    if not ydke.startswith("ydke://"):
        raise ValueError("Unrecognized URL protocol")
    
    components = ydke[len("ydke://"):].split("!")
    if len(components) < 3:
        raise ValueError("Missing ydke URL component")
    
    def decode_component(component: str) -> List[int]:
        try:
            return list(base64_to_passcodes(component))
        except Exception as e:
            raise ValueError(f"Failed to decode component: {e}")
    
    return TypedDeck(
        main=decode_component(components[0]),
        extra=decode_component(components[1]),
        side=decode_component(components[2])
    )

def to_url(deck: TypedDeck) -> str:
    return "ydke://" + "!".join(
        passcodes_to_base64(part) for part in (deck.main, deck.extra, deck.side)
    ) + "!"

def parse_deck_text(text: str) -> TypedDeck:
    sections = {'main': [], 'extra': [], 'side': []}
    current_section = None
    
    lines = text.strip().split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.lower() in ['#main', '#extra', '!side']:
            current_section = stripped_line.strip('#!').lower()
        elif stripped_line and current_section:
            try:
                card_id = int(stripped_line)
                sections[current_section].append(card_id)
            except ValueError:
                continue
    
    return TypedDeck(**sections)

def on_convert_click():
    input_text = text_input.get("1.0", END).strip()
    try:
        deck = parse_deck_text(input_text)
        result_url = to_url(deck)
        output_text.delete("1.0", END)
        output_text.insert(END, result_url)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_paste_click():
    text_input.delete("1.0", END)
    text_input.insert(END, root.clipboard_get())

def on_copy_click():
    result_text = output_text.get("1.0", END).strip()
    root.clipboard_clear()
    root.clipboard_append(result_text)
    messagebox.showinfo("Info", "Copied to clipboard!")

root = Tk()
root.title("YDKE生成")

text_input = Text(root, height=20, width=80)
text_input.pack(padx=10, pady=10)

paste_button = Button(root, text="粘贴YDK", command=on_paste_click)
paste_button.pack(pady=5)

convert_button = Button(root, text="转换到YDKE", command=on_convert_click)
convert_button.pack(pady=5)

output_text = Text(root, height=5, width=80)
output_text.pack(padx=10, pady=10)

copy_button = Button(root, text="复制YDKE", command=on_copy_click)
copy_button.pack(pady=5)

root.mainloop()