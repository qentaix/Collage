#Importing the libraries
import time
from PIL import Image
import numpy #I won't be importing it as 'np' as it is easier for beginners to understand what library we are using.
import math
import json
import glob
import threading
import copy
from tqdm import tqdm

"""""
Libraries required to run this code ( in the form of commands to install them ):
pip install Pillow
pip install numpy
pip install tqdm
"""""

"""""
IMPORTANT NOTICE: This Code can have pretty heavy usage of the disk on which you store the images. Furthermore,
the access time to get each image plays a crucial role. As such it is suggested to
run this code of an SSD as Random Read performance on them is way better than that of Hard Drives.
It should still be said that even with an SSD the time to process a single collage can be extremely
large, especially if you utilise the advanced compare function.

    As to refer to quality of generated collages. It directly depends on four factors:
1. How many images You have downloaded
2. The resolution of the downloaded images
3. The Horizontal resolution you set for the collage
    Anything posted by me ( u/QentaiX ) on reddit was most likely generated with my library of ~80,000 images
all in resolution of 64x64, sometimes downscaled to 32x32. For similar results you can simulate my workspace 
by downloding similar amount of images in the same resolution. If the output quality still does not satisfy 
your needs, contact me and I might be able to see what I can do to improve it. Thank You!

    For anybody who may be reading this and is relatively new to Python... First of all, thank you!
It is a great achievement for me to have a chance to have my code potentially help somebody. For You,
I would recommend reading the code from top to bottom as processing steps are roughly sorted that way
and understanding every next step might not be as easy without knowing how the previous part works.
    I have made an attempt at explaining everything in a lot of detail focusing on the points that took
longer for myself to figure out. In case any explanations are insufficient, you can text me on reddit
at u/QentaiX. It is also cool if you share any collage created with this code with me and in case the result
does not satisfy you I can try to help as much as I can.
"""""

def Calculate_Averages(Image):

    #Converting a PIL 'Image' into an array to calculate the average values.
    Numpy_Array = numpy.array(Image.convert("RGB"))

    #Setting the values for Total amount of Red, Green and Blue.
    Red_Total = 0
    Green_Total = 0
    Blue_Total = 0

    #Pixel count defines by how much we will need to divide the sum. It is just width * height of array
    Pixel_Count = Numpy_Array.shape[0] * Numpy_Array.shape[1]

    #Check if the array has appropriate dimensions, otherwise image can break the upcoming code
    if(len(Numpy_Array.shape)==3):

        #Check again just to be sure that the colors came properly in 3 channels
        if(Numpy_Array.shape[2] == 3):

            #Cut out segments of an array 
            Red_Cut = Numpy_Array[:,:,0]
            Green_Cut = Numpy_Array[:,:,1]
            Blue_Cut = Numpy_Array[:,:,2]

            #Reshape the segments into 1-dimensional arrays
            Red_Channel = numpy.resize(Red_Cut, Pixel_Count)
            Green_Channel = numpy.resize(Green_Cut, Pixel_Count)
            Blue_Channel = numpy.resize(Blue_Cut, Pixel_Count)

            #Get the sums of these arrays
            Red_Total = sum(Red_Channel)
            Green_Total = sum(Green_Channel)
            Blue_Total = sum(Blue_Channel)

        else:

            #This doesn't really ever trigger since a few other changes but it doesn't slow down the code so I left it in
            print('Broken Image')
            return (-999, -999, -999)

        #Now we can start calculating the averages. We can just divide the totals by the amount of pixels accounted
        Red_Average = Red_Total / Pixel_Count
        Green_Average = Green_Total / Pixel_Count
        Blue_Average = Blue_Total / Pixel_Count

        #We can now build these three into a tuple for some of the further calcculations. Lets call it 'RGB Average'.
        RGB_Average = (Red_Average, Green_Average, Blue_Average)

        #Return our RGB Average from the function
        return RGB_Average
    else:

        #This doesn't really ever trigger since a few other changes but it doesn't slow down the code so I left it in
        print('Broken Image')
        return (-999, -999, -999)


"""""
Thsi function will return our image, segmented into squares. The Horizontal_Resolution here
sets the amount of squares that the image will be horizontally. Remember that each square will be a
separate image and the total size / resolution of the image can scale up pretty quickly.
"""""
def Segment_Image(Image_, Horizontal_Resolution):

    #Before we start any calculations, let's get the size of the image.
    Dimensions = Image_.size
    Width = Dimensions[0]
    Height = Dimensions[1]

    #We need for each square to be equal in size and have an integer amount of pixels so our first step is to
    #Resize and slightly crop the image in such a way that lets us build it from squares.
    #Wht we need to do now is first resize the image in such a way that the width is divisible by the Horizontal
    #Resolution. We can do this by getting the current division value of Width / Horizontal_Resolution and round it up to
    #an integer. After that we will know the preferred resolution for every square.
    Raw_Segment_resolution = Width / Horizontal_Resolution
    Preferred_Segment_Resolution = int(Raw_Segment_resolution)

    #Now we can go backwards and multiply the Preferred resolution by the Horizontal_resolution
    #in order to get the optimal width value.
    Optimal_Width = Preferred_Segment_Resolution * Horizontal_Resolution

    #We can now divide the Height by our old width and multiply by the new one. That way we can get the
    #value for the height that will keep the aspect ratio constant after resizing the image
    Matching_Height = Height / Width * Optimal_Width

    #Don't forget to make it and integer as resize doesn't like floats
    Matching_Height = int(Matching_Height)

    #We can now resize the image to this new size
    Resized = Image_.resize((Optimal_Width, Matching_Height))

    #After resizing we have to deal with the fact that the hight still cannot be split into squares with thiss resolution.
    #Sadly the best solution is to cut off a few rows fom the bottom as 
    #adding rows with other colors will tamper with our calculations.
    #We will go through a similar procedure, now diving the height by the resolution of single square.
    Vertical_Squares = Matching_Height / Preferred_Segment_Resolution

    #We can now floor the value ( round down ) to get how many squares should fit into the height
    Optimal_Vertical_Squares = math.floor(Vertical_Squares)

    #And multiply the amount with the resolution of a single square to get the largest height that is
    #both smaller than our current one and divisible by the Square Resolution
    Optimal_Height = Optimal_Vertical_Squares * Preferred_Segment_Resolution

    #We can now make a 'box' tuple to specify which part of the image we want to be left in after the crop.
    Cropping_Box = (0, 0, Optimal_Width, Optimal_Height)

    #Now we crop the image
    Cropped_Resized = Resized.crop(Cropping_Box)

    #We can now start the second step - the process of splitting the image into segments.
    #This will be a list where we store our segments
    #We initialize every segment as a 'NoneType' to not give it any strict
    #vallues before the correct ones are provided.
    Segments = []

    #Let's start a loop for the amount of horizontal segments we have
    for Horizontal in range(Horizontal_Resolution):

        #Now for the amount of segments we have vertically
        Segments.append([])
        for Vertical in range(Optimal_Vertical_Squares):

            #Now we can set a box parameter for the current segment we are 'Extracting'
            Left = Horizontal*Preferred_Segment_Resolution
            Top = Vertical*Preferred_Segment_Resolution
            Right = (Horizontal+1)*Preferred_Segment_Resolution
            Bottom = (Vertical+1)*Preferred_Segment_Resolution
            Segment_Box = (Left, Top, Right, Bottom)

            #Now we crop our the segment
            Segment = Cropped_Resized.crop(Segment_Box)

            #And sent it to the correct place in our 'Segments' list
            Segments[Horizontal].append(Segment)
            Segment = None

    #Now we have all the segments and so can return them
    return Segments


"""""
This function calculates the average RGB values for all the images in a specific folder to later use with a function
which will utilise that data for choosing the best suiting image for each segment. The calculated averages will be saved
in the same folder in a form of a .json file.
"""""
def Get_Folder_Averages(Directory):

    print("Getting Average RGB values for Images")

    #We first get the list of all th files in the folder ('*' is added as it points to all files )
    Files = glob.glob(Directory+'*')

    #We can now create a dictionary that will store all of our averages
    Averages = {}

    #Net step is to iterate through every file in the list that we have obtained
    for File_ in tqdm(Files):

        #Just to be sure it is an image
        if(File_.endswith('.png')):

            #Load the file as an 'Image' object
            Image_ = Image.open(File_)

            #Get the average
            RGB_Average = Calculate_Averages(Image_)

            #Now for the 'name' of the entry under which we will store the averages we have to get the id of the image.
            #The id is the name of the image, but to extract it we need to remove the rest of the path
            No_Path = File_.removeprefix(Directory)
            No_Path_And_Filetype = No_Path.removesuffix('.png')

            #Now that we have the id of the image as a string ( just like we want it ), we can add it to the dictionary
            Averages[No_Path_And_Filetype] = RGB_Average

            #Due to a large amount of images being loaded, it is better to be safe and close the ones we finished working with
            Image_.close()

    #After the iteration, it is the time to save the dictionary as a json file. 
    #We can do that easier with the help of 'json' module.
    #Creating the path
    Json_File_Path = Directory + 'Image_Averages.json'

    #Opening the file
    with open(Json_File_Path, 'w') as Write_File:

        #Dump the json data
        json.dump(Averages, Write_File)
    
    #We do not need to close anything because we used 'with' and not just 'open'.
    #After everything that goes into the indented area of the 'with' statement is comlete,
    #the file closes automatically
    #We can now just return 0 as a way of saying that the function comleted without errors
    return 0


"""""
A simple version of the Compare_Find class that only relies on the average RGB value
of the segment. This makes the code run significantly faster while not creating such 
detailed and varied collage parts.
"""""
class Simple_Compare_Find():

    """""
    Class initializer function
    """""
    def __init__(self, dir):

        #Set our Image directory
        self.dir = dir

        #Load the json file as that can sometimes get pretty heavy and constant load / unload would be inefficient
        #We also utilise Try Except here to ensure that the file is indeed there and if it is not, make it.
        try:
            #If the file is there it just opens like normal
            with(open(dir+"Image_Averages.json")) as Read_File:
                self.json = json.load(Read_File)
        except:
            #If it is not, we create one and then open it
            Get_Folder_Averages(dir)
            with(open(dir+"Image_Averages.json")) as Read_File:
                self.json = json.load(Read_File)


    """""
    Main function for the generation of a collage
    """""
    def Make_Collage(self, Image_, Output_Dir,Name,Horizontal_Resolution, Sub_Image_Resolution, Sub_Image_Downscale_Factor = 1):

        #Segments the image with one of our previously-written functions
        self.Segments = Segment_Image(Image_, Horizontal_Resolution)

        #Setting the directions to the file that woulds store all the Image IDs.
        self.Sauce_File = Output_Dir + Name +"_Sauce.txt"

        #A fancy way to initialize a list with set size. All that is important here is that
        #len(self.Segments[0]) is the vertical size and len(self.Segments) is the horizontal size
        self.Images_For_Segments = [[0] * len(self.Segments[0]) for i in range(len(self.Segments))]

        #Iterating through all of the segments of the image and matching them with RGB averages in our json
        print('Calculating Segments...')
        for Column in tqdm(range(len(self.Segments))):
            for Segment in range(len(self.Segments[0])):

                #Starting the calculation thread for a single segment with all the appropriate parameters
                threading.Thread(target=self.Find_Match, args=(Column, Segment, self.dir, Sub_Image_Downscale_Factor)).start()

                #While we are at the thread limit ( It is a constant 8 as I found that works well on most devices ), 
                #we wait for 1/100 of a second. This wait is needed rather than a 'pass' to reduce CPU usage from looping.
                while(threading.active_count() > 8):
                    time.sleep(0.01)

        #Small timeout between the two calculations to be sure all the threads are finished 
        #and all the images are saved properly
        print('Segment Calculation Complete. Starting Collage Generation...')
        time.sleep(3)

        #We can now start making the actual collage!
        #For that, the first step is to create a new, blank Image of matching size. The calculations
        #of sizes on this line might seem long and bulky but really they just multiple the adjusted
        #image resolution with how many segments the original was split into vertically and horizontally respectively
        Collage = Image.new('RGB',(math.floor(Sub_Image_Resolution*Sub_Image_Downscale_Factor)*len(self.Segments), math.floor(Sub_Image_Resolution*Sub_Image_Downscale_Factor)*len(self.Segments[0])))

        #Now, time to iterate through our Images yet another time.
        for Column in tqdm(range(len(self.Images_For_Segments))):
            for Segment in range(len(self.Images_For_Segments[0])):

                #Paste the image that replaces a segment into its corresponding position.
                #Again this code looks bulky but it just calculates and adjusts coordinates.
                Collage.paste(self.Images_For_Segments[Column][Segment], (Column*math.floor(Sub_Image_Resolution*Sub_Image_Downscale_Factor), Segment*math.floor(Sub_Image_Resolution*Sub_Image_Downscale_Factor)))

        #Finally, time to save our collage and return '0' - Mission Accomplished.
        Collage.save(Output_Dir+'Collagee_'+Name+'.png')
        return 0


    """""
    An internal function made for the Make_Collage function.
    This one finds an image that best matches the given segment's color.
    """""
    def Find_Match(self, x, y, Image_Folder, Sub_Image_Scaling_Factor):
        
        #Get the segment we will be comparing to
        Segment = self.Segments[x][y]

        #Load the RGB averages dictionary into the function
        Averages = self.json

        #Calculates average RGB value for our segment. Soon we will be comparing other values to
        #this one so it is especcially impotant.
        Segment_Average = Calculate_Averages(Segment)

        #Setting some basic variables for the upcoming search. These are basically
        #the best value and the position of the best value. it does not matter what 
        #best difference starts out as, as long as it is large enough.
        Best_Distance = 255
        Best_ID = None

        #Now iterating through all the images' average RGB values
        for Image_ in Averages:
            Item = Averages[Image_]

            #To get an understanding of good the match is for this specific image, we take the distance.
            #To understand this better, consider that RGB suddenly turns into XYZ in 3-dimensional space.
            #The more similar the colors are, the closer they would be when converted to coordinates.
            Distance = math.dist(Item, Segment_Average)

            #As such, the best value for distance is the lowest value and that is exactly what we check for.
            if(Distance < Best_Distance):
                Best_Distance = Distance
                Best_ID = Image_

        #Writing Image ID to the Sauce file
        with open(self.Sauce_File, "a") as Sauce:
            Sauce.write("https://www.e621.net/posts/"+Best_ID+"\n")

        #We can now load the image with the id which was found to be the best match.
        im = Image.open(Image_Folder+Best_ID+".png")

        #Resize the image to match extra scaling instructions provided
        im = im.resize((math.floor(im.size[0]*Sub_Image_Scaling_Factor), math.floor(im.size[1]*Sub_Image_Scaling_Factor)))

        #Now, this is something weird that we do here. For some reason, leaving normal open Image objects
        #can cause PIL to overflow when too many are open. This can though, for reasons unknown to me,
        #be simply avoided by making a deepcopy of the object. This is exactly like the object but now PIL
        #is more obedient. Amusing.
        self.Images_For_Segments[x][y] = copy.deepcopy(im)

        #Finally close the image after taking copy of it, again not to overflow PIL
        im.close()


#Finally we start our main function
if(__name__ == '__main__'):

    #Load The Image that we want to turn into a collage
    Image_ = Image.open('C:\\PATH\\TO\\YOUR\\IMAGE.png')

    #Initialise the class with our image path
    Collage_Generator = Simple_Compare_Find('C:\\PATH\\TO\\YOUR\\FOLDER\\WITH\\IMAGES\\')

    #This is the folder where the collage and file with sauce will go
    Output_Folder = "C:\\PATH\\TO\\YOUR\\OUTPUT\\FOLDER\\"

    #This is the name that the collage filename will include
    Name = "Collage"

    #This is the width that the Collage will possess measured in images
    Width = 64

    #It is important to set this to the side length of your Sub-Images in the folder
    Sub_Image_Res = 64

    #Relative resolution to that of what is would be with no scaling. Values from 0 to 1 decrease the resolution
    #While values above 1 increase it though they do not provide extra quality. This is only really created to set
    #To values like 0.5 to create lighter images that you can actually post to social networks.
    Scaling_Factor = 1

    #Finally starting the generation
    Collage_Generator.Make_Collage(Image_, Output_Folder,Name, Width, Sub_Image_Res, Scaling_Factor)
