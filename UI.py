import tkinter as tk
from tkinter import ttk, messagebox
import json
import ftcOPRMethods as opr

# ── Data store ──────────────────────────────────────────────────────────────
scouting_data: dict[tuple, tuple] = {}

# ── Color palette ────────────────────────────────────────────────────────────
BG        = "#0d1117"
PANEL     = "#161b22"
BORDER    = "#30363d"
ACCENT    = "#f78166"
ACCENT2   = "#79c0ff"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"
SUCCESS   = "#3fb950"
INPUT_BG  = "#21262d"

# ── Root window ──────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("FTC Scouting Tool")
root.configure(bg=BG)
root.resizable(False, False)

# Center on screen
W, H = 680, 700
root.geometry(f"{W}x{H}+{(root.winfo_screenwidth()-W)//2}+{(root.winfo_screenheight()-H)//2}")

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Helvetica", 18, "bold")
FONT_LABEL  = ("Helvetica", 10, "bold")
FONT_SMALL  = ("Helvetica", 9)
FONT_INPUT  = ("Helvetica", 12)
FONT_MONO   = ("Helvetica", 9)
FONT_BTN    = ("Helvetica", 10, "bold")

# ── Helper: styled spinbox ────────────────────────────────────────────────────
def make_spinbox(parent, var):
    sb = tk.Spinbox(
        parent, textvariable=var, from_=0, to=999, width=6,
        font=FONT_INPUT, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
        buttonbackground=BORDER, relief="flat", bd=0,
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT2,
    )
    return sb

def make_counter(parent, var, min_val=0, max_val=999):
    """Returns a [−] [value] [+] button group as an alternative to a spinbox."""
    frame = tk.Frame(parent, bg=PANEL)
 
    btn_base = dict(
        font=("Courier New", 12, "bold"),
        relief="flat", bd=0, cursor="hand2", width=2, pady=1, fg=TEXT,
    )
 
    def decrement():
        if var.get() > min_val:
            var.set(var.get() - 1)
 
    def increment():
        if var.get() < max_val:
            var.set(var.get() + 1)
 
    tk.Button(frame, text="−", command=decrement,
              bg="#81362e", activebackground="#be4234", activeforeground=TEXT,
              **btn_base).pack(side="left")
    tk.Label(
        frame, textvariable=var, width=4,
        font=FONT_INPUT, bg=INPUT_BG, fg=TEXT,
        highlightthickness=1, highlightbackground=BORDER,
        anchor="center",
    ).pack(side="left", padx=2)
    tk.Button(frame, text="+", command=increment,
              bg="#356d2f", activebackground="#31b349", activeforeground=TEXT,
              **btn_base).pack(side="left")
 
    return frame

def make_entry(parent, var, width=8):
    e = tk.Entry(
        parent, textvariable=var, width=width,
        font=FONT_INPUT, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
        relief="flat", bd=0,
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT2,
    )
    return e

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=24, pady=(20, 4))

tk.Label(header, text="⬡ FTC SCOUTING TOOL", font=FONT_TITLE,
         bg=BG, fg=ACCENT).pack(side="left")

counter_var = tk.StringVar(value="0 entries")
tk.Label(header, textvariable=counter_var, font=FONT_SMALL,
         bg=BG, fg=MUTED).pack(side="right", pady=6)

tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=24, pady=4)

# ── Input panel ───────────────────────────────────────────────────────────────
form_frame = tk.Frame(root, bg=PANEL, highlightthickness=1,
                      highlightbackground=BORDER)
form_frame.pack(fill="x", padx=24, pady=10)

tk.Label(form_frame, text="MATCH ENTRY", font=FONT_LABEL,
         bg=PANEL, fg=ACCENT2).grid(row=0, column=0, columnspan=4,
                                     sticky="w", padx=16, pady=(12, 6))

# Row 1 — Team & Match
v_team  = tk.IntVar(value=0)
v_match = tk.IntVar(value=1)
v_event = tk.StringVar(value="")

tk.Label(form_frame, text="TEAM #", font=FONT_LABEL, bg=PANEL, fg=MUTED
         ).grid(row=1, column=0, sticky="w", padx=(16, 4), pady=4)
make_spinbox(form_frame, v_team).grid(row=1, column=1, sticky="w",
                                      padx=(0, 24), pady=4)

tk.Label(form_frame, text="MATCH #", font=FONT_LABEL, bg=PANEL, fg=MUTED
         ).grid(row=1, column=2, sticky="w", padx=(0, 4), pady=4)
make_spinbox(form_frame, v_match).grid(row=1, column=3, sticky="w",
                                        padx=(0, 16), pady=4)

tk.Label(form_frame, text="EVENT KEY", font=FONT_LABEL, bg=PANEL, fg=MUTED
         ).grid(row=1, column=4, sticky="w", padx=(0, 4), pady=4)
make_entry(form_frame, v_event).grid(row=1, column=5, sticky="w",
                                        padx=(0, 16), pady=4)

# Divider
tk.Frame(form_frame, bg=BORDER, height=1).grid(
    row=2, column=0, columnspan=4, sticky="ew", padx=16, pady=6)

# Section labels row
for col, label, color in [(0, "AUTO", ACCENT), (2, "DRIVER CONTROLLED", SUCCESS)]:
    tk.Label(form_frame, text=label, font=FONT_LABEL, bg=PANEL, fg=color
             ).grid(row=3, column=col, columnspan=2, sticky="w",
                    padx=(16 if col == 0 else 0, 0), pady=2)

# Score inputs
v_auto_sample_data  = tk.IntVar(value=0)
v_auto_spec_data  = tk.IntVar(value=0)
v_dc_sample_data    = tk.IntVar(value=0)
v_dc_spec_data    = tk.IntVar(value=0)

fields = [
    ("Basket Count",  v_auto_sample_data,  4, 0),
    ("Clip Count",  v_auto_spec_data,  5, 0),
    ("Basket Count",   v_dc_sample_data,  4, 2),
    ("Clip Count",   v_dc_spec_data,  5, 2),
]

for lbl, var, row, col in fields:
    tk.Label(form_frame, text=lbl, font=FONT_LABEL, bg=PANEL, fg=MUTED
             ).grid(row=row, column=col, sticky="w",
                    padx=(16 if col == 0 else 0, 4), pady=4)
    make_counter(form_frame, var).grid(row=row, column=col+1, sticky="w",
                                        padx=(0, 24 if col == 0 else 16), pady=4)

# ── Buttons ───────────────────────────────────────────────────────────────────
def update_counter():
    counter_var.set(f"{len(scouting_data)} entr{'y' if len(scouting_data)==1 else 'ies'}")

def add_entry():
    try:
        team = int(v_team.get())
    except (ValueError, tk.TclError):
        messagebox.showwarning("Missing Field", "Please enter a valid Team number.", parent=root)
        return
    if team <= 0:
        messagebox.showwarning("Missing Field", "Team number must be greater than 0.", parent=root)
        return
    match = v_match.get()
    key   = (team, match)
    val   = (v_auto_sample_data.get(), v_auto_spec_data.get(), v_dc_sample_data.get(), v_dc_spec_data.get())
    scouting_data[key] = val
    refresh_table()
    update_counter()
    status_var.set(f"✓  Added entry for Team {team}, Match {match}")
    # Reset scores and team
    for v in (v_auto_sample_data, v_dc_sample_data, v_auto_spec_data, v_dc_spec_data):
        v.set(0)
    v_team.set(0)
    v_match.set(match + 1)

def clear_all():
    if not scouting_data:
        return
    if messagebox.askyesno("Clear All", "Delete all scouting entries?", parent=root):
        scouting_data.clear()
        refresh_table()
        update_counter()
        status_var.set("All entries cleared.")

def copy_dict():
    if not scouting_data:
        messagebox.showinfo("Nothing to copy", "No entries yet.", parent=root)
        return
    root.clipboard_clear()
    root.clipboard_append(repr(scouting_data))
    status_var.set("✓  Dict copied to clipboard!")

def show_json():
    if not scouting_data:
        messagebox.showinfo("Empty", "No entries yet.", parent=root)
        return
    # Convert tuple keys/values to strings for JSON
    out = {str(k): list(v) for k, v in scouting_data.items()}
    win = tk.Toplevel(root)
    win.title("Raw Dict Output")
    win.configure(bg=BG)
    win.resizable(True, True)
    txt = tk.Text(win, font=FONT_MONO, bg=INPUT_BG, fg=TEXT,
                  insertbackground=TEXT, relief="flat", bd=0,
                  highlightthickness=0, wrap="none", width=70, height=20)
    txt.pack(padx=16, pady=16, fill="both", expand=True)
    txt.insert("1.0", repr(scouting_data))
    txt.configure(state="disabled")

btn_row = tk.Frame(root, bg=BG)
btn_row.pack(fill="x", padx=24, pady=6)

btn_cfg = dict(font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
               padx=14, pady=6)

tk.Button(btn_row, text="＋  ADD ENTRY", bg=ACCENT, fg=BG,
          command=add_entry, **btn_cfg).pack(side="left", padx=(0, 8))
tk.Button(btn_row, text="⎘  COPY DICT", bg=ACCENT2, fg=BG,
          command=copy_dict, **btn_cfg).pack(side="left", padx=(0, 8))
tk.Button(btn_row, text="⊞  VIEW DICT", bg=INPUT_BG, fg=TEXT,
          command=show_json, **btn_cfg).pack(side="left", padx=(0, 8))
tk.Button(btn_row, text="✕  CLEAR ALL", bg=BORDER, fg=MUTED,
          command=clear_all, **btn_cfg).pack(side="right")

# ── Status bar ────────────────────────────────────────────────────────────────
status_var = tk.StringVar(value="Ready — enter match data above.")
tk.Label(root, textvariable=status_var, font=FONT_SMALL,
         bg=BG, fg=MUTED, anchor="w").pack(fill="x", padx=26, pady=(0, 4))

tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=24, pady=2)

# ── Results table ─────────────────────────────────────────────────────────────
tbl_header = tk.Frame(root, bg=BG)
tbl_header.pack(fill="x", padx=24, pady=(8, 2))
tk.Label(tbl_header, text="RECORDED ENTRIES", font=FONT_LABEL,
         bg=BG, fg=ACCENT2).pack(side="left")

cols = ("Team", "Match", "Auto Basket", "Auto Clip", "DC Basket", "DC Clip")

style = ttk.Style()
style.theme_use("clam")
style.configure("Scout.Treeview",
    background=INPUT_BG, fieldbackground=INPUT_BG,
    foreground=TEXT, rowheight=26,
    font=FONT_MONO, borderwidth=0)
style.configure("Scout.Treeview.Heading",
    background=PANEL, foreground=ACCENT2,
    font=FONT_LABEL, relief="flat", borderwidth=0)
style.map("Scout.Treeview",
    background=[("selected", BORDER)],
    foreground=[("selected", TEXT)])

tree_frame = tk.Frame(root, bg=BG)
tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                    style="Scout.Treeview",
                    yscrollcommand=scrollbar.set, height=8)
scrollbar.configure(command=tree.yview)

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=90, anchor="center", stretch=True)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def refresh_table():
    tree.delete(*tree.get_children())
    for (team, match), (asam, aspe, dcsam, dcspe) in scouting_data.items():
        tree.insert("", "end", values=(team, match, asam, aspe, dcsam, dcspe))

# ── Delete selected row ───────────────────────────────────────────────────────
def delete_selected(event=None):
    sel = tree.selection()
    if not sel:
        return
    for item in sel:
        vals = tree.item(item, "values")
        key = (vals[0], int(vals[1]))
        scouting_data.pop(key, None)
    refresh_table()
    update_counter()
    status_var.set("Entry deleted.")

tree.bind("<Delete>", delete_selected)
tree.bind("<BackSpace>", delete_selected)

# ── Keyboard shortcut: Enter to add ──────────────────────────────────────────
root.bind("<Return>", lambda e: add_entry())

root.mainloop()

# ── After window closes — print the dict ─────────────────────────────────────
print("\n=== Scouting Data ===")
print(scouting_data)
opr.event_key = f"2024/{v_event.get()}"
opr.add_data(scouting_data)