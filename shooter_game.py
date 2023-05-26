from pygame import *
from random import randint
from time import time as timer 

# Sprite'lar için ebeveyn sınıfı
class GameSprite(sprite.Sprite):
# Sınıf kurucusu
  def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
      #sınıf kurucusunu çağırıyoruz (Sprite):
      sprite.Sprite.__init__(self)
      
      # Her sprite image - görüntü özelliğini depolamalıdır
      self.image = transform.scale(image.load(player_image), (size_x, size_y))
      self.speed = player_speed
      
      # Her sprite, içine yazıldığı dikdörtgenin rect özelliğini saklamalıdır
      self.rect = self.image.get_rect()
      self.rect.x = player_x
      self.rect.y = player_y

# Pencereye kahraman çizen yöntem
  def reset(self):
      window.blit(self.image, (self.rect.x, self.rect.y))

# Ana oyuncunun sınıfı
class Player(GameSprite):
  # Sprite'ı klavye oklarıyla kontrol etme yöntemi
   def update(self):
       keys = key.get_pressed()
       if keys[K_LEFT] and self.rect.x > 5:
           self.rect.x -= self.speed
       if keys[K_RIGHT] and self.rect.x < win_width - 80:
           self.rect.x += self.speed
           
   # Atış yöntemi (orada bir mermi oluşturmak için oyuncunun yerini kullanırız)
   def fire(self):
       bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
       bullets.add(bullet)


# Mermi sprite sınıfı 
class Bullet(GameSprite):
  #düşmanın hareketi
  def update(self):
      self.rect.y += self.speed
      #ekranın kenarına ulaştığında kaybolur
      if self.rect.y < 0:
          self.kill()  

# Sprite-düşman sınıfı 
class Enemy(GameSprite):
  #düşmanın hareketi
  def update(self):
      self.rect.y += self.speed
      global lost
      #ekranın kenarına ulaştığında kaybolur
      if self.rect.y > win_height:
          self.rect.x = randint(80, win_width - 80)
          self.rect.y = 0
          lost = lost + 1
          
# Böyle resimlere ihtiyacımız var:
img_back = "galaxy.jpg" #oyunun arka planı
img_bullet = "bullet.png" #mermi
img_hero = "rocket.png" #kahraman
img_enemy = "ufo.png" # düşman


img_ast = "asteroid.png" # asteroit    


# Bir pencere oluşturuyoruz
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# Arka plan müziği
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# Karakterler ve yazıtlar
font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.Font(None, 36)

# Sprite oluşturuyoruz
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)


score = 0 #düşmüş gemiler
lost = 0 # kaçırılan gemiler


goal = 20 #Kazanmak için kaç gemiyi vurman gerekiyor      
max_lost = 10#çok gemi kaçırırsak kaybederiz              
life = 3 # yaşam puanı                                   


#bir grup düşman sprite oluşturun
monsters = sprite.Group()
for i in range(1, 6):
  monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
  monsters.add(monster)



asteroids = sprite.Group()
for i in range(1, 3):
   asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
   asteroids.add(asteroid)


bullets = sprite.Group()

# "oyun bitti" değişkeni: True olduğunda, sprite ana döngüde çalışmayı durdurur
finish = False
#Ana oyun döngüsü:
run = True #bayrak pencereyi kapat düğmesiyle sıfırlanır


rel_time = False # şarjdan sorumlu bayrak            
num_fire = 0 # çekimleri saymak için değişken                 


while run:
   #Kapat düğmesindeki olayı tıklayın
   for e in event.get():
       if e.type == QUIT:
           run = False
       #space'e basılma durumunda sprite ateş ediyor
       elif e.type == KEYDOWN:
           if e.key == K_SPACE:
                   
                   if num_fire < 5 and rel_time == False:
                       num_fire = num_fire + 1
                       fire_sound.play()
                       ship.fire()
                     
                   if num_fire  >= 5 and rel_time == False : #eğer oyuncu 5 atış yaptıysa
                       last_time = timer() #bunun gerçekleştiği zamanı tespit ediyoruz
                       rel_time = True #yeniden yükleme bayrağını yerleştiriyoruz
                 
   # Oyunun kendisi: sprite eylemleri, oyunun kurallarını kontrol etme, yeniden çizme
   if not finish:
       # arka planı güncelliyoruz
       window.blit(background,(0,0))

       #sprite hareketleri üretiyoruz
       ship.update()
       monsters.update()
       asteroids.update()                               
       bullets.update()


       #Döngünün her yinelenmesinde onları yeni bir konumda güncelliyoruz
       ship.reset()
       monsters.draw(window)
       asteroids.draw(window) 
       bullets.draw(window)


       
       if rel_time == True:
           now_time = timer() #zamanı okuyoruz
       
           if now_time - last_time < 3:  #3 saniye geçene kadar şarj bilgilerini gösteriyoruz
               reload = font2.render('Wait, reload...', 1, (150, 0, 0))
               window.blit(reload, (260, 460))
           else:
               num_fire = 0   # mermi sayacını sıfırlıyoruz
               rel_time = False # şarj bayrağını sıfırlıyoruz
        
       
       
       # mermi ve canavarların çarpışmasını kontrol etme (hem canavar hem de mermi dokunulduğunda kaybolur)
       collides = sprite.groupcollide(monsters, bullets, True, True)
       for c in collides:
           # Bu döngü, canavarlar vurulana kadar tekrarlanır
           score = score + 1
           monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
           monsters.add(monster)
       
       
       
       #  eğer sprite düşmana dokunursa, canı azalır 
       if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
           sprite.spritecollide(ship, monsters, True)
           sprite.spritecollide(ship, asteroids, True)
           life = life -1

       # Yenilgi 
       if life == 0 or lost >= max_lost:
           finish = True #kaybettik, arka planı koyduk ve artık spriteları yönetmiyoruz.
           window.blit(lose, (200, 200))

       # Kazancınızı kontrol edin: kaç puan aldınız?
       if score >= goal:
           finish = True
           window.blit(win, (200, 200))
      
       
       
       
       # Ekrana metin yazıyoruz
       text = font2.render("Score: " + str(score), 1, (255, 255, 255))
       window.blit(text, (10, 20))

       text_lose = font2.render("Missed: "+ str(lost), 1, (255, 255, 255))
       window.blit(text_lose, (10, 50))

       
       if life == 3:
           life_color = (0, 150, 0)
       if life == 2:
           life_color = (150, 150, 0)
       if life == 1:
           life_color = (150, 0, 0)
       text_life = font1.render(str(life), 1, life_color)
       window.blit(text_life, (650, 10))
       

       display.update()

   
   # bonus: otomatik oyun yeniden başlatma
   else:
       finish = False
       score = 0
       lost = 0
       num_fire = 0
       life = 3 
       for b in bullets:
           b.kill()
       for m in monsters:
           m.kill()
       for a in asteroids: 
           a.kill()   
    
       time.delay(3000)
       for i in range(1, 6):
           monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
           monsters.add(monster)
       for i in range(1, 3):
           asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
           asteroids.add(asteroid)   
          
   time.delay(50)