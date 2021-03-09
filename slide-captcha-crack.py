#!/usr/bin/env python3

'''
Date     : 2018/11/15
Author   : ybdt
FileName : slide_captcha_crack.py
'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
from PIL import Image
import random

def get_image(browser, n):
    browser.save_screenshot(n + ".png")
    picture = Image.open(n + ".png").crop( (793, 278, 1115, 477) )
    picture.save("crop_" + n + ".png")
    return picture

def get_space(picture1, picture2):
    start = 60 # define slider left distance 60
    threhold = 80 # define the pixel-by-pixel difference value
    for i in range(start, picture1.size[0]):
        for j in range(picture1.size[1]):
            rgb1 = picture1.load()[i, j]
            rgb2 = picture2.load()[i, j]
            res1 = abs(rgb1[0] - rgb2[0])
            res2 = abs(rgb1[1] - rgb2[1])
            res3 = abs(rgb1[2] - rgb2[2])
            if (res1 < threhold and res2 < threhold and res3 < threhold):
                continue
            else:
                print( "rgb diffrence is: " + str(res1) + " " + str(res2) + " " + str(res3) )
                print("calculated gab offset is: " + str(i) )
                return i

def get_tracks(space):
    '''
    acceleration formula

    x->distance
    v0->initial speed
    t->time
    a->accelerated speed
    vt->current speed
    
    vt = v0 + a * t
    x = v0 * t + 0.5 * a * t * t
    
    '''
    space = round(space * 5 / 6)
    print( "calculated altered gap space: " + str(space) )
    space += 20
    v0 = 0
    t = random.randint(2, 3) / 10
    forward_tracks = []
    current = 0
    mid = space * 6 / 10
    drag_distance = 0
    while current < space:
        if current < mid:
            a = 2
        else:
            a = -3
        s = v0 * t + 0.5 * a * (t ** 2)
        vt = v0 + a * t
        v0 = vt
        current += s
        drag_distance += round(s)
        forward_tracks.append( round(s) )
    print( "calculated forward move offset: " + str(drag_distance) )
    print(forward_tracks)
    back_tracks = [-4, -2, -2, -1, -1, -4, -3, -1, -2, -6, -3]
    back = 0
    for i in back_tracks:
        back += abs(i)
    print( "calculated back move offset: " + str(back) )
    print(back_tracks)
    return {"forward_tracks": forward_tracks, "back_tracks": back_tracks}

def slide_to_gap(browser, slider, tracks):
    ActionChains(browser).click_and_hold(slider).perform()
    for forward_track in tracks['forward_tracks']:
        ActionChains(browser).move_by_offset(xoffset=forward_track, yoffset=0).perform()
    time.sleep(0.5)
    for back_track in tracks["back_tracks"]:
        ActionChains(browser).move_by_offset(xoffset=back_track, yoffset=0).perform()
    
    # simulate human shake
    ActionChains(browser).move_by_offset(xoffset=-3, yoffset=0).perform()
    ActionChains(browser).move_by_offset(xoffset=3, yoffset=0).perform()
    ActionChains(browser).move_by_offset(xoffset=2, yoffset=0).perform()
    ActionChains(browser).move_by_offset(xoffset=-2, yoffset=0).perform()
    time.sleep(0.5)

    ActionChains(browser).release().perform()
    time.sleep(1)

def main():
    # maximize the chrome window and initialize the chrome class
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--start-maximized")
    browser = webdriver.Chrome(options=browser_options)

    # visit the site, and fill in the phone number and the password, and then click the login
    browser.get("http://xxx.xxx.com")
    browser.find_element_by_id("xxx").send_keys("xxx")
    browser.find_element_by_id("xxx").send_keys("xxx")
    time.sleep(1) # if set 0.5s, cannot click login occur once
    browser.find_element_by_id("xxx").click()

    # get the verification picture with the slider and the gap
    time.sleep(1)
    get_image(browser, "slider_with_gap")

    # get the verification picture with the gap but without the slider
    WebDriverWait(browser, 10).until(expected_conditions.element_to_be_clickable( (By.CLASS_NAME, "geetest_slider_button") ) ).click()
    time.sleep(1.7) # wait for a moment in case the picture is loading instead of presenting the verification picture
    picture1 = get_image(browser, "slider_without_gap")

    # alter the css for getting the verification picture without the gap and the slider
    browser.execute_script("document.querySelectorAll('canvas')[2].style=''")
    picture2 = get_image(browser, "slider_with_full")
    time.sleep(0.5) # if without this, it will cannot drap the drop the slider

    # explict wait the geetest verification present, get the space then drag and drop slider
    slider = WebDriverWait(browser, 10).until(expected_conditions.element_to_be_clickable( (By.CLASS_NAME, "geetest_slider_button") ) )
    space = get_space(picture1, picture2)
    tracks = get_tracks(space)
    slide_to_gap(browser, slider, tracks)

    # don't know why program crashed
    time.sleep(10)

if __name__ == "__main__":
    main()
