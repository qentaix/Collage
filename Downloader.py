#Importing all the required libraries
import requests
from requests.auth import HTTPBasicAuth
import threading
from PIL import Image
import io
import time



im = Image.open('C:\\Users\\qenta\\61dc309f05025d8df0a6bb33e96d6b64.png')

"""""
This function takes in a PIL 'Image' object and a resolution for the transformation.
It then first calculates whether the Image should be cut off at the sides or it top and bottom
to be turned into a square. It then cuts off the parts it has calculated and resizes the acquired
square to the resolution specified in the function call
"""""
def Make_Square(image, Resolution):
    #Gets the dimensions and sets them to appropriate variables
    Dimensions = image.size
    Width = Dimensions[0]
    Height = Dimensions[1]
    Box = (0,0,Width,Height)
    if(Width > Height):
        #If we need to crop horizontally we set the 'Box' to cut off half the difference at both sides
        Dimension_Difference = Width - Height
        Half_Dimension_Difference = Dimension_Difference / 2
        Box = (Half_Dimension_Difference, 0, Width - Half_Dimension_Difference, Height)
    elif(Height > Width):
        #If we need to crop vertically we set the 'Box' to cut off half the difference at top and bottom
        Dimension_Difference = Height - Width
        Half_Dimension_Difference = Dimension_Difference / 2
        Box = (0, Half_Dimension_Difference, Width, Height - Half_Dimension_Difference)
    #Crop the Image with our 'Box' Coordinates
    Cropped_Image = image.crop(Box)
    #Resize our, now square, image to the set resolution
    Resize_Dimensions = (Resolution, Resolution)
    Resized_Cropped_Image = Cropped_Image.resize(Resize_Dimensions)
    return Resized_Cropped_Image



"""""
Function made to retrieve a json ( similar to Python dictionary ) from the e621 API with stored
data for 320 different posts. We take in a Page parameter so we can get different posts with the same tags.
"""""
def Retrieve_Batch_Json(Tag_List, Page, Auth, Headers):
    #Setting the post limit in each batch to 320 for best efficiency as that is the most e621 API allows us.
    #You can set this to anything you want to but be aware that lower values CAN cause a dip in retrieval speed.
    Limit = '320'
    #Now we combine all the tags into one string
    Tag_String = ''
    for Tag in Tag_List:
        Tag_String += Tag + '+'
    #We can now combine all of our parameters to form an e621 URL for our batch
    Url = 'https://e621.net/posts.json?limit=' + Limit + '&page=' + str(Page) + '&tags=' + Tag_String
    #We can now send a request to the URL we have just built to retrieve the wanted json.
    #The auth parameter is taken from a parameter passed to this function - a 'HTTPBasicAuth' auth value.
    Json = requests.get(Url, auth=Auth, headers=Headers).json()
    return Json



"""""
Sub-function of the next function. This one is made to be used in threads for extra speed and efficiency.
"""""
def Get_Save_Image(Url, Save_Location, Resolution):
    #Get the Image
    Image_Bytes = requests.get(Url).content
    #Load image from bytes with the use of BytesIO buffer
    Image_ = Image.open(io.BytesIO(Image_Bytes))
    #Transform the Image with one of our other functions
    Image_Transformed = Make_Square(Image_, Resolution)
    #Saving the Image
    Image_Transformed.save(Save_Location)
    print('Downloaded '+Save_Location)



"""""
Function for retrieving all of the Images from a list of posts in a single batch / json file / page of content
"""""
def Save_Post_Images(Tag_List, Page, Auth, Headers, Image_Directory, Resolution):
    #Step number one is to get out batch json / dictionary for given parameters
    Json = Retrieve_Batch_Json(Tag_List, Page, Auth, Headers)
    #For every post...
    for Post in Json['posts']:
        #We take the url from the 'sample' quality of the post as we
        #do not really need high quality in individual images.
        Url = Post['sample']['url']
        #We now make a path / file location for the image using the id of the post as a filename.
        Save_Location = Image_Directory + str(Post['id'])+'.png'
        #We can now start a 'Get_Save_Image' function as a Thread in order to maximize general retrieval speed
        threading.Thread(target=Get_Save_Image, args=(Url, Save_Location, Resolution)).start()
        #Start a waiting loop until we have a free spot for a new thread
        while(threading.active_count() > 8):
            time.sleep(0.1)

if(__name__ == '__main__'):

    Username = 'YOUR_USERNAME' #Enter your username in this string
    API_Key = 'YOUR_API_KEY' #Enter your API key here ( can be obtained at e621.net > Account > API access )
    Resolution = 64 #Enter the resolution to save the images with. Sets value for both width and heing (Duh, its a square -_-)
    #Enter the tags you would like to download the posts with here. It is important to exclude tags
    # 'young' , 'child' and 'cub' if you plan to share the output collage somewhere. Any images with these
    #tags fall into the category which can and will likely get you banned from wherever you post it.
    Tag_List = ['type:png', 'order:score', '-young', '-child', '-cub'] 
    #Set the auth that will be passed to e621 API with the credentials you entered earlier.
    Auth = HTTPBasicAuth(Username, API_Key)
    #The ones below are headers - they let the API know some minimal info of the Client that requests the content
    #While I recommend to change the value of 'User-Agent' to your own, you could theoretically keep it the same,
    #likely without much, if any, consequences or impact on the program's performance.
    Headers = {'User-Agent': 'Collage_Generator'}
    #This variable sets the value for how many pages / batches of posts the programm will download.
    #Remember that whatever you set this value to, the amount of posts downloaded will be exactly, or close to, 320x of that.
    #For making a collage you also have to considerr that a larger amount of Pages will get you better looking results while
    #taking considerably longer to process and generate the output image.
    Pages = 300
    #Here you will have to specify where you would like the program to dump all of the Image files.
    #Creating a new separate directory for this is pretty much a requirement as it will get flooded with thousands of images.
    #Note: recommended to use '\\' in the path if you are on Windows. This is not a requirement but I have my own story
    #of working with paths and relative paths and it ended up with me preferring this.
    Save_Path = 'C:\\Path\\To\\Your\\Folder\\'
    #Now we can start the loop that downloads all the pages from page 1 to page 'Pages'.
    #Don't worry about the range saying 'Pages+1', it is related to us starting from 1 rather than 0.
    for Page in range(1, Pages+1):
        Save_Post_Images(Tag_List, Page, Auth, Headers, Save_Path, Resolution)