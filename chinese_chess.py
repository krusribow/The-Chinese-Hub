import tkinter as tk
from tkinter import messagebox
import random

# --- ค่าคงที่สำหรับกระดาน ---
CELL_SIZE = 60
BOARD_COLS = 9
BOARD_ROWS = 10
MARGIN = 30
CANVAS_WIDTH = MARGIN * 2 + CELL_SIZE * (BOARD_COLS - 1)
CANVAS_HEIGHT = MARGIN * 2 + CELL_SIZE * (BOARD_ROWS - 1)

# --- ตัวอักษรจีนสำหรับชิ้นหมาก ---
piece_labels = {
    'G': {'red': '帥', 'black': '將'},
    'A': {'red': '仕', 'black': '士'},
    'E': {'red': '相', 'black': '象'},
    'H': {'red': '傌', 'black': '馬'},
    'R': {'red': '俥', 'black': '車'},
    'C': {'red': '炮', 'black': '砲'},
    'S': {'red': '兵', 'black': '卒'}
}

# --- ค่าของชิ้นสำหรับประเมิน AI ---
piece_value = {
    'G': 100, 'A': 20, 'E': 20, 'H': 30, 'R': 50, 'C': 40, 'S': 10
}

# --- Class สำหรับชิ้นหมาก ---
class Piece:
    def __init__(self, piece_type, color, pos):
        self.piece_type = piece_type  # 'G', 'A', 'E', 'H', 'R', 'C', 'S'
        self.color = color            # 'red' หรือ 'black'
        self.pos = pos                # (col, row)

# --- Class สำหรับกระดานเกม ---
class Board:
    def __init__(self):
        self.grid = {}  # เก็บชิ้นหมากโดยใช้ key เป็น (col, row)
        self.init_board()

    def init_board(self):
        # จัดวางชิ้นของฝ่ายดำ (ด้านบน)
        self.grid[(0, 0)] = Piece('R', 'black', (0, 0))
        self.grid[(8, 0)] = Piece('R', 'black', (8, 0))
        self.grid[(1, 0)] = Piece('H', 'black', (1, 0))
        self.grid[(7, 0)] = Piece('H', 'black', (7, 0))
        self.grid[(2, 0)] = Piece('E', 'black', (2, 0))
        self.grid[(6, 0)] = Piece('E', 'black', (6, 0))
        self.grid[(3, 0)] = Piece('A', 'black', (3, 0))
        self.grid[(5, 0)] = Piece('A', 'black', (5, 0))
        self.grid[(4, 0)] = Piece('G', 'black', (4, 0))
        self.grid[(1, 2)] = Piece('C', 'black', (1, 2))
        self.grid[(7, 2)] = Piece('C', 'black', (7, 2))
        for col in [0, 2, 4, 6, 8]:
            self.grid[(col, 3)] = Piece('S', 'black', (col, 3))

        # จัดวางชิ้นของฝ่ายแดง (ด้านล่าง)
        self.grid[(0, 9)] = Piece('R', 'red', (0, 9))
        self.grid[(8, 9)] = Piece('R', 'red', (8, 9))
        self.grid[(1, 9)] = Piece('H', 'red', (1, 9))
        self.grid[(7, 9)] = Piece('H', 'red', (7, 9))
        self.grid[(2, 9)] = Piece('E', 'red', (2, 9))
        self.grid[(6, 9)] = Piece('E', 'red', (6, 9))
        self.grid[(3, 9)] = Piece('A', 'red', (3, 9))
        self.grid[(5, 9)] = Piece('A', 'red', (5, 9))
        self.grid[(4, 9)] = Piece('G', 'red', (4, 9))
        self.grid[(1, 7)] = Piece('C', 'red', (1, 7))
        self.grid[(7, 7)] = Piece('C', 'red', (7, 7))
        for col in [0, 2, 4, 6, 8]:
            self.grid[(col, 6)] = Piece('S', 'red', (col, 6))

    def get_piece(self, pos):
        return self.grid.get(pos, None)

    def move_piece(self, start, end):
        """ย้ายชิ้นจาก start ไปยัง end (โดยไม่ตรวจสอบความถูกต้องอีกครั้ง)"""
        piece = self.get_piece(start)
        if piece:
            del self.grid[start]
            piece.pos = end
            self.grid[end] = piece

# --- ฟังก์ชันตรวจสอบการเดินของชิ้นแต่ละตัว ---
def is_valid_move(piece, start, end, board: Board):
    col, row = end
    # ตรวจสอบขอบกระดาน
    if col < 0 or col >= BOARD_COLS or row < 0 or row >= BOARD_ROWS:
        return False, "นอกขอบกระดาน"
    # ไม่ให้เดินทับชิ้นของตัวเอง
    target = board.get_piece(end)
    if target and target.color == piece.color:
        return False, "ไม่สามารถเดินทับชิ้นของตัวเองได้"

    dc = end[0] - start[0]
    dr = end[1] - start[1]
    abs_dc = abs(dc)
    abs_dr = abs(dr)

    if piece.piece_type == 'G':  # พระยา
        if (abs_dc + abs_dr) != 1:
            return False, "พระยาเดินทีละก้าวในแนวตั้งหรือแนวนอนเท่านั้น"
        if piece.color == 'red':
            if not (3 <= end[0] <= 5 and 7 <= end[1] <= 9):
                return False, "พระยาต้องอยู่ในวัง"
        else:
            if not (3 <= end[0] <= 5 and 0 <= end[1] <= 2):
                return False, "พระยาต้องอยู่ในวัง"

    elif piece.piece_type == 'A':  # ผู้ช่วย
        if abs_dc != 1 or abs_dr != 1:
            return False, "ผู้ช่วยเดินเฉียงทีละก้าว"
        if piece.color == 'red':
            if not (3 <= end[0] <= 5 and 7 <= end[1] <= 9):
                return False, "ผู้ช่วยต้องอยู่ในวัง"
        else:
            if not (3 <= end[0] <= 5 and 0 <= end[1] <= 2):
                return False, "ผู้ช่วยต้องอยู่ในวัง"

    elif piece.piece_type == 'E':  # ช้าง
        if abs_dc != 2 or abs_dr != 2:
            return False, "ช้างเดินเฉียง 2 ก้าว"
        mid = (start[0] + dc // 2, start[1] + dr // 2)
        if board.get_piece(mid) is not None:
            return False, "ช้างถูกบล็อก"
        if piece.color == 'red' and end[1] < 5:
            return False, "ช้างไม่สามารถข้ามแม่น้ำได้"
        if piece.color == 'black' and end[1] > 4:
            return False, "ช้างไม่สามารถข้ามแม่น้ำได้"

    elif piece.piece_type == 'H':  # ม้า
        if (abs_dc, abs_dr) not in [(1, 2), (2, 1)]:
            return False, "ม้าเดินเป็นรูป L"
        if abs_dc == 2:
            step = (start[0] + dc // 2, start[1])
            if board.get_piece(step) is not None:
                return False, "ม้าถูกบล็อกที่ขา"
        if abs_dr == 2:
            step = (start[0], start[1] + dr // 2)
            if board.get_piece(step) is not None:
                return False, "ม้าถูกบล็อกที่ขา"

    elif piece.piece_type == 'R':  # รถ
        if dc != 0 and dr != 0:
            return False, "รถต้องเดินตรง"
        if dc == 0:
            step = 1 if dr > 0 else -1
            for r in range(start[1] + step, end[1], step):
                if board.get_piece((start[0], r)) is not None:
                    return False, "มีชิ้นขวางทาง"
        if dr == 0:
            step = 1 if dc > 0 else -1
            for c in range(start[0] + step, end[0], step):
                if board.get_piece((c, start[1])) is not None:
                    return False, "มีชิ้นขวางทาง"

    elif piece.piece_type == 'C':  # กระสุน
        if dc != 0 and dr != 0:
            return False, "กระสุนต้องเดินตรง"
        count = 0
        if dc == 0:
            step = 1 if dr > 0 else -1
            for r in range(start[1] + step, end[1], step):
                if board.get_piece((start[0], r)) is not None:
                    count += 1
        if dr == 0:
            step = 1 if dc > 0 else -1
            for c in range(start[0] + step, end[0], step):
                if board.get_piece((c, start[1])) is not None:
                    count += 1
        target = board.get_piece(end)
        if target is None:
            if count != 0:
                return False, "กระสุนเดินไม่ได้เพราะมีชิ้นขวาง"
        else:
            if count != 1:
                return False, "กระสุนต้องมีสะพานเดียวในการจับคู่"

    elif piece.piece_type == 'S':  # ทหาร
        if piece.color == 'red':
            forward = -1
            crossed = start[1] <= 4  # เมื่อทหารแดงข้ามแม่น้ำ (row <= 4)
        else:
            forward = 1
            crossed = start[1] >= 5  # เมื่อทหารดำข้ามแม่น้ำ (row >= 5)
        if dr == forward and dc == 0:
            pass
        elif crossed and dr == 0 and abs_dc == 1:
            pass
        else:
            return False, "ทหารเดินได้เฉพาะไปข้างหน้า (และข้างเมื่อข้ามแม่น้ำแล้ว)"
    else:
        return False, "ชนิดชิ้นไม่รู้จัก"

    return True, ""

# --- ตรวจสอบกฎ "เห็นหน้ากัน" ของพระยา ---
def check_flying_general(board: Board):
    pos_red = None
    pos_black = None
    for pos, piece in board.grid.items():
        if piece.piece_type == 'G':
            if piece.color == 'red':
                pos_red = pos
            else:
                pos_black = pos
    if pos_red and pos_black and pos_red[0] == pos_black[0]:
        col = pos_red[0]
        start_row = min(pos_red[1], pos_black[1]) + 1
        end_row = max(pos_red[1], pos_black[1])
        for r in range(start_row, end_row):
            if board.get_piece((col, r)) is not None:
                return True
        return False
    return True

# --- ตรวจสอบการ "รุกฆาต" (ตรวจ General หายไป) ---
def check_game_over(board: Board):
    red_general = None
    black_general = None
    for piece in board.grid.values():
        if piece.piece_type == 'G':
            if piece.color == 'red':
                red_general = piece
            else:
                black_general = piece
    if not red_general:
        return True, 'black'
    if not black_general:
        return True, 'red'
    return False, None

# --- ฟังก์ชันตรวจสอบการเดินสำหรับ AI (simulation แล้ว revert) ---
def is_valid_ai_move(piece, start, end, board: Board):
    valid, msg = is_valid_move(piece, start, end, board)
    if not valid:
        return False
    captured = board.get_piece(end)
    board.move_piece(start, end)
    if not check_flying_general(board):
        board.move_piece(end, start)
        if captured:
            board.grid[end] = captured
        return False
    board.move_piece(end, start)
    if captured:
        board.grid[end] = captured
    return True

# --- Class จัดการเกมและส่วนติดต่อกราฟิก ---
class ChineseChessGame:
    def __init__(self, master, mode="PvP"):
        self.master = master
        self.mode = mode  # "PvP", "AI_Easy", "AI_Medium", "AI_Hard"
        self.board = Board()
        self.current_turn = 'red'  # ผู้เล่นสีแดงเริ่มก่อน (ในโหมด AI, คอมคือสีดำ)
        self.selected_piece_pos = None

        # สร้าง canvas สำหรับวาดกระดาน
        self.canvas = tk.Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="burlywood")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # เพิ่มปุ่ม "ยอมแพ้" สำหรับออกเกม
        self.resign_button = tk.Button(master, text="ยอมแพ้", font=("Arial", 14), command=self.resign_game)
        self.resign_button.pack(pady=10)

        self.draw_board()

    def resign_game(self):
        if messagebox.askyesno("ยอมแพ้", "คุณต้องการยอมแพ้และจบเกมหรือไม่?"):
            messagebox.showinfo("Game Over", f"{self.current_turn} ยอมแพ้! เกมจบแล้ว")
            self.master.destroy()

    def draw_board(self):
        self.canvas.delete("all")
        # วาดเส้นตารางแนวตั้ง
        for i in range(BOARD_COLS):
            x = MARGIN + i * CELL_SIZE
            self.canvas.create_line(x, MARGIN, x, MARGIN + CELL_SIZE * (BOARD_ROWS - 1))
        # วาดเส้นตารางแนวนอน
        for j in range(BOARD_ROWS):
            y = MARGIN + j * CELL_SIZE
            self.canvas.create_line(MARGIN, y, MARGIN + CELL_SIZE * (BOARD_COLS - 1), y)
        # วาดเส้นทแยงในวัง (สำหรับทั้งสองฝ่าย)
        # วังฝ่ายดำ: คอลัมน์ 3-5, แถว 0-2
        self.canvas.create_line(MARGIN+3*CELL_SIZE, MARGIN+0*CELL_SIZE,
                                MARGIN+5*CELL_SIZE, MARGIN+2*CELL_SIZE, dash=(4,2))
        self.canvas.create_line(MARGIN+5*CELL_SIZE, MARGIN+0*CELL_SIZE,
                                MARGIN+3*CELL_SIZE, MARGIN+2*CELL_SIZE, dash=(4,2))
        # วังฝ่ายแดง: คอลัมน์ 3-5, แถว 7-9
        self.canvas.create_line(MARGIN+3*CELL_SIZE, MARGIN+7*CELL_SIZE,
                                MARGIN+5*CELL_SIZE, MARGIN+9*CELL_SIZE, dash=(4,2))
        self.canvas.create_line(MARGIN+5*CELL_SIZE, MARGIN+7*CELL_SIZE,
                                MARGIN+3*CELL_SIZE, MARGIN+9*CELL_SIZE, dash=(4,2))
        # วาดชิ้นหมาก
        for pos, piece in self.board.grid.items():
            self.draw_piece(piece)

    def draw_piece(self, piece):
        col, row = piece.pos
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        radius = CELL_SIZE // 2 - 5
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="white")
        label = piece_labels.get(piece.piece_type, {}).get(piece.color, piece.piece_type)
        fill_color = "red" if piece.color == "red" else "black"
        self.canvas.create_text(x, y, text=label, fill=fill_color, font=("Arial", 20, "bold"))

    def on_canvas_click(self, event):
        col = round((event.x - MARGIN) / CELL_SIZE)
        row = round((event.y - MARGIN) / CELL_SIZE)
        if col < 0 or col >= BOARD_COLS or row < 0 or row >= BOARD_ROWS:
            return
        pos = (col, row)
        piece = self.board.get_piece(pos)
        if self.selected_piece_pos:
            from_pos = self.selected_piece_pos
            moving_piece = self.board.get_piece(from_pos)
            if moving_piece and moving_piece.color == self.current_turn:
                valid, msg = is_valid_move(moving_piece, from_pos, pos, self.board)
                if not valid:
                    messagebox.showwarning("การเดินผิดกติกา", msg)
                    self.selected_piece_pos = None
                    self.draw_board()
                    return
                # จับชิ้น (ถ้ามี) และย้ายชิ้น
                captured = self.board.get_piece(pos)
                self.board.move_piece(from_pos, pos)
                if not check_flying_general(self.board):
                    # ถ้าเดินแล้วทำให้ General "เห็นหน้ากัน" ให้ย้อนกลับ
                    self.board.move_piece(pos, from_pos)
                    if captured:
                        self.board.grid[pos] = captured
                    messagebox.showwarning("การเดินผิดกติกา", "พระยาไม่ควรเห็นกันโดยไม่มีชิ้นคั่น!")
                    self.selected_piece_pos = None
                    self.draw_board()
                    return

                # ตรวจสอบ "รุกฆาต" หลังการเดิน
                game_over, winner = check_game_over(self.board)
                if game_over:
                    messagebox.showinfo("Game Over", f"{winner} รุกฆาตฝ่ายตรงข้าม! เกมจบแล้ว")
                    self.master.destroy()
                    return

                # สลับเทิร์น
                self.current_turn = 'black' if self.current_turn == 'red' else 'red'
                self.draw_board()
                self.selected_piece_pos = None

                # หากโหมดเป็น AI และถึงตาคอม (สีดำ) ให้ AI เดิน
                if self.mode != "PvP" and self.current_turn == 'black':
                    self.master.after(500, self.ai_move)
            else:
                messagebox.showinfo("แจ้งเตือน", "โปรดเลือกชิ้นที่คุณควบคุม")
                self.selected_piece_pos = None
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece_pos = pos
            else:
                messagebox.showinfo("แจ้งเตือน", "โปรดเลือกชิ้นที่คุณควบคุม")

    def get_all_valid_moves(self, color):
        moves = []
        # ค้นหาการเดินที่ถูกต้องสำหรับทุกชิ้นของสีที่กำหนด
        for pos, piece in list(self.board.grid.items()):
            if piece.color == color:
                for col in range(BOARD_COLS):
                    for row in range(BOARD_ROWS):
                        target = (col, row)
                        if is_valid_ai_move(piece, pos, target, self.board):
                            captured = self.board.get_piece(target)
                            value = piece_value[captured.piece_type] if captured else 0
                            moves.append((pos, target, value))
        return moves

    def ai_move(self):
        moves = self.get_all_valid_moves(self.current_turn)
        if not moves:
            messagebox.showinfo("Game Over", "AI ไม่มีการเดินที่ถูกต้อง! เกมจบแล้ว")
            self.master.destroy()
            return
        chosen_move = None
        if self.mode == "AI_Easy":
            chosen_move = random.choice(moves)
        elif self.mode == "AI_Medium":
            capture_moves = [m for m in moves if m[2] > 0]
            chosen_move = random.choice(capture_moves) if capture_moves else random.choice(moves)
        elif self.mode == "AI_Hard":
            capture_moves = [m for m in moves if m[2] > 0]
            chosen_move = max(capture_moves, key=lambda x: x[2]) if capture_moves else random.choice(moves)
        if chosen_move:
            from_pos, to_pos, _ = chosen_move
            captured = self.board.get_piece(to_pos)
            self.board.move_piece(from_pos, to_pos)
            if not check_flying_general(self.board):
                self.board.move_piece(to_pos, from_pos)
                if captured:
                    self.board.grid[to_pos] = captured
                messagebox.showwarning("AI เดินผิดกติกา", "การเดินทำให้พระยาเห็นกัน!")
                return
            # ตรวจสอบ "รุกฆาต" หลังการเดินของ AI
            game_over, winner = check_game_over(self.board)
            if game_over:
                messagebox.showinfo("Game Over", f"{winner} รุกฆาตฝ่ายตรงข้าม! เกมจบแล้ว")
                self.master.destroy()
                return
            self.current_turn = 'red'
            self.draw_board()

# --- เมนูหลักสำหรับเลือกโหมดการเล่น ---
def start_game(mode):
    game_window = tk.Toplevel()
    if mode == "PvP":
        game_window.title("เซียงชี่ - แข่งหนึ่งต่อหนึ่ง")
    elif mode == "AI_Easy":
        game_window.title("เซียงชี่ - เล่นกับคอม (ง่าย)")
    elif mode == "AI_Medium":
        game_window.title("เซียงชี่ - เล่นกับคอม (ปานกลาง)")
    elif mode == "AI_Hard":
        game_window.title("เซียงชี่ - เล่นกับคอม (ยาก)")
    ChineseChessGame(game_window, mode=mode)

def main_menu():
    root = tk.Tk()
    root.title("เมนูหลัก - เซียงชี่")
    label = tk.Label(root, text="เลือกโหมดการเล่น", font=("Arial", 18))
    label.pack(pady=10)
    btn_pvp = tk.Button(root, text="แข่งหนึ่งต่อหนึ่ง", font=("Arial", 14),
                        command=lambda: start_game("PvP"))
    btn_easy = tk.Button(root, text="เล่นกับคอม (ง่าย)", font=("Arial", 14),
                         command=lambda: start_game("AI_Easy"))
    btn_medium = tk.Button(root, text="เล่นกับคอม (ปานกลาง)", font=("Arial", 14),
                           command=lambda: start_game("AI_Medium"))
    btn_hard = tk.Button(root, text="เล่นกับคอม (ยาก)", font=("Arial", 14),
                         command=lambda: start_game("AI_Hard"))
    btn_pvp.pack(pady=5)
    btn_easy.pack(pady=5)
    btn_medium.pack(pady=5)
    btn_hard.pack(pady=5)
    root.mainloop()

if __name__ == "__main__":
    main_menu()
