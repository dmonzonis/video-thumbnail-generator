#!/bin/bashç
# Process all videos in the current directory
FILES="*.mp4 *.wmv *.flv *.mkv *.webm"
count=$(ls -1q ${FILES} 2>/dev/null | wc -l)
echo "Found $count files to process"

for f in $FILES
do
    [ -e "$f" ] && echo "Processing file $f..." && python generator.py "$f"
done
