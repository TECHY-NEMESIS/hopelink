import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
import re

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "hopelink"
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def analyze_emotion(msg):
    msg = msg.lower()

    sad_words = [
        'sad','lonely','depressed','hopeless','anxious','suicidal','worthless','empty',
        'tired','stressed','broken','crying','hurt','pain','fear','scared','panic',
        'devastated','lost','overwhelmed','anxiety','panic','life sucks','i can’t anymore',
        'i cant anymore','kill myself','end it','overthinking','done with life'
    ]

    happy_words = [
        'happy','joy','good','great','awesome','fantastic','wonderful','nice','fine',
        'feeling better','positive','excited','motivated','cheerful','thrilled'
    ]

    sad_score = sum(1 for w in sad_words if w in msg)
    happy_score = sum(1 for w in happy_words if w in msg)

    if happy_score >= 1 and sad_score == 0:
        return "happy"
    elif sad_score >= 3:
        return "high"
    elif sad_score >= 1:
        return "LOW"
    else:
        return "neutral"

root = tk.Tk()
root.title("HopeLink")
root.geometry("720x520")
current_user = None

main_frame = tk.Frame(root)
register_frame = tk.Frame(root)
user_frame = tk.Frame(root)
volunteer_frame = tk.Frame(root)
chat_window = None

for f in (main_frame, register_frame, user_frame, volunteer_frame):
    f.place(relwidth=1, relheight=1)

def show_frame(frame):
    frame.tkraise()

def open_register():
    show_frame(register_frame)

def open_login():
    login_window()

tk.Label(main_frame, text="HopeLink", font=("Arial", 28, "bold")).pack(pady=20)
tk.Button(main_frame, text="Register", width=20, command=open_register).pack(pady=8)
tk.Button(main_frame, text="Login", width=20, command=open_login).pack(pady=8)
tk.Button(main_frame, text="Exit", width=20, command=root.destroy).pack(pady=8)

tk.Label(register_frame, text="Register", font=("Arial", 20, "bold")).pack(pady=12)
tk.Label(register_frame, text="Name").pack()
reg_name = tk.Entry(register_frame)
reg_name.pack(pady=4)
role_var = tk.StringVar(value="user")
tk.Radiobutton(register_frame, text="User", variable=role_var, value="user").pack()
tk.Radiobutton(register_frame, text="Volunteer", variable=role_var, value="volunteer").pack()

def register_user():
    name = reg_name.get().strip()
    role = role_var.get()
    if not name:
        messagebox.showwarning("Input Error", "Please enter a name.")
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, role) VALUES (%s,%s)", (name, role))
    conn.commit()
    uid = cur.lastrowid
    cur.close()
    conn.close()
    messagebox.showinfo("Success", f"Registered as {role}! Your ID: {uid}")
    reg_name.delete(0, tk.END)
    show_frame(main_frame)

tk.Button(register_frame, text="Submit", command=register_user).pack(pady=8)
tk.Button(register_frame, text="Back", command=lambda: show_frame(main_frame)).pack()

def login_window():
    win = tk.Toplevel(root)
    win.title("Login")
    win.geometry("320x180")
    tk.Label(win, text="Enter User ID").pack(pady=6)
    uid_entry = tk.Entry(win)
    uid_entry.pack(pady=6)
    def do_login():
        uid_text = uid_entry.get().strip()
        if not uid_text.isdigit():
            messagebox.showerror("Error", "ID must be numeric.")
            return
        uid = int(uid_text)
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        u = cur.fetchone()
        cur.close()
        conn.close()
        if not u:
            messagebox.showerror("Error", "User not found.")
            return
        global current_user
        current_user = u
        messagebox.showinfo("Welcome", f"Hello {u['username']} ({u['role']})")
        win.destroy()
        if u['role'] == 'user':
            load_user_dashboard()
            show_frame(user_frame)
        else:
            load_volunteer_dashboard()
            show_frame(volunteer_frame)
    tk.Button(win, text="Login", command=do_login).pack(pady=8)

tk.Label(user_frame, text="User Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
sos_text = scrolledtext.ScrolledText(user_frame, height=6, width=70)
sos_text.pack(pady=8)
tk.Button(user_frame, text="Post SOS", command=lambda: post_sos()).pack(pady=4)
tk.Button(user_frame, text="My SOS (View/Open Chat)", command=lambda: view_my_sos()).pack(pady=4)
tk.Button(user_frame, text="Logout", command=lambda: logout_to_main()).pack(pady=6)

def post_sos():
    msg = sos_text.get("1.0", tk.END).strip()
    if not msg:
        messagebox.showwarning("Error", "Message cannot be empty.")
        return
    emotion = analyze_emotion(msg)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO sos_posts (user_id,message,emotion_level,is_claimed) VALUES (%s,%s,%s,%s)",
                (current_user['user_id'], msg, emotion, False))
    conn.commit()
    cur.close()
    conn.close()
    sos_text.delete("1.0", tk.END)
    messagebox.showinfo("Posted", f"SOS posted with {emotion} emotion level!")

def view_my_sos():
    win = tk.Toplevel(root)
    win.title("My SOS Posts")
    win.geometry("640x360")
    listbox = tk.Listbox(win, width=100, height=15)
    listbox.pack(pady=8)
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM sos_posts WHERE user_id = %s ORDER BY timestamp DESC", (current_user['user_id'],))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        status = "Claimed" if r['is_claimed'] else "Open"
        display = f"ID:{r['sos_id']} | {status} | {r['emotion_level']} | {r['timestamp']} | {r['message'][:80]}"
        listbox.insert(tk.END, display)
    def open_chat_for_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select a post to open chat.")
            return
        text = listbox.get(sel[0])
        sos_id = int(text.split('|')[0].split(':')[1].strip())
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM sos_posts WHERE sos_id = %s", (sos_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row['is_claimed']:
            messagebox.showinfo("Not Claimed", "Your post is not claimed yet.")
            return
        open_chat_window_for(sos_id, current_user['user_id'], row['claimed_by'], 'user')
    tk.Button(win, text="Open Chat", command=open_chat_for_selected).pack(pady=6)

tk.Label(volunteer_frame, text="Volunteer Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
vol_sos_list = tk.Listbox(volunteer_frame, width=100, height=15)
vol_sos_list.pack(pady=8)
tk.Button(volunteer_frame, text="Refresh", command=lambda: load_volunteer_dashboard()).pack(pady=4)
tk.Button(volunteer_frame, text="Claim Selected SOS and Open Chat", command=lambda: claim_selected_and_chat()).pack(pady=4)
tk.Button(volunteer_frame, text="Logout", command=lambda: logout_to_main()).pack(pady=6)

def load_user_dashboard():
    sos_text.delete("1.0", tk.END)

def load_volunteer_dashboard():
    vol_sos_list.delete(0, tk.END)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT sos_id,user_id,message,emotion_level,timestamp FROM sos_posts WHERE is_claimed=FALSE ORDER BY CASE emotion_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, timestamp ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        display = f"ID:{r[0]} | User:{r[1]} | {r[3]} | {r[4]} | {r[2][:80]}"
        vol_sos_list.insert(tk.END, display)

def claim_selected_and_chat():
    sel = vol_sos_list.curselection()
    if not sel:
        messagebox.showwarning("Select", "Select an SOS to claim.")
        return
    text = vol_sos_list.get(sel[0])
    sos_id = int(text.split('|')[0].split(':')[1].strip())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE sos_posts SET is_claimed=TRUE, claimed_by=%s WHERE sos_id=%s", (current_user['user_id'], sos_id))
    conn.commit()
    cur.close()
    conn.close()
    conn2 = get_conn()
    cur2 = conn2.cursor(dictionary=True)
    cur2.execute("SELECT user_id FROM sos_posts WHERE sos_id = %s", (sos_id,))
    row = cur2.fetchone()
    cur2.close()
    conn2.close()
    open_chat_window_for(sos_id, row['user_id'], current_user['user_id'], 'volunteer')
    load_volunteer_dashboard()

def open_chat_window_for(sos_id, user_id, volunteer_id, role):
    global chat_window
    if chat_window and tk.Toplevel.winfo_exists(chat_window):
        try:
            chat_window.destroy()
        except:
            pass
    chat_window = tk.Toplevel(root)
    chat_window.title(f"Chat SOS{sos_id}")
    chat_window.geometry("640x480")
    chat_area = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD, width=80, height=20)
    chat_area.pack(padx=8, pady=8)
    chat_area.config(state="disabled")
    entry_msg = tk.Entry(chat_window, width=60)
    entry_msg.pack(side=tk.LEFT, padx=8, pady=6)
    if role == 'user':
        sender_alias = f"User#{user_id}"
        sender_role = 'user'
        other_alias = f"Volunteer#{volunteer_id}"
    else:
        sender_alias = f"Volunteer#{volunteer_id}"
        sender_role = 'volunteer'
        other_alias = f"User#{user_id}"
    chat_id = f"SOS{sos_id}_U{user_id}_V{volunteer_id}"
    def load_history():
        chat_area.config(state="normal")
        chat_area.delete("1.0", tk.END)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT sender_alias, sender_role, message, timestamp FROM messages WHERE chat_id = %s ORDER BY timestamp ASC", (chat_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for r in rows:
            chat_area.insert(tk.END, f"[{r[3]}] {r[0]} ({r[1]}): {r[2]}\n")
        chat_area.config(state="disabled")
    def send_message_chat():
        msg = entry_msg.get().strip()
        if not msg:
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (chat_id, sender_role, sender_alias, message) VALUES (%s, %s, %s, %s)", (chat_id, sender_role, sender_alias, msg))
        conn.commit()
        cur.close()
        conn.close()
        entry_msg.delete(0, tk.END)
        load_history()
    tk.Button(chat_window, text="Send", command=send_message_chat).pack(side=tk.LEFT, padx=4)
    tk.Button(chat_window, text="Refresh", command=load_history).pack(side=tk.LEFT, padx=4)
    load_history()

def logout_to_main():
    global current_user
    current_user = None
    show_frame(main_frame)

show_frame(main_frame)
root.mainloop()
