import pyxel
import time
import random
from decimal import Decimal
import tetromino


class App:

    # 1ブロックのサイズ
    BLOCK_SIZE = 16

    # テトロミノのサイズ
    TETRO_SIZE = 4

    # フィールドの行列を定義
    FIELD_COL = 10
    FIELD_ROW = 20

    # 描画するスクリーンのサイズ
    SCREEN_W = BLOCK_SIZE * FIELD_COL
    SCREEN_H = BLOCK_SIZE * FIELD_ROW

    # ネクストのサイズ
    NEXT_FIELD = BLOCK_SIZE * 6

    def __init__(self):
        pyxel.init(self.SCREEN_W+self.NEXT_FIELD, self.SCREEN_H, title="Among Us Tetris")
        pyxel.load("tetris.pyxres")

        # テトロミノを初期化
        self.next_tetros = []
        self.hold_tetro = 0
        self.hold_flag = True
        self.tetro_init()

        # テトロミノが落ちてくるスピード (秒)
        self.tetro_fall_speed = 0.7

        # フィールドの配列を初期化
        self.field = []
        for y in range(self.FIELD_ROW):
            self.field.append([])
            for x in range(self.FIELD_COL):
                self.field[y].append([])
                self.field[y][x] = 0

        # タイマーを初期化
        self.start = time.time()

        # スコア
        self.score = 0
        self.linec = 0

        # ゲームオーバー判定
        self.gameover = False

        pyxel.run(self.update, self.draw)

    # テトロミノの初期化
    def tetro_init(self):
        # nexy_tetros配列が空なら代入する
        if len(self.next_tetros) <= 1:
            lst = list(range(0,7))
            rnd_lst = random.sample(lst, len(lst))
            self.next_tetros += rnd_lst

        self.tetro_randi = self.next_tetros[0]
        self.tetro_x = int(self.FIELD_COL/2 - self.TETRO_SIZE/2)
        self.tetro_y = 0
        self.tetro_col = tetromino.TETRO_COLORS[self.tetro_randi]
        self.tetro = tetromino.TETRO_TYPES[self.tetro_randi]
        self.next_tetros.pop(0)
        self.hold_flag = True

    # ホールド処理
    def hold_tetro_click(self):
        # hold_tetroが空の場合
        if not self.hold_tetro:
            if self.hold_flag:
                self.hold_tetro = self.tetro_randi + 1
                self.tetro_init()
                self.hold_flag = False
        else:
            if self.hold_flag:
                # tetroの値を保存
                now_tetro = self.tetro_randi
                # holdに入っている情報をtetroに与える
                self.tetro_randi = self.hold_tetro-1
                self.tetro_x = int(self.FIELD_COL/2 - self.TETRO_SIZE/2)
                self.tetro_y = 0
                self.tetro_col = tetromino.TETRO_COLORS[self.hold_tetro-1]
                self.tetro = tetromino.TETRO_TYPES[self.hold_tetro-1]
                self.hold_flag = False
                # now_tetroに入っている情報をholdに与える
                self.hold_tetro = now_tetro + 1

    # テトロミノの描画
    def draw_tetro(self):
        # テトロミノの着地点を計算
        plus = 0
        while self.check_move(0,plus+1):
            plus += 1

        for y in range(self.TETRO_SIZE):
            for x in range(self.TETRO_SIZE):
                if self.tetro[y][x]:
                    self.draw_block(self.tetro_x+x, self.tetro_y+y+plus, 7)
                    self.draw_block(self.tetro_x+x, self.tetro_y+y, self.tetro_randi) # 本体

    # フィールドの描画
    def draw_field(self):
        for y in range(self.FIELD_ROW):
            for x in range(self.FIELD_COL):
                if self.field[y][x]:
                    self.draw_block(x, y, self.field[y][x]-1)
        pyxel.rectb(0, 0, self.SCREEN_W, self.SCREEN_H, 13) # 背景を表示

    # ネクストの描画
    def draw_sidebar(self):
        # NEXTを表示
        pyxel.text(self.SCREEN_W+5, 5, "NEXT", 7)
        # ネクストのテトロミノを表示
        if len(self.next_tetros) > 0:
            next_tetro = tetromino.TETRO_TYPES[self.next_tetros[0]]
            for y in range(self.TETRO_SIZE):
                for x in range(self.TETRO_SIZE):
                    if next_tetro[y][x]:
                        self.draw_block(11+x, 1+y, self.next_tetros[0])

        # HOLDを表示
        pyxel.text(self.SCREEN_W+5, 80, "HOLD", 7)
        # ホールドされているテトロミノを表示
        if not self.hold_tetro == 0:
            for y in range(self.TETRO_SIZE):
                draw_htetro = tetromino.TETRO_TYPES[self.hold_tetro-1]
                for x in range(self.TETRO_SIZE):
                    if draw_htetro[y][x]:
                        self.draw_block(11+x, 6+y, self.hold_tetro-1)

        # スコアを表示
        pyxel.text(self.SCREEN_W+5, 160, "SCORE: "+str(self.score), 7)

    # 1ブロックを描画する関数
    def draw_block(self, x, y, c):
        px = x * self.BLOCK_SIZE
        py = y * self.BLOCK_SIZE
        pyxel.blt(px, py, 0, tetromino.TETRO_COLORS[c][0], tetromino.TETRO_COLORS[c][1], self.BLOCK_SIZE, self.BLOCK_SIZE, colkey=15)

    # テトロミノの移動チェック
    def check_move(self, mx, my, ntetro=0):
        if ntetro == 0: ntetro = self.tetro
        for y in range(self.TETRO_SIZE):
            for x in range(self.TETRO_SIZE):
                nx = self.tetro_x + mx + x
                ny = self.tetro_y + my + y
                if ntetro[y][x]:
                    if  ny < 0 or nx < 0 or ny >= self.FIELD_ROW or nx >= self.FIELD_COL or self.field[ny][nx]:
                        return False

        return True

    # テトロミノの回転
    def tetro_rotate(self):
        ntetro = []
        for y in range(self.TETRO_SIZE):
            ntetro.append([])
            for x in range(self.TETRO_SIZE):
                ntetro[y].append([])
                ntetro[y][x] = self.tetro[self.TETRO_SIZE-x-1][y]
        return ntetro

    # テトロミノを固定
    def tetro_fix(self):
        for y in range(self.TETRO_SIZE):
            for x in range(self.TETRO_SIZE):
                if self.tetro[y][x]:
                    self.field[self.tetro_y + y][self.tetro_x + x] = self.tetro_randi+1

    # 全てのラインが埋まっている部分を消す
    def check_line(self):
        for y in range(self.FIELD_ROW):
            flag = True
            for x in range(self.FIELD_COL):
                if self.field[y][x] == 0:
                    flag = False
                    break
            if flag:
                # ラインを消す処理と,スコアを加算する処理
                self.linec += 1
                self.score = self.linec*100
                if self.linec % 10 == 0:
                    self.tetro_fall_speed = Decimal(str(self.tetro_fall_speed)) - Decimal("0.05")

                for ny in range(y, 0, -1):
                    for x in range(self.FIELD_COL):
                        self.field[ny][x] = self.field[ny-1][x]

    # キー入力されたときに処理する関数
    def onkeydown(self):
        if pyxel.btnp(pyxel.KEY_A, 10, 3): # 左
            if self.check_move(-1, 0): self.tetro_x-=1
        elif pyxel.btnp(pyxel.KEY_W, 10, 3): # 上
            while self.check_move(0, 1):
                self.tetro_y+=1
        elif pyxel.btnp(pyxel.KEY_D, 10, 3): # 左
            if self.check_move(1, 0): self.tetro_x+=1
        elif pyxel.btnp(pyxel.KEY_S, 10, 3): # 下
            self.drop_tetro()
        elif pyxel.btnp(pyxel.KEY_SPACE): # 回転
            ntetro = self.tetro_rotate()
            if self.check_move(0, 0, ntetro): self.tetro = ntetro
        elif pyxel.btnp(pyxel.KEY_H): # ホールド
            self.hold_tetro_click()

    # テトロミノを落とす処理
    def drop_tetro(self):
        if self.check_move(0, 1):
            self.tetro_y+=1
        else:
            self.tetro_fix()
            self.check_line()
            self.tetro_init()
            if not self.check_move(0, 0):
                self.gameover = True

    # 一定間隔でテトロミノを落とす
    def interval_tetro_fall(self):
        now = time.time()
        if (now - self.start) >= self.tetro_fall_speed:
            self.drop_tetro()

            self.start = time.time() # startをリセット

    def update(self):
        if not self.gameover:
            self.onkeydown()
            self.interval_tetro_fall()

    def draw(self):
        pyxel.cls(0)

        if not self.gameover:
            self.draw_field() # フィールドを表示
            self.draw_tetro() # テトロミノを表示
            self.draw_sidebar() # ネクストを表示
        else:
            pyxel.text(self.SCREEN_W/2, self.SCREEN_H/2 - 20, "GAMEOVER!!", 8)
            pyxel.text(self.SCREEN_W/2, self.SCREEN_H/2, "SCORE: "+str(self.score), 7)

App()