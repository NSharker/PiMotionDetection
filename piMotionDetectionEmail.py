'''
Raspberry Pi Motion Detection with Email Notification
The program will create an infinite loop
that will send an email with the date, time and
an image attached whenever it detects motion

Motion is detected as change between two subsequent
images in the green channel. The detection rate can
be changed by using different threshold and sensitivity
values.

Make sure to change the email server information if you
plan on using a service other than GMAIL

Also need to fill in the email login, password,
from address and to address
'''


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO
from picamera import PiCamera
from PIL import Image
import datetime
import os




# Motion detection settings:
# Threshold (how much a pixel has to change by to be marked as "changed")
# Sensitivity (how many changed pixels before capturing an image)
threshold = 60
sensitivity = 20

#Width the number of pixels wide for the images
#height the number of pixels tall for the images
#might consider using image.size to grab the info
width = 1280
height = 720


#intialize the camera
camera = PiCamera()
camera.resolution = (width, height)


#capture first image as intialization
streamA = BytesIO()
camera.capture(streamA, format='png')
streamA.seek(0)
imageA = Image.open(streamA)

#Loop forever
#take second image and compare it to first image
#check pixel by pixel for the difference
#if the difference between pixels is larger than threshold 
#   then increment changedpixels
#if changedpixels is larger than sensitivity
#   then motion detected and send email
#set first image as second and continue with loop
while (1):
    streamB = BytesIO()
    camera.capture(streamB, format='png')
    streamB.seek(0)
    imageB = Image.open(streamB)
    timeString = datetime.datetime.now().strftime("%Y-%m-%d-%I-%M-%p")
    
    pictureA = imageA.load()  
    pictureB = imageB.load()
    
    changedpixels = 0
    
    #Increment by 2 to go through only half the pixels for faster processing
    for x in range(0, width,2):
        for y in range(0, height,2):
            diff = abs(pictureA[x,y][1] - pictureB[x,y][1])
            if diff > threshold:
                #print(diff)
                changedpixels += 1
                
    
    if changedpixels > sensitivity:
        fileName = timeString + ".png"
        imageB.save(fileName)
        #Change this if using a service other than gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        #Replace email login and password
        server.login("EMAIL LOGIN","EMAIL PASSWORD")
        #Replace with email address
        fromaddr = "FROM ADDRESS"
        #Replace with email address 
        toaddr = "TO ADDRESS"       
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Motion Detected at " + timeString
        body = "Time picture was taken at: " + timeString
        msg.attach(MIMEText(body, 'plain'))
        fp = open(fileName, 'rb')
        img = MIMEImage(fp.read())
        fp.close
        img.add_header('Content-Disposition', 'attachment', filename=fileName)
        msg.attach(img)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print("IMAGE CAPTURED! at time: \n" + timeString)
        os.remove(fileName)
       
    imageA = imageB



