#!/usr/bin/env python

import sys,os,math,numpy,cv
#from PIL import Image,ImageDraw

def getR(part1X,part1Y,part2X,part2Y):
  #get rotation degree
  r = 0;
  if (part1X != part2X):
    r = -1*math.atan((part1Y-part2Y)/(part1X-part2X));

  return r;

def getRRefined(part1X,part1Y,part2X,part2Y,thresh,imageName):
  if (part1X != part2X):
    print("ERROR: Should not be here... ("+imageName+")");
    sys.exit();

  print imageName;

  if (math.fabs(part2Y - part1Y) <= thresh):
    r=0;
  elif (part1Y > part2Y):
    r = (math.pi/2.0);
  elif (part1Y < part2Y):
    r = -1*(math.pi/2.0);
    
  return r;


def warpPointX(pointX,pointY,rotMat):
  warpedPointX = pointX*rotMat[0,0] + pointY*rotMat[0,1] + rotMat[0,2];
  retVal = 0;
  #use floor and ceil to make sure there is enough room in the new image
  if warpedPointX < 0:
    retVal = math.floor(warpedPointX);
  else:
    retVal = math.ceil(warpedPointX);
  return int(retVal);

def warpPointY(pointX,pointY,rotMat):
  warpedPointY = pointX*rotMat[1,0] + pointY*rotMat[1,1] + rotMat[1,2];
  retVal = 0;
  if warpedPointY < 0:
    retVal = math.floor(warpedPointY);
  else:
    retVal = math.ceil(warpedPointY);
  return int(retVal);


baseDir = "/work/cv2/hanselmann/CUB200-2011/";
originalPath = baseDir+"images/original/";
outputPath = str(sys.argv[1]);
addPixel = float(sys.argv[2]);
ratio = float(sys.argv[3]);
finalSize = str(sys.argv[4]);
rotateArg = str(sys.argv[5]);
flipArg = str(sys.argv[6]);

#interpolation method for rotation and resizing, options: NN, LINEAR, AREA, CUBIC
interpolation_FLAG = cv.CV_INTER_LINEAR;

finalSizeSplit = finalSize.split("x");
keepAspectRatio = False;
if (len(finalSizeSplit) == 2):
  finalSizeX = finalSizeSplit[0];
  finalSizeY = finalSizeSplit[1];
else:
  maxSize = finalSizeSplit[0];
  keepAspectRatio = True;

prefix = "lists/";
if outputPath.split("/")[-1] != "":
  prefix = prefix+outputPath.split("/")[-1];
else:
  prefix = prefix+outputPath.split("/")[-2];
  
partLocsList = open(baseDir+"parts/part_locs.txt","r");
imageList = open(baseDir+"images.txt","r");

noRotationList = open(baseDir+prefix+"_noRotation.txt","w");
unclearRotationList = open(baseDir+prefix+"_unclearRotation.txt","w");
smallBBList = open(baseDir+prefix+"_smallBB.txt","w");
finalBBList = open(baseDir+prefix+"_finalBB.txt","w");
finalPartLocsList = open(baseDir+prefix+"_finalPartLocs.txt","w");
partsCountList = open(baseDir+prefix+"_partsCount.txt","w");
notVisibleList = open(baseDir+prefix+"_notVisible.txt","w");

classesToUse = ["all"];
#classesToUse = ["151.Black_capped_Vireo", "152.Blue_headed_Vireo", \
#               "153.Philadelphia_Vireo", "154.Red_eyed_Vireo", \
#               "155.Warbling_Vireo", "156.White_eyed_Vireo", \
#               "157.Yellow_throated_Vireo", "187.American_Three_toed_Woodpecker", \
#               "188.Pileated_Woodpecker", "189.Red_bellied_Woodpecker", \
#               "190.Red_cockaded_Woodpecker", "191.Red_headed_Woodpecker", \
#               "192.Downy_Woodpecker", "036.Northern_Flicker"]
#classesToUse = ["046.Gadwall"]
#classesToUse = ["002.Laysan_Albatross","003.Sooty_Albatross","064.Ring_billed_Gull","075.Green_Jay","076.Dark_eyed_Junco","143.Caspian_Tern","146.Forsters_Tern","159.Black_and_white_Warbler","166.Golden_winged_Warbler"]

partLocsListLines = partLocsList.readlines();
partsToUse = ["2","5","6","7","11","15"];
partsDict = {};
partsSumDict = {};

for line in partLocsListLines:
  words = line.split();
  imageNumber = words[0];
  if imageNumber not in partsDict:
    partsDict[imageNumber] = {};
  if imageNumber not in partsSumDict:
    partsSumDict[imageNumber] = [0.0,0.0]; 

  if (words[4] == "0"):
    continue;
  
  if words[1] in partsToUse:
    partsDict[imageNumber][words[1]] = [float(words[2]),float(words[3])];
    partsSumDict[imageNumber][0] += float(words[2]);
    partsSumDict[imageNumber][1] += float(words[3]);

imageListLines = imageList.readlines();


for line in imageListLines:
  words = line.split();
  className = words[1].split("/")[0];
  if ( (not className in classesToUse) and (not "all" in classesToUse) ):
    continue;  
  imageNumber = words[0];
  imageName = words[1];
  #print imageName
  #if not imageName == "076.Dark_eyed_Junco/Dark_Eyed_Junco_0114_67964.jpg":
  #  continue;

  if not os.path.exists(outputPath+className):
    print("creating: "+outputPath+className);
    os.makedirs(outputPath+className);

  image = cv.LoadImageM(originalPath+imageName);
  imageWidth,imageHeight = cv.GetSize(image);
  partsCount = len(partsDict[imageNumber]);
  partsCountList.write(str(imageNumber)+" "+imageName+" "+str(partsCount)+"\n");

  #if none of the required parts are visible => torso not visible
  if (partsCount < 1):
    notVisibleList.write(str(imageNumber)+" "+imageName+"\n");
    os.system("cp "+originalPath+imageName+" "+outputPath+imageName);
    continue;
  
  #centroid part locations
  centerX = partsSumDict[imageNumber][0]/float(partsCount);
  centerY = partsSumDict[imageNumber][1]/float(partsCount);

  flip = False;
  rotate = False;
  
  #find the rotation rotation angle r and whether or not to flip
  r = 0;

  #frontal/back view => no flipping, rotate according to wings
  if ("7" in partsDict[imageNumber] and "11" in partsDict[imageNumber]):
    leftEyeX = partsDict[imageNumber]["7"][0]; # left of the bird, not the image
    leftEyeY = partsDict[imageNumber]["7"][1];
    rightEyeX = partsDict[imageNumber]["11"][0];
    rightEyeY = partsDict[imageNumber]["11"][1];

    r = getR(leftEyeX,leftEyeY,rightEyeX,rightEyeY);
    if leftEyeX == rightEyeX:
      print("WARNING: Unclear rotation for image "+imageName+". Check if this is what you want...");
      unclearRotationList.write(str(imageNumber)+" "+imageName+"\n");
      r = getRRefined(leftEyeX,leftEyeY,rightEyeX,rightEyeY,2,imageName);

    rotate = True;
      
  #side view
  elif ("7" in partsDict[imageNumber] and "2" in partsDict[imageNumber]):
    leftEyeX = partsDict[imageNumber]["7"][0]; 
    leftEyeY = partsDict[imageNumber]["7"][1];
    beakX = partsDict[imageNumber]["2"][0]; 
    beakY = partsDict[imageNumber]["2"][1];
    
    r = getR(leftEyeX,leftEyeY,beakX,beakY);
    if leftEyeX == beakX:
      print("WARNING: Unclear rotation for image "+imageName+". Check if this is what you want...");
      unclearRotationList.write(str(imageNumber)+" "+imageName+"\n");
      r = getRRefined(beakX,beakY,leftEyeX,leftEyeY,2,imageName);

    rotate = True;

  #other side view, flip to match first side view
  elif ("11" in partsDict[imageNumber] and "2" in partsDict[imageNumber]):
    rightEyeX = partsDict[imageNumber]["11"][0]; 
    rightEyeY = partsDict[imageNumber]["11"][1];
    beakX = partsDict[imageNumber]["2"][0]; 
    beakY = partsDict[imageNumber]["2"][1];
    
    r = getR(beakX,beakY,rightEyeX,rightEyeY);
    if rightEyeX == beakX:
      print("WARNING: Unclear rotation for image "+imageName+". Check if this is what you want...");
      unclearRotationList.write(str(imageNumber)+" "+imageName+"\n");
      r = getRRefined(rightEyeX,rightEyeY,beakX,beakY,2,imageName);

    rotate = True;
    flip = True;
    
  #don't know the view, flip in case it is side view  
  elif ("11" in partsDict[imageNumber]):
    flip = True;


  #bounding box variables
  x=-1; y=-1; w=-1; h=-1;
  bb = [100000,100000,0,0];
  
  #skip rotation, if arg is given
  if (rotateArg != "rotate"):
    rotate = False;

  # if we have more than one part, do the transformation
  if (rotate):

    #OpenCV needs rotation angle in degrees
    r = math.degrees(r);
    #get rotation matrix
    rotMat = cv.CreateMat(2,3,cv.CV_32FC1);
    cv.GetRotationMatrix2D((centerX,centerY),-r,1.0,rotMat);

    #get maximal Dimension of imageRotated, such that the rotated image fully fits
    warpedCornersX = [warpPointX(0,0,rotMat), warpPointX(0,imageHeight-1,rotMat), warpPointX(imageWidth-1,0,rotMat), warpPointX(imageWidth-1,imageHeight-1,rotMat)];
    warpedCornersY = [warpPointY(0,0,rotMat), warpPointY(0,imageHeight-1,rotMat), warpPointY(imageWidth-1,0,rotMat), warpPointY(imageWidth-1,imageHeight-1,rotMat)];
    minMaxCorners = [max(warpedCornersX),min(warpedCornersX),max(warpedCornersY),min(warpedCornersY)];

    imageRotatedWidth = minMaxCorners[0] - minMaxCorners[1] + 1;
    imageRotatedHeight = minMaxCorners[2] - minMaxCorners[3] + 1;

    #adjust the shift of the rotation
    rotMat[0,2] -= minMaxCorners[1];
    rotMat[1,2] -= minMaxCorners[3];

    #create new image to save the rotated image (rows = height, cols = width)
    imageRotated = cv.CreateMat(imageRotatedHeight,imageRotatedWidth,image.type);
    
    #perform the rotation:
    cv.WarpAffine(image,imageRotated,rotMat,flags=interpolation_FLAG+cv.CV_WARP_FILL_OUTLIERS,fillval=(255,255,255));

    #compute the new warped bounding box
    bb = [100000,100000,0,0];
    for part in partsDict[imageNumber]:
      if part in partsToUse:
        currentPointX = partsDict[imageNumber][part][0];
        currentPointY = partsDict[imageNumber][part][1];
        warpedPointX = currentPointX*rotMat[0,0] + currentPointY*rotMat[0,1] + rotMat[0,2];
        warpedPointY = currentPointX*rotMat[1,0] + currentPointY*rotMat[1,1] + rotMat[1,2];

        finalPartLocsList.write(str(imageNumber)+" "+part+" "+str(warpedPointX)+" "+str(warpedPointY)+" 1\n");
                
        bb[0] = min(bb[0],warpedPointX);
        bb[1] = min(bb[1],warpedPointY);
        bb[2] = max(bb[2],warpedPointX);
        bb[3] = max(bb[3],warpedPointY);
  

  else:
    imageRotatedWidth = imageWidth;
    imageRotatedHeight = imageHeight;
    
    bb = [100000,100000,0,0];
    for part in partsDict[imageNumber]:
      if part in partsToUse:
        currentPointX = partsDict[imageNumber][part][0];
        currentPointY = partsDict[imageNumber][part][1];

        finalPartLocsList.write(str(imageNumber)+" "+part+" "+str(currentPointX)+" "+str(currentPointY)+" 1\n");
                
        bb[0] = min(bb[0],currentPointX);
        bb[1] = min(bb[1],currentPointY);
        bb[2] = max(bb[2],currentPointX);
        bb[3] = max(bb[3],currentPointY);


  if (bb[0] < 0 or bb[1] < 0 or bb[2] > imageRotatedWidth-1 or bb[3] > imageRotatedHeight-1):
    print("WARNING: Warping out of bounds "+imageName);
    #sys.exit();

  #cv.SaveImage(outputPath+imageName,imageRotated);

  bb[0] = max(bb[0],0);
  bb[1] = max(bb[1],0);
  bb[2] = min(bb[2],imageRotatedWidth-1); 
  bb[3] = min(bb[3],imageRotatedHeight-1);
      
  x = bb[0];
  y = bb[1];
  w = bb[2] - bb[0];
  h = bb[3] - bb[1]; 

    
  #now do the final processing (cropping etc...)
  addPixelFactor = 1;
  #if we only have one part, add more, otherwise the patch would very small
  if (partsCount == 1):    
    addPixelFactor = 4;
    w=1;
    h=1;
  
  x = x - addPixel*addPixelFactor*w;
  y = y - addPixel*addPixelFactor*h;
  

  w = w + 2*addPixel*addPixelFactor*w;
  h = h + 2*addPixel*addPixelFactor*h;

  #make sure that the aspect ratio is not too low
  if (h < w/ratio):
    smallBBList.write(str(imageNumber)+" "+imageName+"\n");
    y = y - (w/ratio - h)/2.0;
    h = w/ratio;

  if (w < h/ratio):
    smallBBList.write(str(imageNumber)+" "+imageName+"\n");
    x = x - (h/ratio - w)/2.0;
    w = h/ratio;

  if x < 0:
    print("WARNING: After normalizing ratio the bounding box is outside the image borders... (shifted such that it fits):");
    print(imageName);
    x=0;
  if y < 0:
    print("WARNING: After normalizing ratio the bounding box is outside the image borders... (shifted such that it fits):");
    print(imageName);
    y=0;

  if (rotate):
    #print("convert -crop "+str(w)+"x"+str(h)+"+"+str(x)+"+"+str(y)+" "+outputPath+imageName+" "+outputPath+imageName);
    #print(str(int(y+0.5))+":"+str(int(y+h+0.5))+", "+str(int(x+0.5))+":"+str(int(x+w+0.5)));
    #print cv.GetSize(imageRotated);
    #print imageWidth,imageHeight
    imageCropped = imageRotated[int(y+0.5):int(y+h+0.5), int(x+0.5):int(x+w+0.5)];
  else:
    #print("convert -crop "+str(w)+"x"+str(h)+"+"+str(x)+"+"+str(y)+" "+originalPath+imageName+" "+outputPath+imageName);
    imageCropped = image[int(y+0.5):int(y+h+0.5), int(x+0.5):int(x+w+0.5)];
    noRotationList.write(str(imageNumber)+" "+imageName+"\n");
    
  finalBBList.write(str(imageNumber)+" "+imageName+" "+str(w)+"x"+str(h)+"+"+str(x)+"+"+str(y)+"\n");

  if (flip and flipArg == "flip"):
    #print("convert -flip "+outputPath+imageName+" "+outputPath+imageName);
    cv.Flip(imageCropped,None,1);

  #resize the image
  if (keepAspectRatio):
    resizeFactor = 1.0;
    if (w > h):
      resizeFactor = float(maxSize)/float(w);
    else:
      resizeFactor = float(maxSize)/float(h);
    
    newWidth = int(w*resizeFactor+0.5); # cols = width
    newHeight = int(h*resizeFactor+0.5); # rows = height
  else:
    newWidth = int(finalSizeX); # cols = width
    newHeight = int(finalSizeY); # rows = height
    
  imageResized = cv.CreateMat(newHeight,newWidth,image.type);
  cv.Resize(imageCropped,imageResized,interpolation=interpolation_FLAG);
  cv.SaveImage(outputPath+imageName,imageResized);

   
  
partLocsList.close();
imageList.close();
noRotationList.close();
unclearRotationList.close();
smallBBList.close();
finalBBList.close();
finalPartLocsList.close();
partsCountList.close();
