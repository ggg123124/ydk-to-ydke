import base64
import json
import struct
from tkinter import ttk, Tk, Text, END, FALSE, messagebox
from typing import NamedTuple, List

SAVE = "decks.json"

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

def enable_deck():
    if selected != None:
        deck_buttons[selected].state(['!disabled'])

def disable_deck():
    if selected != None:
        deck_buttons[selected].state(['disabled'])

def render_deck(i, name):
    button = ttk.Button(decks, text=name, command=lambda: on_deck_click(i))
    button.grid(column=0, row=len(deck_buttons))
    deck_buttons.append(button)

def render_all_decks():
    global deck_buttons
    for button in deck_buttons:
        button.destroy()
    deck_buttons = []

    for i in range(0, len(deckdata)):
        [name, _] = deckdata[i]
        render_deck(i, name)

def save():
    with open(SAVE, "w") as file:
        json.dump(deckdata, file)

def on_deck_click(i):
    global selected
    enable_deck()
    selected = i
    disable_deck()
    [_, ydke] = deckdata[i]
    output_text.delete("1.0", END)
    output_text.insert(END, ydke)
    save_button.state(["!disabled"])

def on_newdeck():
    global selected
    deckname = newdeck_entry.get().strip()
    result_text = output_text.get("1.0", END).strip()
    if deckname == "" or result_text == "":
        return
    newdeck_entry.delete(0, END)
    deckdata.append([deckname, result_text])
    enable_deck()
    selected = len(deckdata) - 1
    render_deck(selected, deckname)
    disable_deck()
    save_button.state(["!disabled"])
    save()

def on_deldeck():
    global selected
    deckdata.remove(deckdata[selected])
    render_all_decks()
    selected = None
    save_button.state(["disabled"])
    save()

def on_save_click():
    result_text = output_text.get("1.0", END).strip()
    if selected == None or result_text == "":
        return
    [name, _] = deckdata[selected]
    deckdata[selected] = [name, result_text]
    save()

# [[Name, YDKE]]
deckdata = []
try:
    with open(SAVE) as file:
        deckdata = json.load(file)
except:
    None
selected = None
deck_buttons = []
root = Tk()
root.title("YDKE生成")

# decks
decks = ttk.Frame(root, borderwidth=5)
decks.grid(column=0, row=0)

render_all_decks()

# deckmanager
deckmanager = ttk.Frame(root, borderwidth=5)
deckmanager.grid(column=0, row=1)

newdeck_entry = ttk.Entry(deckmanager)
newdeck_entry.grid(column=0, row=0, columnspan=2)

newdeck_button = ttk.Button(deckmanager, text="新建", command=on_newdeck)
newdeck_button.grid(column=0, row=1)

deldeck_button = ttk.Button(deckmanager, text="删除", command=on_deldeck)
deldeck_button.grid(column=1, row=1)

# converter
converter = ttk.Frame(root, borderwidth=5)
converter.grid(column=1, row=0)

text_input = Text(converter, height=20, width=80)
text_input.pack(padx=10, pady=10)

paste_button = ttk.Button(converter, text="粘贴并覆盖YDK", command=on_paste_click)
paste_button.pack(pady=5)

convert_button = ttk.Button(converter, text="转换到YDKE", command=on_convert_click)
convert_button.pack(pady=5)

output_text = Text(converter, height=5, width=80)
output_text.pack(padx=10, pady=10)

copy_button = ttk.Button(converter, text="复制YDKE", command=on_copy_click)
copy_button.pack(pady=5)

save_button = ttk.Button(converter, text="保存当前卡组更改", command=on_save_click)
save_button.pack(pady=5)
save_button.state(["disabled"])

root.resizable(FALSE, FALSE)
root.mainloop()
