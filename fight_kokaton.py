import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)



class Beam:#練習1
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):#1
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")#画像ロード#1
        self.rct = self.img.get_rect()#rectの取得#1
        self.rct.centery = bird.rct.centery#ビーム、こうかとんの中心縦座標##1
        self.rct .left = bird.rct.right#ビームの左座標＝こうかとんの右端座標# 1
        self.vx, self.vy = +5, 0 #横に5、縦0の速度ベクトル#

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


# 課題1：Scoreクラスの追加
class Score:
    """
    打ち落とした爆弾の数を表示するスコアクラス
    """
    def __init__(self):
        # イニシャライザ
        self.fonto = pg.font.SysFont(None, 30) # フォントの設定
        self.color = (0, 0, 255) #青
        self.score = 0 # スコアの初期値
        # 文字列Surface
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)
        # 文字列の中心座標：画面左下
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        """
        現在のスコアを表示させる文字列Surfaceの生成とblit
        """
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.img, self.rct)


# 課題3：Explosionクラスの追加
class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self, bomb: "Bomb"):
        # イニシャライザ
        img = pg.image.load("fig/explosion.gif")
        # 元の画像と上下左右にflipした画像のリスト
        self.imgs = [img, pg.transform.flip(img, True, True)]
        # 爆発した爆弾のrct.centerに座標を設定
        self.rct = img.get_rect()
        self.rct.center = bomb.rct.center
        # 表示時間（爆発時間）lifeを設定
        self.life = 40

    def update(self, screen: pg.Surface):
        # 爆発経過時間lifeを1減算
        self.life -= 1
        # lifeが正なら、Surfaceリストを交互に切り替えて表示
        if self.life > 0:
            screen.blit(self.imgs[self.life // 10 % 2], self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))#左辺呼び出し、右辺数値
    # bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    # for i in range(NUM_OF_BOMBS):
    #     bomb = Bomb((255, 0, 0), 10)
    #     bombs.appned(bomb)

    # 課題2
    beams = [] 
    # 課題1
    score = Score() 
    # 課題3
    exps = []

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # 課題2
                beams.append(Beam(bird))             
        screen.blit(bg_img, [0, 0])

        for bomb in bombs:
            if bomb is not None:
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー時にこうかとん画像を切り替え
                    fonto = pg.font.Font(None, 80)
                    txt = fonto.render("Game Over", True, (255, 0, 0))
                    screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
        
        # 課題2：要素に対して二重ループ
        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if beam is not None and bomb is not None:
                    if beam.rct.colliderect(bomb.rct):  # 練習2：爆弾とビームの衝突判定
                        # 課題3：衝突したらインスタンス
                        exps.append(Explosion(bomb))
                        
                        beams[j] = None
                        bombs[i] = None
                        # 課題1：爆弾を打ち落としたらスコアアップ
                        score.score += 1
                        bird.change_img(6, screen)  # 練習3：こうかとん喜びエフェクト
                        pg.display.update()#追加1
        
        bombs = [bomb for bomb in bombs if bomb is not None]
        # 課題2：要素がNoneでないもの画面内のものだけに更新
        beams = [beam for beam in beams if beam is not None and check_bound(beam.rct) == (True, True)]
        # 課題3：lifeが0より大きいインスタンスだけのリストにする
        exps = [exp for exp in exps if exp.life > 0]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        # 課題2：リスト内の全ビーム
        for beam in beams:
            beam.update(screen)
        for bomb in bombs:
            bomb.update(screen)
        # 課題3：updateを呼び出して爆発を
        for exp in exps:
            exp.update(screen)
        # 課題1：updateを呼び出してスコアを表示
        score.update(screen) 
        pg.display.update()
        tmr += 1
        clock.tick(50)
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()