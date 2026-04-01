from machine import Pin,SPI,PWM
from random import randint
import framebuf
import time
import os

PICO_RP2040 = True
PICO_RP2350 = not PICO_RP2040

LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17

button_areas_top = ""
button_areas_bottom = ""
worm_direction_head = "left"
worm = [[250,150],[255,150],[260,150]]
worm_steps = 5
Game_MODE = "GAME_OVER"
foot = [-10,-10]
foot_collider = []
score = 0
grow = 0
death_reason = ""


def init_globale():
    global button_areas_top
    global button_areas_bottom

    button_areas_top = [["top","Knopf Oben",50,0,380,50,LCD.RED,7600,4800,4700,4400],["left","Links Oben",0,50,50,160,LCD.RED,7900,6150,7600,4900],["right","Rechts Oben",430,50,50,160,LCD.RED,4700,6150,4200,4900]]
    button_areas_bottom = [["bottom","Knopf Unten",50,110,380,50,LCD.RED,7600,7700,4700,7200],["left","Links Unten",0,0,50,110,LCD.RED,7900,7300,7600,6150],["right","Rechts Unten",430,0,50,110,LCD.RED,4700,7300,4200,6150]]


class LCD_3inch5(framebuf.FrameBuffer):

    def __init__(self):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000
        self.YELLOW=   0x000f
        
        self.rotate = 90   # Set the rotation Angle to 0°, 90°, 180° and 270°
        
        if self.rotate == 0 or self.rotate == 180:
            self.width = 320
            self.height = 240
        else:
            self.width = 480
            self.height = 160
            
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)
        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)
        
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,6_000_000)
        print(self.spi)  
        self.spi = SPI(1,baudrate=40_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
        print(self.spi)      
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        #self.spi.write(bytearray([0X00]))
        self.spi.write(bytearray([buf]))
        self.cs(1)


    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        self.write_cmd(0x21)
        
        self.write_cmd(0xC2)
        self.write_data(0x33)
        
        self.write_cmd(0XC5)
        self.write_data(0x00)
        self.write_data(0x1e)
        self.write_data(0x80)
        
        self.write_cmd(0xB1)
        self.write_data(0xB0)
        
        self.write_cmd(0XE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3a)
        self.write_data(0x56)
        self.write_data(0x4d)
        self.write_data(0x03)
        self.write_data(0x0a)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3e)
        self.write_data(0x0f)
        
        self.write_cmd(0XE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4d)
        self.write_data(0x06)
        self.write_data(0x0d)
        self.write_data(0x0b)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0f)
        
        self.write_cmd(0X3A)
        self.write_data(0x55)
        
        self.write_cmd(0x11)
        time.sleep_ms(120)
        self.write_cmd(0x29)
        
        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)
        
        self.write_cmd(0x36) # Sets the memory access mode for rotation
        if self.rotate == 0:
            self.write_data(0x88)
        elif self.rotate == 180:
            self.write_data(0x48)
        elif self.rotate == 90:
            self.write_data(0xe8)
        else:
            self.write_data(0x28)
    def show_up(self):
        if self.rotate == 0 or self.rotate == 180:
            self.write_cmd(0x2A)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x01)
            self.write_data(0x3f)
             
            self.write_cmd(0x2B)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0xef)
        else:
            self.write_cmd(0x2A)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x01)
            self.write_data(0xdf)
            
            self.write_cmd(0x2B)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x9f)
            
            
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def show_down(self):
        if self.rotate == 0 or self.rotate == 180:
            self.write_cmd(0x2A)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x01)
            self.write_data(0x3f)
             
            self.write_cmd(0x2B)
            self.write_data(0x00)
            self.write_data(0xf0)
            self.write_data(0x01)
            self.write_data(0xdf)
        else:
            self.write_cmd(0x2A)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x01)
            self.write_data(0xdf)
            
            self.write_cmd(0x2B)
            self.write_data(0x00)
            self.write_data(0xA0)
            self.write_data(0x01)
            self.write_data(0x3f)
            
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

    def touch_get(self): 
        if self.irq() == 0:
            self.spi = SPI(1,4_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0,3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

            X_Point=X_Point/3
            Y_Point=Y_Point/3
            
            self.tp_cs(1) 
            self.spi = SPI(1,40_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            Result_list = [X_Point,Y_Point]
            #print(Result_list)
            return(Result_list)
        
        
class game_object(LCD_3inch5):
    
    def create_game_table_1(self): 
        LCD.fill(LCD.WHITE)
        #TOP
        LCD.fill_rect(0,0,480,5,LCD.YELLOW)
        #LEFT TOP
        LCD.fill_rect(0,0,5,160,LCD.YELLOW)
        #REIGHT TOP
        LCD.fill_rect(475,0,5,160,LCD.YELLOW)

    def create_game_table_2(self): 
        #LEFT TOP
        LCD.fill(LCD.WHITE)
        LCD.fill_rect(0,0,5,160,LCD.YELLOW)
        #REIGHT TOP
        LCD.fill_rect(475,0,5,160,LCD.YELLOW)
        # BOTTOM
        LCD.fill_rect(0,155,480,5,LCD.YELLOW)

        
    def create_touch_areas_1(self,double_value):
        global worm_direction_head
        for button in button_areas_top:
            #print("Touch Areas no match",button[8], double_value[0],button[10]  )
            if button[7] > double_value[1] > button[9] and button[8] > double_value[0] > button[10]:
                #print("Touch Areas match",button[7], double_value[1],button[9]  )
                LCD.fill_rect(button[2],button[3],button[4],button[5],LCD.YELLOW)
                # Ignore Reverse
                if button[0] == "top" and worm_direction_head != "bottom" :
                    worm_direction_head = button[0]
                if button[0] == "left" and worm_direction_head != "right" :
                    worm_direction_head = button[0]
                if button[0] == "right" and worm_direction_head != "left" :
                    worm_direction_head = button[0]
                if button[0] == "bottom" and worm_direction_head != "top" :
                    worm_direction_head = button[0]


            
    def create_touch_areas_2(self,double_value):
        global worm_direction_head
        for button in button_areas_bottom:      
            #print("Touch Areas no match",button[8], double_value[0],button[10]  )
            if button[7] > double_value[1] > button[9] and button[8] > double_value[0] > button[10]:
                #print("Touch Areas match",button[7], double_value[1],button[9]  )
                LCD.fill_rect(button[2],button[3],button[4],button[5],LCD.YELLOW)
                # Ignore Reverse
                if button[0] == "top" and worm_direction_head != "bottom" :
                    worm_direction_head = button[0]
                if button[0] == "left" and worm_direction_head != "right" :
                    worm_direction_head = button[0]
                if button[0] == "right" and worm_direction_head != "left" :
                    worm_direction_head = button[0]
                if button[0] == "bottom" and worm_direction_head != "top" :
                    worm_direction_head = button[0]
               
                
                
    def update_worm(self):
        global worm
        global grow
        new_head = []
        new_worm = []
        past_head = worm[0]

        # calc new head pos
        if worm_direction_head == "left":
             new_head = [ past_head[0] - 5 , past_head[1] ]
        elif worm_direction_head == "right":
             new_head = [ past_head[0] + 5 , past_head[1] ]
        elif worm_direction_head == "top":
             new_head = [ past_head[0] , past_head[1] - 5 ]
        elif worm_direction_head == "bottom":
             new_head = [ past_head[0] , past_head[1] + 5 ]
             
        #print("new_head: ", new_head)
        
        new_worm.append(new_head)
        for worm_body_elemtent in worm:
            new_worm.append(worm_body_elemtent)
        
        if grow != 0:
            new_worm = new_worm
            grow = grow - 1
        else:    
            new_worm = new_worm[:-1]
        

        
        ret = self.boundry_check(new_worm)
        ret_bite = self.bite_myself_check(new_worm)
        if ret_bite == True:
            self.end_game("i bite my self")
            
        if ret == False:
            worm = new_worm
            self.check_eat_time()
    
    def create_matrix(self,position):
        matrix = []
        for item_x in range(position[0],position[0]+6):
            for item_y in range(position[1],position[1]+6):
                matrix.append([item_x,item_y])
        return matrix
        
            
    def check_eat_time(self):
        global foot
        global foot_collider
        global score
        global grow
        ret_value = False
        head_collider = []
        
        
        head_collider = self.create_matrix(worm[0])
        # Collisions Check
        for point_in_foot in foot_collider:
            for point_in_head in head_collider:
                if point_in_foot[0] == point_in_head[0] and point_in_foot[1] == point_in_head[1]:
                    ret_value = True
                    break
        if ret_value == True:
            score = score + 100
            self.spawn_foot()
            grow = grow + 5
        
        return ret_value
  
    def boundry_check(self,new_worm):
        ret_value = False
        #Left
        if new_worm[0][0] < 5:
            self.end_game("i hit a wall")
            ret_value = True
        #Right
        if new_worm[0][0] > 465:
            self.end_game("i hit a wall")
            ret_value = True
        #Top    
        if new_worm[0][1] < 5:
            self.end_game("i hit a wall")
            ret_value = True
        
        #Down
        if new_worm[0][1] > 305:
            self.end_game("i hit a wall")
            ret_value = True
            
        return ret_value
    
    def round_50(self, value):
        return 5 * round(value/5)
        
    def spawn_foot(self):
        global foot
        global foot_collider
        randx = randint(10, 450)
        randy = randint(10, 300)
        foot = [self.round_50(randx),self.round_50(randy)]
        foot_collider = self.create_matrix(foot)
    
    def bite_myself_check(self,new_worm):
        global worm
        ret_value = False
        head_collider = []
                
        head_collider = self.create_matrix(new_worm[0])
        # Collisions Check
        for worm_part in worm[2:]:
            for point_in_head in head_collider:
                if worm_part[0] == point_in_head[0] and worm_part[1] == point_in_head[1]:
                    ret_value = True
                    break               

        return ret_value
        
    
    def end_game(self,reason):
        global Game_MODE
        global death_reason
        print("Game Over")
        death_reason = reason
        Game_MODE = "GAME_OVER"
        

        
        
if __name__=='__main__':

    LCD = LCD_3inch5()
    game = game_object()
    init_globale()
    
    display_color = 0x001F
       
    while True:
        LCD.fill(LCD.WHITE)

        get = LCD.touch_get()
        
        if Game_MODE == "RUN":
            
            game.update_worm()
            game.create_game_table_1()
            score_text = "score: " + str(score)
            LCD.text(score_text,10,10,LCD.BLACK)
            
            for worm_element in worm:
                if 160 > worm_element[1]:
                    LCD.fill_rect(worm_element[0],worm_element[1],10,10,LCD.RED)
                    
            if 160 > foot[1]:
                LCD.fill_rect(foot[0],foot[1],10,10,LCD.GREEN)
            if get != None:
                game.create_touch_areas_1(get)
                #LCD.text(str(get),170,70,LCD.BLACK) 
            
            LCD.show_up()
            game.create_game_table_2()
            for worm_element in worm:
                if worm_element[1] >= 155:
                    worm_possition_correction = worm_element[1] - 160
                    LCD.fill_rect(worm_element[0],worm_possition_correction,10,10,LCD.RED)
                    
            if foot[1] >= 155:
                foot_possition_correction = foot[1] - 160
                LCD.fill_rect(foot[0],foot_possition_correction,10,10,LCD.GREEN)
                
            if get != None:
                game.create_touch_areas_2(get)
            LCD.show_down()
     
            
            time.sleep(0.01)
            
        else:
            
            
            LCD.fill(LCD.WHITE)          
            LCD.text("SNAKE CLONE",190,70,LCD.BLACK)
            LCD.text("Tip to Start",185,90,LCD.BLACK)
            
            if score != 0:
                score_text = "score: " + str(score)
                LCD.text(score_text,190,110,LCD.BLACK)
                
            if death_reason != "":
                LCD.text(death_reason,180,130,LCD.BLACK)
            
            LCD.show_up()
            
            LCD.fill(LCD.WHITE)
            LCD.show_down()
            
            # Reset start Condition
            worm = [[250,150],[255,150],[260,150]]
            worm_direction_head = "left"
            
            if get != None:
                Game_MODE = "RUN"
                game.spawn_foot()
                score = 0
                death_reason = ""
    

