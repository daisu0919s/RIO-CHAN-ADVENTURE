import pyxel

# ゲームの状態を管理するフラグ
STATE_TITLE = 0
STATE_GAME = 1
STATE_GAME_OVER = 2
STATE_GAME_CLEAR = 3

# ゲーム初期化
class App:
    def __init__(self):
        pyxel.init(160, 120, title="RIO-CHAN ADVENTURE")
        pyxel.load("assets/riochan.pyxres")  # リソースファイルを読み込み
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """ゲームのリセット処理"""
        self.state = STATE_TITLE
        self.player_x = 20
        self.player_y = 80
        self.player_dx = 0
        self.player_dy = 0
        self.bouquet_x = 90
        self.bouquet_y = 60
        self.bouquet_dx = 0
        self.bouquet_dy = 0
        self.bouquet_speed = 1  # 花束の逃げる速度
        self.bouquet_direction = 0  # 初期の進行方向（上：0, 左：1, 下：2, 右：3）
        
        # 敵の初期位置と速度
        self.enemy_x = pyxel.rndi(0, pyxel.width - 8)
        self.enemy_y = pyxel.rndi(0, pyxel.height - 8)
        self.enemy_speed = 1  # 敵の移動速度

        # ゲーム開始からの経過時間（フレーム数）
        self.start_time = pyxel.frame_count

    def update(self):
        if self.state == STATE_TITLE:
            self.update_title()
        elif self.state == STATE_GAME:
            self.update_game()
        elif self.state == STATE_GAME_CLEAR:
            self.update_game_clear()
        elif self.state == STATE_GAME_OVER:
            self.update_game_over()

    def update_title(self):
        """初期画面の更新"""
        if pyxel.btnp(pyxel.KEY_SPACE)or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.state = STATE_GAME

    def update_game(self):
        """ゲーム画面の更新"""
        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.player_dx = -2
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.player_dx = 2
        else:
            self.player_dx = 0

        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.player_dy = -2
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.player_dy = 2
        else:
            self.player_dy = 0

        self.player_x += self.player_dx
        self.player_y += self.player_dy

        # プレイヤーが画面外に出ないように制限
        self.player_x = max(0, min(self.player_x, pyxel.width - 8))
        self.player_y = max(0, min(self.player_y, pyxel.height - 8))

        # 花束がプレイヤーから逃げるように動く
        self.move_away_from_player()

        # 花束が画面外に出た場合、ランダムにプレイヤーから離れた位置に出現
        if self.bouquet_x < 0 or self.bouquet_x >= pyxel.width or self.bouquet_y < 0 or self.bouquet_y >= pyxel.height:
            self.respawn_bouquet()

        # 敵がプレイヤーを追いかけるように移動
        # ゲーム開始から3秒間は敵を動かさない
        if pyxel.frame_count - self.start_time > 60:  # 60フレーム = 1秒
            self.move_enemy_towards_player()

        # プレイヤーと敵が衝突した場合、ゲームオーバー
        if abs(self.player_x - self.enemy_x) < 8 and abs(self.player_y - self.enemy_y) < 8:
            self.state = STATE_GAME_OVER

        # 花束を取得したらクリア
        if abs(self.player_x - self.bouquet_x) < 8 and abs(self.player_y - self.bouquet_y) < 8:
            self.state = STATE_GAME_CLEAR

    def move_away_from_player(self):
        """花束がプレイヤーから逃げるように移動する"""
        # プレイヤーと花束の距離を計算
        dx = self.player_x - self.bouquet_x
        dy = self.player_y - self.bouquet_y

        # 逃げる方向を計算
        if abs(dx) > abs(dy):
            # プレイヤーが花束の左右にいる場合
            if dx > 0:
                # プレイヤーが右にいるので、花束は左に逃げる
                self.bouquet_dx = -self.bouquet_speed
            else:
                # プレイヤーが左にいるので、花束は右に逃げる
                self.bouquet_dx = self.bouquet_speed
            self.bouquet_dy = 0
        else:
            # プレイヤーが花束の上下にいる場合
            if dy > 0:
                # プレイヤーが下にいるので、花束は上に逃げる
                self.bouquet_dy = -self.bouquet_speed
            else:
                # プレイヤーが上にいるので、花束は下に逃げる
                self.bouquet_dy = self.bouquet_speed
            self.bouquet_dx = 0

        # 花束を移動
        self.bouquet_x += self.bouquet_dx
        self.bouquet_y += self.bouquet_dy

    def respawn_bouquet(self):
        """花束が画面外に出たときに、プレイヤーから離れたランダムな位置に再出現させる"""
        while True:
            # ランダムな位置を生成（画面外に出た場合は適当な位置）
            new_bouquet_x = pyxel.rndi(0, pyxel.width - 8)
            new_bouquet_y = pyxel.rndi(0, pyxel.height - 8)
            
            # プレイヤーとの距離を計算し、一定距離離れた位置であれば出現
            dx = new_bouquet_x - self.player_x
            dy = new_bouquet_y - self.player_y
            if abs(dx) > 20 and abs(dy) > 20:
                self.bouquet_x = new_bouquet_x
                self.bouquet_y = new_bouquet_y
                break

    def move_enemy_towards_player(self):
        """敵がプレイヤーを追いかけるように移動する"""
        # プレイヤーと敵の距離を計算
        dx = self.player_x - self.enemy_x
        dy = self.player_y - self.enemy_y

        # x軸方向の移動
        if abs(dx) > 1:
            self.enemy_x += self.enemy_speed if dx > 0 else -self.enemy_speed

        # y軸方向の移動
        if abs(dy) > 1:
            self.enemy_y += self.enemy_speed if dy > 0 else -self.enemy_speed

    def update_game_clear(self):
        """ゲームクリア画面の更新"""
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.reset_game()

    def update_game_over(self):
        """ゲームオーバー画面の更新"""
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.reset_game()

    def draw(self):
        if self.state == STATE_TITLE:
            self.draw_title()
        elif self.state == STATE_GAME:
            self.draw_game()
        elif self.state == STATE_GAME_CLEAR:
            self.draw_game_clear()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()

    def draw_title(self):
        """初期画面の描画"""
        pyxel.cls(6)
        title = "RIO-CHAN ADVENTURE"
        press_start = "PRESS SPACE TO START"
        pyxel.text((pyxel.width - len(title) * 4) // 2, 40, title, pyxel.frame_count % 16)
        pyxel.text((pyxel.width - len(press_start) * 4) // 2, 60, press_start, 8)

    def draw_game(self):
        """ゲーム画面の描画"""
        pyxel.cls(6)  # クリーム色の背景

        # 背景の描画：(x, y, tm, u, v, w, h, colkey)
        # xy:コピー先の座標、tm:タイルマップの番号
        # uv:コピー元の座標、wh:コピー範囲、col透明色
        pyxel.bltm(0, 0, 0, 0, 0, 160, 120, 0)

        # プレイヤーの描画
        pyxel.blt(self.player_x, self.player_y, 0, 0, 0, 8, 8, 3)

        # 花束の描画
        pyxel.blt(self.bouquet_x, self.bouquet_y, 0, 0, 8, 8, 8, 3)

        # 敵の描画
        pyxel.blt(self.enemy_x, self.enemy_y, 0, 8, 0, 8, 8, 3)

    def draw_game_clear(self):
        """ゲームクリア画面の描画"""
        pyxel.cls(6)
        game_clear_text = "YOU GOT A BOUQUET"
        restart_text = "PRESS R TO RESTART"
        pyxel.text((pyxel.width - len(game_clear_text) * 4) // 2, 40, game_clear_text, 8)
        pyxel.text((pyxel.width - len(restart_text) * 4) // 2, 80, restart_text, 8)

    def draw_game_over(self):
        """ゲームオーバー画面の描画"""
        pyxel.cls(0)
        game_over_text = "CAUGHT BY DAISUKE"
        restart_text = "PRESS R TO RESTART"
        pyxel.text((pyxel.width - len(game_over_text) * 4) // 2, 40, game_over_text, 8)
        pyxel.text((pyxel.width - len(restart_text) * 4) // 2, 80, restart_text, 8)


App()
