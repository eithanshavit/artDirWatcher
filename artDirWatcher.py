#!/usr/bin/env python
import sys
import time
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import os
import argparse

# Some globals (yes, I know...)
outputFileName = ""

# Event handlers for watchdog
class EventHandler(FileSystemEventHandler):
    def __init__(self, inputRootDir, outputRootDir, subDir):
      super(EventHandler, self).__init__()
      self.outputDir = os.path.join(outputRootDir, subDir)
      self.inputDir = os.path.join(inputRootDir, subDir)

      if not os.path.exists(self.inputDir):
          os.makedirs(self.inputDir)
      if not os.path.exists(self.outputDir):
          os.makedirs(self.outputDir)

    def on_created(self, event):
        inputFile = event.src_path
        print "processing: ", inputFile
        _, inputFileExt = os.path.splitext(inputFile)
        # Traverse output dir and find latest file
        filesInDir = [f for f in os.listdir(self.outputDir) if os.path.isfile(os.path.join(self.outputDir, f))]
        latestFileNumber = 0
        for f in filesInDir:
          currentFilePath = os.path.join(self.outputDir, f)
          nakedFile, _ = os.path.splitext(currentFilePath)
          try:
            fileNumber = int(nakedFile.split('-')[1])
          except:
            # Don't deal with files that don't conform to format
            continue
          if fileNumber > latestFileNumber:
            latestFileNumber = fileNumber
        # If none found, name as first output file, otherwise increment
        latestFileNumber = latestFileNumber + 1 if latestFileNumber else 1
        outputFile = os.path.join(self.outputDir, "%s-%03d%s" % (outputFileName, latestFileNumber, inputFileExt))

        # Finally move file to output dir
        print "moving to:  ", outputFile
        print "-----"
        shutil.move(inputFile, outputFile)

# Main
def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('indir', help="Input root directory", type=str)
    parser.add_argument('outdir', help="Output root directory", type=str)
    parser.add_argument('name', help="Output base file name", type=str)

    # Parse args
    args = parser.parse_args(arguments)
    global outputFileName
    outputFileName = args.name

    inputRootDir = args.indir
    outputRootDir = args.outdir

    # Validate args
    if not os.path.isdir(outputRootDir):
      print "Output directory doesn't exist"
      return 1
    if not os.path.isdir(inputRootDir):
      print "Input directory doesn't exist"
      return 1

    # Setup watchdog
    observer = Observer()
    thumbObserver = EventHandler(inputRootDir, outputRootDir, "thumb")
    fullObserver = EventHandler(inputRootDir, outputRootDir, "full")
    observer.schedule(thumbObserver, thumbObserver.inputDir, recursive=True)
    observer.schedule(fullObserver, fullObserver.inputDir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
