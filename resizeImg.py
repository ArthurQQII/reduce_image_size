import math
from PIL import Image
import os
import sys
import getopt

shortOpt = "d:s:f:w:h:p:"

longOpt = ["src_directory=", "des_directory=",
           "file_name=", "width=", "height=", "percentage="]

# error code
DIRESCTORY_OR_FILE = 2
DIRESCTORY_OE_FILE_NOT_EXIST = 3
REDUCE_RULE_NOT_DEFINE = 4
PERCENTAGE_OR_WIDTH_HEIGHT = 5
IMAGE_REDUCE_FAIL = 6
FILE_OR_DIRECTORY = 7


def error_quit(errorCode=1, imageName='', exit=True):
    errorMsg = ''
    match errorCode:
        case 2:
            errorMsg = "You cannot set source directory and file at the same time"
        case 3:
            errorMsg = "The source directory or the file is not exist"
        case 4:
            errorMsg = "The images reduce rule is not "
        case 5:
            errorMsg = "Percentage and width/height should not been defined at the same time"
        case 6:
            errorMsg = "Image reduce size fail: " + imageName
        case _:
            errorMsg = "Something wrong"

    sys.stderr.writelines(errorMsg + '\n')
    if exit:
        sys.exit(errorCode)


def log_result(finished=0, total=1, done=False):
    return 
    # if done:
    #     sys.stdout.write("\nAll done\n")
    # else:
    #     sys.stdout.write("Processed [%.2f%%]\r" %
    #                      (float(finished/total) * 100))
    # sys.stdout.flush()


def init_image_reduce():
    imageReduce = Image_reduce()
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, shortOpt, longOpt)
    except:
        error_quit()

    for opt, arg in opts:
        if opt in ['-s', '--src_directory']:
            imageReduce.sourceDirectory = arg
        elif opt in ['-d', '--des_directory']:
            imageReduce.destinationDirectory = arg
        elif opt in ['-f', '--file_name']:
            imageReduce.fileName = arg
        elif opt in ['-w', '--width']:
            imageReduce.width = int(arg)
        elif opt in ['-h', '--height']:
            imageReduce.height = int(arg)
        elif opt in ['-p', '--percentage']:
            imageReduce.percentage = float(arg) / 100
    return imageReduce


class Image_reduce:

    def __init__(self, sourceDirectory=None, destinationDirectory=None, fileName=None, width=0, height=0, percentage=0):
        self.sourceDirectory = sourceDirectory
        self.destinationDirectory = destinationDirectory
        self.fileName = fileName
        self.width = width
        self.height = height
        self.percentage = percentage

    def check_valid(self):
        if self.sourceDirectory != None and self.fileName != None:
            error_quit(errorCode=DIRESCTORY_OR_FILE)

        if self.sourceDirectory == None and self.fileName == None:
            error_quit(errorCode=DIRESCTORY_OR_FILE)

        if self.width == 0 and self.height == 0 and self.percentage == 0:
            error_quit(errorCode=REDUCE_RULE_NOT_DEFINE)

        if (self.width > 0 or self.height > 0) and self.percentage > 0:
            error_quit(errorCode=PERCENTAGE_OR_WIDTH_HEIGHT)

        if self.sourceDirectory != None:
            if not os.path.isdir(self.sourceDirectory):
                error_quit(errorCode=DIRESCTORY_OE_FILE_NOT_EXIST)

        if self.fileName != None:
            if not os.path.isfile(self.fileName):
                error_quit(errorCode=DIRESCTORY_OE_FILE_NOT_EXIST)

        if self.destinationDirectory is None:
            self.destinationDirectory = os.path.curdir

    def reduce_size(self, file):
        if os.path.isfile(file):
            img = Image.open(file)
            (wSize, hSize) = self.process_reduce_rule(img)
            img = img.resize((wSize, hSize), Image.ANTIALIAS)

            img.save(os.path.join(
                self.destinationDirectory, os.path.basename(file)))
            return True
        return False

    def process_reduce_rule(self, image):
        if self.percentage == 0:
            if self.width != 0:
                wSize = self.width
                if self.height != 0:
                    hSize = self.height
                else:
                    wpercent = (wSize / float(image.size[0]))
                    hSize = int((float(image.size[1]) * float(wpercent)))
            else:
                hSize = self.height
                if self.width != 0:
                    wSize = self.width
                else:
                    hpercent = (hSize / float(image.size[1]))
                    wSize = int((float(image.size[0]) * float(hpercent)))
        else:
            wSize = int((float(image.size[0]) * float(self.percentage)))
            hSize = int((float(image.size[1]) * float(self.percentage)))
        return (wSize, hSize)

    def run(self):
        count = 0
        if self.fileName is not None:
            total = 1
            if not self.reduce_size(self.fileName):
                error_quit(errorCode=IMAGE_REDUCE_FAIL,
                           imageName=self.fileName, exit=False)
            else:
                count = 1
            log_result(finished=count, total=total)

        if self.sourceDirectory is not None:
            fileList = os.listdir(self.sourceDirectory)
            total = len(fileList)
            for filename in fileList:
                file = os.path.join(self.sourceDirectory, filename)
                if self.reduce_size(file):
                    count += 1
                else:
                    error_quit(errorCode=IMAGE_REDUCE_FAIL,
                               imageName=self.fileName, exit=False)

                log_result(finished=count, total=total)

        log_result(finished=count, total=total, done=True)

    def __str__(self):
        result = ''
        for attribute, value in self.__dict__.items():
            if value == None:
                value = "None"
            result += attribute + ": " + str(value) + '\n'
        return result


def main():
    imageReduce = init_image_reduce()

    imageReduce.check_valid()

    imageReduce.run()

    exit(0)


if __name__ == "__main__":
    main()
